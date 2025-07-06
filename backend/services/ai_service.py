from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser, ResponseSchema, StructuredOutputParser
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import json
import os

from backend.core.config import settings
from backend.core.exceptions import AIProcessingException
from backend.resume import ResumeModel

class JobAnalysisOutput(BaseModel):
    """Structured output for job analysis"""
    key_requirements: List[str] = Field(description="Key job requirements")
    required_skills: List[str] = Field(description="Required skills for the position")
    preferred_skills: List[str] = Field(description="Preferred skills for the position")
    experience_level: str = Field(description="Required experience level")
    industry: str = Field(description="Industry or domain")

class KeywordExtractionOutput(BaseModel):
    """Structured output for keyword extraction"""
    keywords: List[str] = Field(description="Extracted keywords")
    scores: Dict[str, float] = Field(description="Relevance scores for each keyword")

class KeywordComparisonOutput(BaseModel):
    """Structured output for keyword comparison"""
    job_keywords: List[str] = Field(description="Keywords extracted from job description")
    resume_keywords: List[str] = Field(description="Keywords extracted from resume")
    missing_keywords: List[str] = Field(description="Keywords in job description but not in resume")
    matching_keywords: List[str] = Field(description="Keywords that match between job and resume")
    keyword_scores: Dict[str, float] = Field(description="Relevance scores for missing keywords")

class AIServiceInterface(ABC):
    """Abstract interface for AI services following Dependency Inversion Principle"""
    
    @abstractmethod
    async def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """Analyze job description and extract key information"""
        pass
    
    @abstractmethod
    async def extract_keywords(self, text: str, max_keywords: int = 20) -> Dict[str, Any]:
        """Extract keywords from text"""
        pass
    
    @abstractmethod
    async def generate_resume(self, job_description: str, user_experience: str, target_role: str) -> Dict[str, Any]:
        """Generate resume based on job description and user experience"""
        pass
    
    @abstractmethod
    async def enhanced_analyze_job(self, job_description: str, resume_text: str) -> Dict[str, Any]:
        """Enhanced job analysis with resume comparison"""
        pass

