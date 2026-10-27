"""Tests for the weighted final score in ResumeAnalyzer.analyze_resume.

Weights: 30% JD similarity, 50% skills, 20% experience. When experience is unavailable the
remaining weights are re-normalised: (0.30*sim + 0.50*skills) / 0.80.
All Gemini / embedding calls are mocked, so the numbers below are exact.
"""
import pytest


def test_final_score_with_experience(run_analysis):
    # 0.30*60 + 0.50*80 + 0.20*100 = 18 + 40 + 20
    result, _ = run_analysis(similarity=60.0, skills_score=80.0, candidate_years=2.0)
    assert result["experience_match_score"] == 100.0
    assert result["final_score"] == pytest.approx(78.0)


def test_final_score_renormalises_when_experience_unknown(run_analysis):
    # (0.30*60 + 0.50*80) / 0.80 = 58 / 0.8
    result, _ = run_analysis(similarity=60.0, skills_score=80.0, candidate_years=None)
    assert result["experience_match_score"] is None
    assert result["experience_match_status"] == "Unknown"
    assert result["final_score"] == pytest.approx(72.5)


def test_final_score_renormalises_when_experience_not_required(run_analysis):
    result, _ = run_analysis(similarity=60.0, skills_score=80.0, candidate_years=3.0,
                             required_years=None)
    assert result["experience_match_score"] is None
    assert result["experience_match_status"] == "Not required"
    assert result["final_score"] == pytest.approx(72.5)


def test_partial_experience_lowers_the_score(run_analysis):
    # experience score = 1/2 * 100 = 50 -> 18 + 40 + 10
    result, _ = run_analysis(similarity=60.0, skills_score=80.0, candidate_years=1.0)
    assert result["experience_match_score"] == 50.0
    assert result["final_score"] == pytest.approx(68.0)


def test_estimated_experience_is_still_used_in_the_score(run_analysis):
    # 1.5 of 2 years -> 75, flagged "Needs review" -> 18 + 40 + 15
    result, _ = run_analysis(similarity=60.0, skills_score=80.0, candidate_years=1.5,
                             estimated=True)
    assert result["experience_match_status"] == "Needs review"
    assert result["final_score"] == pytest.approx(73.0)


def test_all_perfect_components_give_100(run_analysis):
    result, _ = run_analysis(similarity=100.0, skills_score=100.0, candidate_years=5.0)
    assert result["final_score"] == pytest.approx(100.0)


def test_all_zero_components_give_0(run_analysis):
    result, _ = run_analysis(similarity=0.0, skills_score=0.0, candidate_years=0.0)
    assert result["final_score"] == pytest.approx(0.0)


def test_skills_carry_more_weight_than_similarity(run_analysis):
    high_skills, _ = run_analysis(similarity=40.0, skills_score=90.0, candidate_years=2.0)
    high_similarity, _ = run_analysis(similarity=90.0, skills_score=40.0, candidate_years=2.0)
    assert high_skills["final_score"] > high_similarity["final_score"]


def test_unknown_experience_is_not_treated_as_zero(run_analysis):
    # Unknown experience must not rank a candidate below one with explicit 0 years.
    unknown, _ = run_analysis(similarity=60.0, skills_score=80.0, candidate_years=None)
    zero_years, _ = run_analysis(similarity=60.0, skills_score=80.0, candidate_years=0.0)
    assert unknown["final_score"] > zero_years["final_score"]


def test_scores_are_rounded_to_two_decimals(run_analysis):
    result, _ = run_analysis(similarity=61.23456, skills_score=79.98765, candidate_years=None)
    for key in ("jd_similarity_score", "skills_match_score", "final_score"):
        assert result[key] == round(result[key], 2)
    assert result["jd_similarity_score"] == 61.23
    assert result["skills_match_score"] == 79.99


def test_skill_lists_are_combined_correctly(run_analysis):
    result, _ = run_analysis(matched=("Python", "Git"), missing=("Docker",),
                             matched_pref=("React",), missing_pref=("Jest",))
    assert result["matched_skills"] == ["Python", "Git"]
    assert result["missing_skills"] == ["Docker"]
    assert result["required_skills"] == ["Python", "Git", "Docker"]
    assert result["preferred_skills"] == ["React", "Jest"]
    assert result["matched_preferred_skills"] == ["React"]
    assert result["missing_preferred_skills"] == ["Jest"]


def test_profile_details_are_passed_through(run_analysis):
    result, _ = run_analysis(candidate_years=1.5, required_years=2)
    assert result["required_experience_years"] == 2
    assert result["candidate_experience_years"] == 1.5
    assert result["candidate_education"] == "Bachelor's degree"
    assert result["education_in_progress"] == ["B.Tech Computer Science"]


def test_dependencies_are_called_with_the_right_inputs(run_analysis):
    _, mocks = run_analysis()
    mocks.sim.assert_called_once_with("JD text", "resume text")
    mocks.match.assert_called_once_with(
        "resume text", ["Python", "Git", "Docker"], ["React", "Jest"], return_details=True
    )
    mocks.prof.assert_called_once_with("resume text")
