from typing import Optional, Any

class CustomException(Exception):
    """Base custom exception class following the Open/Closed Principle"""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 500, 
        detail: Optional[str] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)

class ValidationException(CustomException):
    """Exception for validation errors"""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, status_code=400, detail=detail)

class FileUploadException(CustomException):
    """Exception for file upload errors"""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, status_code=400, detail=detail)

class AIProcessingException(CustomException):
    """Exception for AI processing errors"""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, status_code=500, detail=detail)

class ResourceNotFoundException(CustomException):
    """Exception for resource not found errors"""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, status_code=404, detail=detail)

class AuthenticationException(CustomException):
    """Exception for authentication errors"""
    
    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, status_code=401, detail=detail) 