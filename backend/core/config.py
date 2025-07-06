from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings following the Single Responsibility Principle"""
    
    # API Configuration
    api_title: str = "ResumAI API"
    api_version: str = "1.0.0"
    api_description: str = "AI-powered resume generation and analysis API"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # AI Configuration
    groq_api_key: Optional[str] = None
    ai_model: str = "llama3-8b-8192"
    
    # File Upload Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list = [".pdf", ".docx", ".txt"]
    upload_folder: str = "uploads"
    
    # CORS Configuration
    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load from environment variables if not set
        if not self.groq_api_key:
            self.groq_api_key = os.getenv("GROQ_API_KEY")

settings = Settings() 