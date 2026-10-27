from typing import List, Optional
from pydantic import BaseModel, Field


class JobProfile(BaseModel):
    job_title: Optional[str] = None

    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)

    minimum_experience_years: Optional[float] = Field(
        default=None,
        ge=0,
    )

    required_education: Optional[str] = None