class GeminiAIService(AIServiceInterface):
    """Concrete implementation of AI service using Google Gemini"""
    
    def __init__(self):
        if not settings.groq_api_key:
            raise AIProcessingException("GROQ_API_KEY not configured")
        
        self.llm = ChatGroq(
            model=settings.ai_model,
            groq_api_key=settings.groq_api_key,
            temperature=0.1,  # Lower temperature for more consistent outputs
            max_tokens=4096
        )
        
        # Initialize output parsers
        self.resume_parser = PydanticOutputParser(pydantic_object=ResumeModel)
        self.job_analysis_parser = PydanticOutputParser(pydantic_object=JobAnalysisOutput)
        self.keyword_parser = PydanticOutputParser(pydantic_object=KeywordExtractionOutput)
        self.keyword_comparison_parser = PydanticOutputParser(pydantic_object=KeywordComparisonOutput)
    
    async def analyze_job_description(self, job_description: str) -> Dict[str, Any]:
        """Analyze job description and extract key information"""
        try:
            system_prompt = """
            You are an expert HR analyst with deep knowledge of job market trends and hiring requirements.
            Analyze the provided job description and extract structured information about the position.
            
            Focus on:
            1. Key requirements that are essential for the role
            2. Required skills that candidates must have
            3. Preferred skills that would be beneficial
            4. Experience level (entry, mid, senior, lead, etc.)
            5. Industry or domain context
            
            Be specific and accurate in your analysis.
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", "Analyze this job description:\n{job_description}\n\n{format_instructions}")
            ])
            
            # Create the chain with structured output parsing
            chain = prompt | self.llm | self.job_analysis_parser
            
            result = await chain.ainvoke({
                "job_description": job_description,
                "format_instructions": self.job_analysis_parser.get_format_instructions()
            })
            
            return result.model_dump()
            
        except Exception as e:
            raise AIProcessingException(f"Failed to analyze job description: {str(e)}")
    
    async def extract_keywords(self, text: str, max_keywords: int = 20) -> Dict[str, Any]:
        """Extract keywords from text with relevance scores"""
        try:
            system_prompt = f"""
            You are a keyword extraction expert specializing in resume and job description analysis.
            Extract the top {max_keywords} most relevant keywords from the given text.
            
            Guidelines:
            - Focus on technical skills, tools, technologies, and professional terms
            - Provide relevance scores between 0.0 and 1.0 (1.0 being most relevant)
            - Consider industry context and job market relevance
            - Avoid generic terms unless they are highly relevant
            - Include both technical and soft skills
            - Normalize keywords (e.g., "Python" not "python programming")
            
            Return structured data with keywords and their relevance scores.
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", "Extract keywords from this text:\n{text}\n\n{format_instructions}")
            ])
            
            # Create the chain with structured output parsing
            chain = prompt | self.llm | self.keyword_parser
            
            result = await chain.ainvoke({
                "text": text,
                "format_instructions": self.keyword_parser.get_format_instructions()
            })
            
            return result.model_dump()
            
        except Exception as e:
            raise AIProcessingException(f"Failed to extract keywords: {str(e)}")
    
    async def enhanced_analyze_job(self, job_description: str, resume_text: str) -> Dict[str, Any]:
        """Enhanced job analysis with resume comparison"""
        try:
            # First, analyze the job description
            job_analysis = await self.analyze_job_description(job_description)
            
            # Extract keywords from both job description and resume
            job_keywords_result = await self.extract_keywords(job_description, max_keywords=30)
            resume_keywords_result = await self.extract_keywords(resume_text, max_keywords=30)
            
            # Compare keywords to find missing ones
            system_prompt = """
            You are an expert in resume and job description analysis.
            Compare the keywords from a job description and a resume to identify:
            1. Keywords that are in the job description but missing from the resume
            2. Keywords that match between both documents
            3. Relevance scores for the missing keywords
            
            Guidelines:
            - Focus on technical skills, tools, technologies, and professional terms
            - Consider variations and synonyms (e.g., "Python" matches "Python programming")
            - Provide relevance scores between 0.0 and 1.0 for missing keywords
            - Prioritize skills that are explicitly required in the job description
            - Normalize keywords for comparison
            
            Return structured data with the comparison results.
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", """
                Job Description Keywords: {job_keywords}
                Resume Keywords: {resume_keywords}
                
                Compare these keywords and identify missing ones from the resume.
                
                {format_instructions}
                """)
            ])
            
            # Create the chain with structured output parsing
            chain = prompt | self.llm | self.keyword_comparison_parser
            
            comparison_result = await chain.ainvoke({
                "job_keywords": job_keywords_result.get("keywords", []),
                "resume_keywords": resume_keywords_result.get("keywords", []),
                "format_instructions": self.keyword_comparison_parser.get_format_instructions()
            })
            
            # Combine all results
            return {
                **job_analysis,
                "resume_content": resume_text,
                "keyword_comparison": comparison_result.model_dump()
            }
            
        except Exception as e:
            raise AIProcessingException(f"Failed to perform enhanced job analysis: {str(e)}")
    
    async def generate_resume(self, job_description: str, user_experience: str, target_role: str) -> Dict[str, Any]:
        """Generate resume based on job description and user experience"""
        try:
            system_prompt = f"""
            You are an experienced tech recruiter and resume expert with deep knowledge of:
            - Software industry hiring practices
            - ATS (Applicant Tracking System) optimization
            - Resume best practices for technical roles
            - Hiring manager expectations at top tech companies
            
            Your goal is to create a highly effective, ATS-friendly, and tailored resume for the target role: {target_role}.
            
            Guidelines:
            1. Tailor the resume specifically to the job description requirements
            2. Use action verbs and quantifiable achievements
            3. Optimize for ATS systems with relevant keywords
            4. Structure content for maximum impact
            5. Ensure professional formatting and clarity
            6. Focus on relevant experience and skills
            
            Consider the job description requirements and user's experience to craft the best possible resume.
            """
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("user", "Job Description:\n{job_description}\n\nUser Experience:\n{user_experience}\n\n{format_instructions}")
            ])
            
            # Create the chain with structured output parsing
            chain = prompt | self.llm | self.resume_parser
            
            result = await chain.ainvoke({
                "job_description": job_description,
                "user_experience": user_experience,
                "format_instructions": self.resume_parser.get_format_instructions()
            })
            
            return result.model_dump()
            
        except Exception as e:
            raise AIProcessingException(f"Failed to generate resume: {str(e)}")

# Factory function for creating AI service instances
def create_ai_service() -> AIServiceInterface:
    """Factory function following Dependency Inversion Principle"""
    return GeminiAIService() 