from typing import List, Dict, Optional, Union
from pydantic import BaseModel

class EducationModel(BaseModel):
    university: str = ""
    courses: List[str] = []
    date_started: str = ""
    date_completed: str = ""
    gpa: Optional[float] = None
    ta: bool = False
    place: str = ""

class ExperienceModel(BaseModel):
    company: str = ""
    role: str = ""
    date_started: str = ""
    date_completed: str = ""
    work: List[str] = []
    place: str = ""

class ProjectModel(BaseModel):
    name: str = ""
    tools: List[str] = []
    github_link: str = ""
    description: List[str] = []

class ResearchModel(BaseModel):
    title: str = ""
    publication: str = ""
    date_published: str = ""
    link: str = ""
    description: List[str] = []

class ResumeModel(BaseModel):
    summary: str = ""
    education: List[EducationModel] = []
    experience: List[ExperienceModel] = []
    projects: List[ProjectModel] = []
    research: List[ResearchModel] = []
    skills: Dict[str, List[str]] = {}
