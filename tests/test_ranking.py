"""Tests for ResumeAnalyzer.analyze_multiple_resumes: ranking order, rank numbers, validation.

analyze_resume is replaced by a fake that returns a fixed final score per resume, so only the
sorting / ranking / validation logic is tested here. The real AnalysisResult model validates
every result, so a failure with a validation error means the fake result in conftest.py
(make_result) does not match the model's field names or types.
"""
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from conftest import make_result
from src.analysis.resume_analyzer import ResumeAnalyzer


@pytest.fixture
def job_profile():
    return SimpleNamespace(
        required_skills=["Python", "Git"],
        preferred_skills=["React"],
        minimum_experience_years=2,
    )


def rank(analyzer, job_profile, scores_by_text):
    """Run analyze_multiple_resumes with a fake analyze_resume that returns fixed scores."""
    def fake(**kwargs):
        return make_result(scores_by_text[kwargs["resume_text"]])

    resumes = [{"name": f"Candidate {text}", "text": text} for text in scores_by_text]
    with patch.object(ResumeAnalyzer, "analyze_resume", side_effect=fake) as mock:
        results = analyzer.analyze_multiple_resumes("JD text", resumes, job_profile)
    return results, mock


def test_candidates_are_sorted_by_final_score_descending(analyzer, job_profile):
    results, _ = rank(analyzer, job_profile, {"a": 55.0, "b": 82.5, "c": 30.0, "d": 70.1})
    assert [r["final_score"] for r in results] == [82.5, 70.1, 55.0, 30.0]


def test_ranks_start_at_one_and_follow_the_order(analyzer, job_profile):
    results, _ = rank(analyzer, job_profile, {"a": 55.0, "b": 82.5, "c": 30.0})
    assert [r["rank"] for r in results] == [1, 2, 3]
    assert [r["candidate_name"] for r in results] == ["Candidate b", "Candidate a", "Candidate c"]


def test_tied_scores_still_get_distinct_ranks(analyzer, job_profile):
    results, _ = rank(analyzer, job_profile, {"a": 60.0, "b": 60.0, "c": 40.0})
    assert sorted(r["rank"] for r in results) == [1, 2, 3]
    assert results[2]["candidate_name"] == "Candidate c"


def test_single_candidate_gets_rank_one(analyzer, job_profile):
    results, _ = rank(analyzer, job_profile, {"only": 47.0})
    assert len(results) == 1
    assert results[0]["rank"] == 1


def test_empty_resume_list_returns_empty_list(analyzer, job_profile):
    results = analyzer.analyze_multiple_resumes("JD text", [], job_profile)
    assert results == []


def test_candidate_name_comes_from_the_resume_entry(analyzer, job_profile):
    results, _ = rank(analyzer, job_profile, {"x": 50.0})
    assert results[0]["candidate_name"] == "Candidate x"


def test_job_profile_values_are_passed_to_every_analysis(analyzer, job_profile):
    _, mock = rank(analyzer, job_profile, {"a": 50.0, "b": 60.0})
    assert mock.call_count == 2
    for call in mock.call_args_list:
        assert call.kwargs["job_description"] == "JD text"
        assert call.kwargs["required_skills"] == ["Python", "Git"]
        assert call.kwargs["preferred_skills"] == ["React"]
        assert call.kwargs["required_experience_years"] == 2


def test_each_resume_is_analysed_with_its_own_text(analyzer, job_profile):
    _, mock = rank(analyzer, job_profile, {"first": 50.0, "second": 60.0})
    texts = [call.kwargs["resume_text"] for call in mock.call_args_list]
    assert texts == ["first", "second"]
