import os
import uuid
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import aiofiles
from datetime import datetime
import io
import tempfile

# Import text extraction libraries
try:
    import PyPDF2
    from docx import Document
except ImportError:
    PyPDF2 = None
    Document = None

# Import Docling for enhanced document processing
try:
    from docling.document_converter import DocumentConverter
    from docling.core.document import DoclingDocument
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

from backend.core.config import settings
from backend.core.exceptions import FileUploadException, ValidationException
from backend.models.schemas import FileType

class DocumentService:
    """Enhanced service for handling document operations with Docling integration"""
    
    def __init__(self, use_docling: bool = True):
        self.upload_folder = Path(settings.upload_folder)
        self.use_docling = use_docling and DOCLING_AVAILABLE
        self._ensure_upload_directory()
        
        # Initialize Docling converter if available
        if self.use_docling:
            try:
                self.docling_converter = DocumentConverter()
            except Exception as e:
                print(f"Warning: Failed to initialize Docling converter: {e}")
                self.use_docling = False
    
    def _ensure_upload_directory(self):
        """Ensure upload directory exists"""
        self.upload_folder.mkdir(exist_ok=True)
    
    def validate_file(self, file_content: bytes, filename: str, file_type: FileType) -> None:
        """Validate uploaded file"""
        # Check file size
        if len(file_content) > settings.max_file_size:
            raise FileUploadException(
                f"File size exceeds maximum allowed size of {settings.max_file_size} bytes"
            )
        
        # Check file extension
        file_extension = Path(filename).suffix.lower()
        if file_extension not in settings.allowed_file_types:
            raise FileUploadException(
                f"File type {file_extension} not allowed. Allowed types: {settings.allowed_file_types}"
            )
        
        # Validate file type matches extension
        if file_extension != f".{file_type.value}":
            raise ValidationException(
                f"File extension {file_extension} doesn't match declared file type {file_type.value}"
            )
    
    async def save_file(self, file_content: bytes, filename: str, file_type: FileType) -> Tuple[str, int]:
        """Save uploaded file and return file ID and size"""
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Create filename with ID
            safe_filename = f"{file_id}_{filename}"
            file_path = self.upload_folder / safe_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            file_size = len(file_content)
            return file_id, file_size
            
        except Exception as e:
            raise FileUploadException(f"Failed to save file: {str(e)}")
    
    async def read_file(self, file_id: str) -> Optional[bytes]:
        """Read file content by file ID"""
        try:
            # Find file by ID
            for file_path in self.upload_folder.iterdir():
                if file_path.name.startswith(file_id):
                    async with aiofiles.open(file_path, 'rb') as f:
                        return await f.read()
            return None
            
        except Exception as e:
            raise FileUploadException(f"Failed to read file: {str(e)}")
    
    async def get_file_by_id(self, file_id: str) -> Optional[Tuple[bytes, str, FileType]]:
        """Get file content, filename, and type by file ID"""
        try:
            for file_path in self.upload_folder.iterdir():
                if file_path.name.startswith(file_id):
                    # Read file content
                    async with aiofiles.open(file_path, 'rb') as f:
                        file_content = await f.read()
                    
                    # Determine file type from extension
                    file_extension = file_path.suffix.lower()
                    if file_extension == '.pdf':
                        file_type = FileType.PDF
                    elif file_extension == '.docx':
                        file_type = FileType.DOCX
                    elif file_extension == '.txt':
                        file_type = FileType.TXT
                    else:
                        raise ValidationException(f"Unsupported file type: {file_extension}")
                    
                    return file_content, file_path.name, file_type
            return None
            
        except Exception as e:
            raise FileUploadException(f"Failed to get file: {str(e)}")
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file by file ID"""
        try:
            for file_path in self.upload_folder.iterdir():
                if file_path.name.startswith(file_id):
                    file_path.unlink()
                    return True
            return False
            
        except Exception as e:
            raise FileUploadException(f"Failed to delete file: {str(e)}")
    
    def get_file_info(self, file_id: str) -> Optional[dict]:
        """Get file information by file ID"""
        try:
            for file_path in self.upload_folder.iterdir():
                if file_path.name.startswith(file_id):
                    stat = file_path.stat()
                    return {
                        "file_id": file_id,
                        "filename": file_path.name,
                        "size": stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime),
                        "modified": datetime.fromtimestamp(stat.st_mtime)
                    }
            return None
            
        except Exception as e:
            raise FileUploadException(f"Failed to get file info: {str(e)}")
    
    def extract_text_from_file(self, file_content: bytes, file_type: FileType) -> str:
        """Extract text content from uploaded file using Docling or fallback to local libraries"""
        try:
            if file_type == FileType.TXT:
                return file_content.decode('utf-8')
            
            # Try Docling first if available and enabled
            if self.use_docling:
                try:
                    return self._extract_text_with_docling(file_content, file_type)
                except Exception as e:
                    print(f"Docling extraction failed, falling back to local libraries: {e}")
            
            # Fallback to local libraries
            return self._extract_text_with_local_libraries(file_content, file_type)
                
        except Exception as e:
            raise FileUploadException(f"Failed to extract text from file: {str(e)}")
    
    def _extract_text_with_docling(self, file_content: bytes, file_type: FileType) -> str:
        """Extract text using Docling library"""
        try:
            # Create temporary file for Docling
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type.value}") as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Convert document using Docling
                result = self.docling_converter.convert(temp_file_path)
                
                # Extract text from DoclingDocument
                if hasattr(result, 'document') and result.document:
                    # Try to get markdown format first (cleaner text)
                    try:
                        return result.document.export_to_markdown()
                    except:
                        # Fallback to text extraction
                        text_parts = []
                        for page in result.document.pages:
                            for element in page.elements:
                                if hasattr(element, 'text') and element.text:
                                    text_parts.append(element.text)
                        return "\n".join(text_parts)
                else:
                    raise Exception("Docling conversion failed to produce document")
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            raise Exception(f"Docling extraction failed: {str(e)}")
    
    def _extract_text_with_local_libraries(self, file_content: bytes, file_type: FileType) -> str:
        """Extract text using local libraries (PyPDF2, python-docx)"""
        if file_type == FileType.PDF:
            if PyPDF2 is None:
                raise FileUploadException("PyPDF2 library not installed. Please install it to extract text from PDF files.")
            
            # Extract text from PDF
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        elif file_type == FileType.DOCX:
            if Document is None:
                raise FileUploadException("python-docx library not installed. Please install it to extract text from DOCX files.")
            
            # Extract text from DOCX
            doc = Document(io.BytesIO(file_content))
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text.strip()
            
        else:
            raise ValidationException(f"Unsupported file type: {file_type}")
    
    def extract_text_with_metadata(self, file_content: bytes, file_type: FileType) -> Dict[str, Any]:
        """Extract text and metadata from document using Docling"""
        if not self.use_docling:
            # Fallback to basic text extraction
            text = self.extract_text_from_file(file_content, file_type)
            return {
                "text": text,
                "metadata": {
                    "extraction_method": "local_libraries",
                    "file_type": file_type.value
                }
            }
        
        try:
            # Create temporary file for Docling
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type.value}") as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                # Convert document using Docling
                result = self.docling_converter.convert(temp_file_path)
                
                if hasattr(result, 'document') and result.document:
                    # Extract text
                    try:
                        text = result.document.export_to_markdown()
                    except:
                        text_parts = []
                        for page in result.document.pages:
                            for element in page.elements:
                                if hasattr(element, 'text') and element.text:
                                    text_parts.append(element.text)
                        text = "\n".join(text_parts)
                    
                    # Extract metadata
                    metadata = {
                        "extraction_method": "docling",
                        "file_type": file_type.value,
                        "pages": len(result.document.pages) if hasattr(result.document, 'pages') else 0,
                        "elements": sum(len(page.elements) for page in result.document.pages) if hasattr(result.document, 'pages') else 0
                    }
                    
                    return {
                        "text": text,
                        "metadata": metadata
                    }
                else:
                    raise Exception("Docling conversion failed to produce document")
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            # Fallback to basic extraction
            text = self._extract_text_with_local_libraries(file_content, file_type)
            return {
                "text": text,
                "metadata": {
                    "extraction_method": "local_libraries_fallback",
                    "file_type": file_type.value,
                    "error": str(e)
                }
            }

# Factory function for creating document service instances
def create_document_service(use_docling: bool = True) -> DocumentService:
    """Factory function for document service"""
    return DocumentService(use_docling=use_docling) 