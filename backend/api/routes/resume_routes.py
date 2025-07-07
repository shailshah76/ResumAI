from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
from datetime import datetime
from pathlib import Path

from backend.models.schemas import (
    UploadResumeResponse,
    ExtractKeywordsRequest, ExtractKeywordsResponse,
    GenerateResumeRequest, GenerateResumeResponse, FileType,
    EnhancedAnalyzeJobRequest, EnhancedAnalyzeJobResponse
)
from backend.services.ai_service import AIServiceInterface, create_ai_service
from backend.services.file_service import FileService, create_file_service
from backend.services.document_service import create_document_service
from backend.core.exceptions import CustomException

router = APIRouter()

# Dependency injection for services
def get_ai_service() -> AIServiceInterface:
    return create_ai_service()

def get_file_service() -> FileService:
    return create_file_service()

def get_document_service():
    return create_document_service()

@router.post("/upload-resume", response_model=UploadResumeResponse)
async def upload_resume(
    file: Optional[UploadFile] = File(None),
    resume_text: Optional[str] = Form(None),
    job_description: Optional[str] = Form(None),
    ai_service: AIServiceInterface = Depends(get_ai_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Upload a resume for processing
    
    Accepts:
    - **file**: Resume file (PDF, DOCX, or TXT) via multipart/form-data
    - **resume_text**: Resume content as text via form field
    - **job_description**: Job description for context (optional)
    
    Returns file upload confirmation with unique file ID
    """
    try:
        file_id = None
        file_size = 0
        file_type = None
        filename = None
        
        if file:
            # Handle file upload
            file_content = await file.read()
            
            # Determine file type
            file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
            if file_extension == 'pdf':
                file_type = FileType.PDF
            elif file_extension == 'docx':
                file_type = FileType.DOCX
            elif file_extension == 'txt':
                file_type = FileType.TXT
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")
            
            # Use document service for saving (will convert PDFs to TXT)
            document_service = create_document_service()
            
            # Validate file
            document_service.validate_file(file_content, file.filename, file_type)
            
            # Save file (PDFs will be converted to TXT automatically)
            file_id, file_size = await document_service.save_file(file_content, file.filename, file_type)
            
            # Update filename if PDF was converted to TXT
            if file_type == FileType.PDF:
                filename = f"{Path(file.filename).stem}.txt"
            else:
                filename = file.filename
            
            print(f"Upload: File saved with ID: {file_id}, size: {file_size}")
            if file_type == FileType.PDF:
                print(f"Upload: PDF converted to TXT format")
            
        elif resume_text:
            # Handle text input
            if not resume_text.strip():
                raise HTTPException(status_code=400, detail="Resume text cannot be empty")
            
            # Convert text to bytes
            file_content = resume_text.encode('utf-8')
            file_type = FileType.TXT
            filename = f"resume_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # Save text as file using document service
            document_service = create_document_service()
            file_id, file_size = await document_service.save_file(file_content, filename, file_type)
            
        else:
            raise HTTPException(status_code=400, detail="Either file or resume_text must be provided")
        
        return UploadResumeResponse(
            file_id=file_id,
            filename=filename,
            file_type=file_type,
            upload_timestamp=datetime.utcnow(),
            file_size=file_size,
            message="Resume uploaded successfully",
            job_description=job_description
        )
        
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/analyze-job", response_model=EnhancedAnalyzeJobResponse)
async def analyze_job(
    request: EnhancedAnalyzeJobRequest,
    ai_service: AIServiceInterface = Depends(get_ai_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Enhanced job analysis that compares resume with job description
    
    This endpoint:
    1. Parses the resume (using Docling-like text extraction)
    2. Extracts keywords from both resume and job description
    3. Compares keywords and returns only the missing ones
    
    - **job_description**: The job description text to analyze
    - **resume_text**: Resume content as text (optional if file_id provided)
    - **file_id**: File ID of uploaded resume (optional if resume_text provided)
    - Returns detailed analysis with keyword comparison
    """
    try:
        # Generate unique analysis ID
        analysis_id = str(uuid.uuid4())
        
        # Get resume text
        resume_text = request.resume_text
        
        if not resume_text and request.file_id:
            # Get text content from uploaded file using document service
            document_service = create_document_service()
            resume_text = await document_service.get_text_content(request.file_id)
            
            if not resume_text:
                raise HTTPException(status_code=404, detail="File not found or could not extract text")
            
            print(f"Analysis: Retrieved text content from file {request.file_id}")
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="No resume content available")
        
        # Perform enhanced analysis
        analysis_result = await ai_service.enhanced_analyze_job(request.job_description, resume_text)
        
        # Extract keyword comparison data
        keyword_comparison = analysis_result.get("keyword_comparison", {})
        
        return EnhancedAnalyzeJobResponse(
            analysis_id=analysis_id,
            job_description=request.job_description,
            resume_content=resume_text,
            key_requirements=analysis_result.get("key_requirements", []),
            required_skills=analysis_result.get("required_skills", []),
            preferred_skills=analysis_result.get("preferred_skills", []),
            experience_level=analysis_result.get("experience_level", "Not specified"),
            industry=analysis_result.get("industry", "Not specified"),
            keyword_comparison={
                "job_keywords": keyword_comparison.get("job_keywords", []),
                "resume_keywords": keyword_comparison.get("resume_keywords", []),
                "missing_keywords": keyword_comparison.get("missing_keywords", []),
                "matching_keywords": keyword_comparison.get("matching_keywords", []),
                "keyword_scores": keyword_comparison.get("keyword_scores", {})
            },
            analysis_timestamp=datetime.utcnow()
        )
        
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced analysis failed: {str(e)}")

@router.post("/extract-keywords", response_model=ExtractKeywordsResponse)
async def extract_keywords(
    request: ExtractKeywordsRequest,
    ai_service: AIServiceInterface = Depends(get_ai_service)
):
    """
    Extract keywords from text with relevance scores
    
    - **text**: Text to extract keywords from
    - **max_keywords**: Maximum number of keywords to extract (default: 20)
    - Returns extracted keywords with relevance scores
    """
    try:
        # Generate unique extraction ID
        extraction_id = str(uuid.uuid4())
        
        # Extract keywords
        keywords_result = await ai_service.extract_keywords(request.text, request.max_keywords)
        
        keywords = keywords_result.get("keywords", [])
        scores = keywords_result.get("scores", {})
        
        return ExtractKeywordsResponse(
            extraction_id=extraction_id,
            original_text=request.text,
            keywords=keywords,
            keyword_scores=scores,
            total_keywords=len(keywords),
            extraction_timestamp=datetime.utcnow()
        )
        
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword extraction failed: {str(e)}")

@router.post("/generate-resume", response_model=GenerateResumeResponse)
async def generate_resume(
    request: GenerateResumeRequest,
    ai_service: AIServiceInterface = Depends(get_ai_service)
):
    """
    Generate a tailored resume based on job description and user experience
    
    - **job_description**: The job description to tailor the resume for
    - **user_experience**: User's experience summary (optional)
    - **target_role**: Target role/position
    - **preferred_style**: Resume style preference (default: "professional")
    - Returns generated resume data
    """
    try:
        # Generate unique generation ID
        generation_id = str(uuid.uuid4())
        
        # Generate resume
        resume_data = await ai_service.generate_resume(
            request.job_description,
            request.user_experience,
            request.target_role
        )
        
        # Calculate confidence score (placeholder - could be based on AI model confidence)
        confidence_score = 0.85  # This could be extracted from AI model response
        
        return GenerateResumeResponse(
            generation_id=generation_id,
            resume_data=resume_data,
            job_description=request.job_description,
            target_role=request.target_role,
            generation_timestamp=datetime.utcnow(),
            confidence_score=confidence_score
        )
        
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume generation failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@router.get("/get-pdf/{file_id}")
async def get_pdf_file(
    file_id: str,
    document_service = Depends(get_document_service)
):
    """
    Get the original PDF file by file ID
    
    - **file_id**: The ID of the uploaded file
    
    Returns the PDF file content
    """
    try:
        # Get PDF file
        pdf_data = await document_service.get_pdf_file(file_id)
        
        if pdf_data is None:
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        file_content, filename = pdf_data
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": filename,
            "file_size": len(file_content),
            "content": file_content  # Note: This will be base64 encoded in JSON response
        }
        
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PDF file: {str(e)}")

@router.get("/get-txt/{file_id}")
async def get_txt_file(
    file_id: str,
    document_service = Depends(get_document_service)
):
    """
    Get the extracted TXT file by file ID
    
    - **file_id**: The ID of the uploaded file
    
    Returns the TXT file content
    """
    try:
        # Get TXT file
        txt_data = await document_service.get_txt_file(file_id)
        
        if txt_data is None:
            raise HTTPException(status_code=404, detail="TXT file not found")
        
        text_content, filename = txt_data
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": filename,
            "content": text_content,
            "content_length": len(text_content)
        }
        
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get TXT file: {str(e)}")

@router.get("/file-info/{file_id}")
async def get_file_info(
    file_id: str,
    document_service = Depends(get_document_service)
):
    """
    Get information about both PDF and TXT files by file ID
    
    - **file_id**: The ID of the uploaded file
    
    Returns information about both files
    """
    try:
        # Get file information
        file_info = document_service.get_file_info_both(file_id)
        
        if file_info is None:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "file_info": file_info
        }
        
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}") 