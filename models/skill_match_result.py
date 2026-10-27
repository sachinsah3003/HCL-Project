from typing import List, Optional

from pydantic import BaseModel, Field


class SkillMatchItem(BaseModel):
    required_skill: str
    equivalent: bool
    resume_evidence: Optional[str] = None


class SkillMatchResponse(BaseModel):
    results: List[SkillMatchItem] = Field(
        default_factory=list
    )
