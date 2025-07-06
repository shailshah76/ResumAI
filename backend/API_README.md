# ResumAI API Documentation

## Overview

ResumAI API is a FastAPI-based REST API that provides AI-powered resume generation and analysis services. The API follows industry standards and SOLID principles for maintainable and scalable code.

## Architecture

The API follows a clean architecture pattern with the following layers:

```
backend/
├── api/                    # API layer (routes, controllers)
│   └── routes/
│       └── resume_routes.py
├── core/                   # Core configuration and utilities
│   ├── config.py          # Application settings
│   └── exceptions.py      # Custom exception classes
├── models/                 # Data models and schemas
│   └── schemas.py         # Pydantic models for requests/responses
├── services/              # Business logic layer
│   ├── ai_service.py      # AI processing service
│   └── file_service.py    # File handling service
├── app.py                 # FastAPI application factory
├── run.py                 # Application entry point
└── resume.py              # Resume data models
```

## SOLID Principles Implementation

### 1. Single Responsibility Principle (SRP)
- Each service has a single responsibility
- `AIService`: Handles AI processing
- `FileService`: Handles file operations
- `Config`: Manages application settings

### 2. Open/Closed Principle (OCP)
- Custom exception hierarchy allows extension without modification
- Service interfaces allow new implementations without changing existing code

### 3. Liskov Substitution Principle (LSP)
- All service implementations can be substituted for their interfaces
- Exception classes can be substituted for the base exception

### 4. Interface Segregation Principle (ISP)
- Separate interfaces for different concerns
- Specific request/response models for each endpoint

### 5. Dependency Inversion Principle (DIP)
- High-level modules depend on abstractions
- Dependency injection for services
- Factory functions for service creation

## API Endpoints

### 1. POST /api/v1/upload-resume
Upload a resume file for processing.

**Request:**
- `file`: Resume file (PDF, DOCX, or TXT)
- Content-Type: multipart/form-data

**Response:**
```json
{
  "file_id": "uuid",
  "filename": "resume.pdf",
  "file_type": "pdf",
  "upload_timestamp": "2024-01-01T00:00:00Z",
  "file_size": 1024,
  "message": "Resume uploaded successfully"
}
```

### 2. POST /api/v1/analyze-job
Analyze a job description to extract key requirements and skills.

**Request:**
```json
{
  "job_description": "Software Engineer position requiring Python, FastAPI, and 3+ years experience..."
}
```

**Response:**
```json
{
  "analysis_id": "uuid",
  "job_description": "Software Engineer position...",
  "key_requirements": ["Python", "FastAPI", "3+ years experience"],
  "required_skills": ["Python", "FastAPI", "REST APIs"],
  "preferred_skills": ["Docker", "AWS", "PostgreSQL"],
  "experience_level": "Mid-level",
  "industry": "Technology",
  "analysis_timestamp": "2024-01-01T00:00:00Z"
}
```

### 3. POST /api/v1/extract-keywords
Extract keywords from text with relevance scores.

**Request:**
```json
{
  "text": "Software engineer with experience in Python, FastAPI, and cloud technologies...",
  "max_keywords": 20
}
```

**Response:**
```json
{
  "extraction_id": "uuid",
  "original_text": "Software engineer with experience...",
  "keywords": ["Python", "FastAPI", "cloud", "software engineer"],
  "keyword_scores": {
    "Python": 0.95,
    "FastAPI": 0.88,
    "cloud": 0.75,
    "software engineer": 0.92
  },
  "total_keywords": 4,
  "extraction_timestamp": "2024-01-01T00:00:00Z"
}
```

### 4. POST /api/v1/generate-resume
Generate a tailored resume based on job description and user experience.

**Request:**
```json
{
  "job_description": "Software Engineer position...",
  "user_experience": "5 years of experience in Python development...",
  "target_role": "Senior Software Engineer",
  "preferred_style": "professional"
}
```

**Response:**
```json
{
  "generation_id": "uuid",
  "resume_data": {
    "summary": "Experienced software engineer...",
    "education": [...],
    "experience": [...],
    "projects": [...],
    "skills": {...}
  },
  "job_description": "Software Engineer position...",
  "target_role": "Senior Software Engineer",
  "generation_timestamp": "2024-01-01T00:00:00Z",
  "confidence_score": 0.85
}
```

## Setup and Installation

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

3. Run the API:
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/api/v1/health`

## Error Handling

The API uses a centralized error handling system with custom exceptions:

- `ValidationException`: Input validation errors (400)
- `FileUploadException`: File upload errors (400)
- `AIProcessingException`: AI processing errors (500)
- `ResourceNotFoundException`: Resource not found (404)
- `AuthenticationException`: Authentication errors (401)

## Configuration

Configuration is managed through the `Settings` class in `core/config.py`:

- API settings (title, version, description)
- Server settings (host, port, debug mode)
- AI settings (model, API key)
- File upload settings (max size, allowed types)
- CORS settings

## Testing

To test the API endpoints:

1. Start the server
2. Use the interactive docs at `/docs`
3. Or use curl/Postman with the examples above

## Production Deployment

For production deployment:

1. Set `debug=False` in settings
2. Configure proper CORS origins
3. Use a production ASGI server like Gunicorn
4. Set up proper logging
5. Configure environment variables securely

## Contributing

When contributing to this API:

1. Follow SOLID principles
2. Add proper error handling
3. Include input validation
4. Write comprehensive tests
5. Update documentation
6. Use type hints throughout 