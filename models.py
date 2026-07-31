from pydantic import BaseModel
from typing import List, Optional

class ContactInfo(BaseModel):
    name: Optional[str] = "Applicant Name"
    email: Optional[str] = ""
    phone: Optional[str] = ""
    location: Optional[str] = ""
    linkedin: Optional[str] = ""

class Experience(BaseModel):
    job_title: str
    company_name: str
    start_date: str
    end_date: str
    achievements: List[str]

class Education(BaseModel):
    degree: str
    institution: str
    graduation_date: str
    details: Optional[str] = "" 

class Project(BaseModel):
    title: str
    description: str

class Course(BaseModel):
    title: str
    institution: Optional[str] = ""
    date: Optional[str] = ""
    description: str

class ResumeAnalysisResult(BaseModel):
    match_score: int
    missing_keywords: List[str]
    contact_info: ContactInfo
    summary: Optional[str] = ""
    experience: List[Experience] = []
    education: List[Education] = []
    projects: List[Project] = []
    courses: List[Course] = []
    soft_skills: List[str] = []
    technical_skills: List[str] = []
    languages: List[str] = []