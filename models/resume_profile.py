from typing import Optional, List
from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    job_title: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    responsibilities: List[str] = Field(default_factory=list)
    employment_type: Optional[str] = None
    dates_are_estimated: bool = False


class ResumeProject(BaseModel):
    project_title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    skills: List[str] = Field(default_factory=list)

    # Actual employment and internships only
    work_experience: List[WorkExperience] = Field(default_factory=list)

    # Personal, academic, and portfolio projects
    projects: List[ResumeProject] = Field(default_factory=list)

    total_experience_years: Optional[float] = Field(
        default=None,
        ge=0
    )
    total_experience_explicitly_stated: bool = False
    experience_estimated: bool = False

    highest_completed_education: Optional[str] = None
    education_in_progress: List[str] = Field(default_factory=list)
