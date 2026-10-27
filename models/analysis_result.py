from typing import Optional

from pydantic import BaseModel, Field, computed_field


class AnalysisResult(BaseModel):
    candidate_name: str
    candidate_summary: Optional[str] = None

    jd_similarity_score: float = Field(ge=0, le=100)
    skills_match_score: float = Field(ge=0, le=100)
    final_score: float = Field(ge=0, le=100)

    required_skills: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    matched_required_groups: list[dict] = Field(default_factory=list)
    missing_required_groups: list[dict] = Field(default_factory=list)
    matched_preferred_groups: list[dict] = Field(default_factory=list)
    missing_preferred_groups: list[dict] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    matched_preferred_skills: list[str] = Field(default_factory=list)
    missing_preferred_skills: list[str] = Field(default_factory=list)
    required_skills_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )
    preferred_skills_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )

    rank: Optional[int] = Field(default=None, ge=1)
    required_experience_years: Optional[float] = None
    candidate_experience_years: Optional[float] = Field(
        default=None,
        ge=0,
    )
    experience_match_score: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
    )
    candidate_education: Optional[str] = None
    education_in_progress: list[str] = Field(default_factory=list)
    experience_match_status: str = "Not specified"
    required_education_level: Optional[int] = None
    candidate_education_level: Optional[int] = None
    education_match_status: str = "Not specified"

    @computed_field
    @property
    def required_skills_count(self) -> int:
        return len(self.required_skills)

    @computed_field
    @property
    def matched_skills_count(self) -> int:
        return len(self.matched_skills)

    @computed_field
    @property
    def missing_skills_count(self) -> int:
        return len(self.missing_skills)
