"""Unit tests for src/analysis/experience_evaluator.py (pure logic, no mocks needed)."""
import pytest

from src.analysis.experience_evaluator import evaluate_experience


def test_no_requirement_gives_no_score():
    result = evaluate_experience(None, 3.0)
    assert result["experience_match_score"] is None
    assert result["experience_match_status"] == "Not required"


def test_unknown_candidate_experience_gives_no_score():
    # Project-only candidates have unknown experience; it must not be scored as 0.
    result = evaluate_experience(2, None)
    assert result["experience_match_score"] is None
    assert result["experience_match_status"] == "Unknown"


def test_unknown_experience_is_checked_before_zero_requirement():
    result = evaluate_experience(0, None)
    assert result["experience_match_score"] is None
    assert result["experience_match_status"] == "Unknown"


@pytest.mark.parametrize(
    "required, candidate, expected_score",
    [
        (2, 2.0, 100.0),    # exactly meets
        (2, 5.0, 100.0),    # more than required is capped at 100
        (2, 1.0, 50.0),     # half of the requirement
        (2, 0.0, 0.0),      # no experience at all
        (3, 1.0, 33.33),    # rounded to 2 decimals
        (4, 3.0, 75.0),
    ],
)
def test_score_is_proportional_and_capped(required, candidate, expected_score):
    result = evaluate_experience(required, candidate)
    assert result["experience_match_score"] == expected_score


@pytest.mark.parametrize("candidate", [0.0, 1.0, 10.0])
def test_zero_year_requirement_is_always_fully_met(candidate):
    # The job description says "0-2 years", so the minimum is 0 and nobody is penalised.
    result = evaluate_experience(0, candidate)
    assert result["experience_match_score"] == 100.0
    assert result["experience_match_status"] == "Meets requirement"


def test_status_meets_requirement():
    assert evaluate_experience(2, 2.0)["experience_match_status"] == "Meets requirement"
    assert evaluate_experience(2, 4.0)["experience_match_status"] == "Meets requirement"


def test_status_below_requirement():
    assert evaluate_experience(2, 1.5)["experience_match_status"] == "Below requirement"


def test_estimated_experience_needs_review_but_is_still_scored():
    result = evaluate_experience(2, 1.5, experience_estimated=True)
    assert result["experience_match_status"] == "Needs review"
    assert result["experience_match_score"] == 75.0


def test_estimated_flag_overrides_meets_status():
    result = evaluate_experience(2, 3.0, experience_estimated=True)
    assert result["experience_match_status"] == "Needs review"
    assert result["experience_match_score"] == 100.0


def test_result_always_has_both_keys():
    for args in [(None, None), (2, None), (2, 1.0), (0, 0.0)]:
        result = evaluate_experience(*args)
        assert set(result) == {"experience_match_score", "experience_match_status"}
