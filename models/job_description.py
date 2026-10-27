from typing import Optional

from pydantic import BaseModel, Field


class JobDescription(BaseModel):
    title: Optional[str] = None
    text: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    experience_required: Optional[float] = None
    education_required: Optional[str] = None
