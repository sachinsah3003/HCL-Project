from typing import Optional

from pydantic import BaseModel


class Candidate(BaseModel):
    name: str
    skills: list[str]
    experience: Optional[float] = None
    education: Optional[str] = None