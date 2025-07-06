from pydantic import BaseModel, Field, validator, model_validator
from typing import List, Dict, Optional, Union
from enum import Enum
import uuid
from datetime import datetime

class FileType(str, Enum):
    """Supported file types for resume upload"""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"



class UploadResumeResponse(BaseModel):
    """Response model for resume upload"""
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    file_type: FileType = Field(..., description="File type")
    upload_timestamp: datetime = Field(..., description="Upload timestamp")
    file_size: int = Field(..., description="File size in bytes")
    message: str = Field(..., description="Upload status message")
    job_description: Optional[str] = Field(None, description="Job description if provided")

class ExtractKeywordsRequest(BaseModel):
    """Request model for keyword extraction"""
    text: str = Field(..., min_length=10, description="Text to extract keywords from")
    max_keywords: int = Field(default=20, ge=1, le=100, description="Maximum number of keywords to extract")
    
    @validator('text')
    def validate_text(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Text must be at least 10 characters long")
        return v.strip()

class ExtractKeywordsResponse(BaseModel):
    """Response model for keyword extraction"""
    extraction_id: str = Field(..., description="Unique extraction identifier")
    original_text: str = Field(..., description="Original text")
    keywords: List[str] = Field(..., description="Extracted keywords")
    keyword_scores: Dict[str, float] = Field(..., description="Keyword relevance scores")
    total_keywords: int = Field(..., description="Total number of keywords extracted")
    extraction_timestamp: datetime = Field(..., description="Extraction timestamp")

class GenerateResumeRequest(BaseModel):
    """Request model for resume generation"""
    job_description: str = Field(..., min_length=10, description="Job description")
    user_experience: Optional[str] = Field(default="", description="User's experience summary")
    target_role: str = Field(..., description="Target role/position")
    preferred_style: str = Field(default="professional", description="Resume style preference")
    
    @validator('job_description')
    def validate_job_description(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Job description must be at least 10 characters long")
        return v.strip()
    
    @validator('target_role')
    def validate_target_role(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Target role cannot be empty")
        return v.strip()

class GenerateResumeResponse(BaseModel):
    """Response model for resume generation"""
    generation_id: str = Field(..., description="Unique generation identifier")
    resume_data: Dict = Field(..., description="Generated resume data")
    job_description: str = Field(..., description="Original job description")
    target_role: str = Field(..., description="Target role")
    generation_timestamp: datetime = Field(..., description="Generation timestamp")
    confidence_score: float = Field(..., ge=0, le=1, description="AI confidence score")

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
    timestamp: datetime = Field(..., description="Error timestamp")

class EnhancedAnalyzeJobRequest(BaseModel):
    """Enhanced request model for job analysis with resume comparison"""
    job_description: str = Field(..., min_length=10, description="Job description text")
    resume_text: Optional[str] = Field(None, description="Resume content as text (required if file_id not provided)")
    file_id: Optional[str] = Field(None, description="File ID of uploaded resume (required if resume_text not provided)")
    
    @validator('job_description')
    def validate_job_description(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError("Job description must be at least 10 characters long")
        return v.strip()
    
    @model_validator(mode='after')
    def validate_resume_input(self):
        if not self.resume_text and not self.file_id:
            raise ValueError("Either resume_text or file_id must be provided")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_description": "We are looking for a Senior Software Engineer with expertise in Python, FastAPI, and cloud technologies. The ideal candidate should have 5+ years of experience in software development, knowledge of Docker, Kubernetes, and AWS.",
                "resume_text": "Experienced software developer with 3 years of experience in Python and web development. Proficient in Django, Flask, and basic cloud services."
            }
        }

class KeywordComparisonResult(BaseModel):
    """Model for keyword comparison results"""
    job_keywords: List[str] = Field(..., description="Keywords extracted from job description")
    resume_keywords: List[str] = Field(..., description="Keywords extracted from resume")
    missing_keywords: List[str] = Field(..., description="Keywords in job description but not in resume")
    matching_keywords: List[str] = Field(..., description="Keywords that match between job and resume")
    keyword_scores: Dict[str, float] = Field(..., description="Relevance scores for missing keywords")

class EnhancedAnalyzeJobResponse(BaseModel):
    """Enhanced response model for job analysis with resume comparison"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    job_description: str = Field(..., description="Original job description")
    resume_content: str = Field(..., description="Parsed resume content")
    key_requirements: List[str] = Field(..., description="Key job requirements")
    required_skills: List[str] = Field(..., description="Required skills")
    preferred_skills: List[str] = Field(..., description="Preferred skills")
    experience_level: str = Field(..., description="Required experience level")
    industry: str = Field(..., description="Industry/domain")
    keyword_comparison: KeywordComparisonResult = Field(..., description="Keyword comparison results")
    analysis_timestamp: datetime = Field(..., description="Analysis timestamp") 