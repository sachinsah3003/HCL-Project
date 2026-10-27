"""Shared fixtures for the unit tests.

The Gemini, Sentence-Transformers and skill-matching calls are replaced with fixed values,
so these tests are fast, free, and give the same result every run.
"""
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.analysis.resume_analyzer import ResumeAnalyzer

MODULE = "src.analysis.resume_analyzer"


def make_skill_details(
    matched=("Python", "Git"),
    missing=("Docker",),
    matched_pref=("React",),
    missing_pref=("Jest",),
    skills_score=80.0,
    required_score=80.0,
    preferred_score=50.0,
):
    """Return a dict shaped like match_required_skills(..., return_details=True)."""
    return {
        "matched_required": list(matched),
        "missing_required": list(missing),
        "matched_preferred": list(matched_pref),
        "missing_preferred": list(missing_pref),
        "skills_score": skills_score,
        "required_score": required_score,
        "preferred_score": preferred_score,
    }


def make_profile(years=2.0, estimated=False):
    """Return an object shaped like the ResumeProfile that analyze_resume reads."""
    return SimpleNamespace(
        total_experience_years=years,
        experience_estimated=estimated,
        highest_completed_education="Bachelor's degree",
        education_in_progress=["B.Tech Computer Science"],
    )


def make_result(final_score, name="Candidate"):
    """A dict with the same keys analyze_resume returns (used by the ranking tests)."""
    return {
        "jd_similarity_score": 60.0,
        "skills_match_score": 70.0,
        "experience_match_score": 100.0,
        "final_score": final_score,
        "required_skills": ["Python", "Git"],
        "preferred_skills": ["React"],
        "matched_skills": ["Python"],
        "missing_skills": ["Git"],
        "matched_preferred_skills": ["React"],
        "missing_preferred_skills": [],
        "required_skills_score": 50.0,
        "preferred_skills_score": 100.0,
        "required_experience_years": 2,
        "candidate_experience_years": 2.0,
        "candidate_education": "Bachelor's degree",
        "education_in_progress": ["B.Tech Computer Science"],
        "experience_match_status": "Meets requirement",
    }


@pytest.fixture
def analyzer():
    with patch(f"{MODULE}.load_skills", return_value=[]):
        return ResumeAnalyzer("unused_skills.txt")


@pytest.fixture
def run_analysis(analyzer):
    """Run analyze_resume with fixed similarity / skill / profile results.

    Returns (result, mocks) so a test can check both the output and the calls made.
    """
    def _run(similarity=60.0, skills_score=80.0, candidate_years=2.0, estimated=False,
             required_years=2, **skill_overrides):
        details = make_skill_details(skills_score=skills_score, **skill_overrides)
        profile = make_profile(candidate_years, estimated)
        with patch(f"{MODULE}.calculate_semantic_similarity", return_value=similarity) as sim, \
             patch(f"{MODULE}.match_required_skills", return_value=details) as match, \
             patch(f"{MODULE}.extract_resume_profile", return_value=profile) as prof:
            result = analyzer.analyze_resume(
                "JD text", "resume text", ["Python", "Git", "Docker"],
                required_experience_years=required_years,
                preferred_skills=["React", "Jest"],
            )
        return result, SimpleNamespace(sim=sim, match=match, prof=prof)
    return _run
