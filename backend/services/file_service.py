import os
import uuid
from typing import Optional, Tuple
from pathlib import Path
import aiofiles
from datetime import datetime
import io

from backend.core.config import settings
from backend.core.exceptions import FileUploadException, ValidationException
from backend.models.schemas import FileType

class FileService:
    """Service for handling file operations following Single Responsibility Principle"""
    
    def __init__(self):
        self.upload_folder = Path(settings.upload_folder)
        self._ensure_upload_directory()
    
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
        """Extract text content from uploaded file using document service"""
        from backend.services.document_service import create_document_service
        
        document_service = create_document_service()
        return document_service.extract_text_from_file(file_content, file_type)

# Factory function for creating file service instances
def create_file_service() -> FileService:
    """Factory function for file service"""
    return FileService() 