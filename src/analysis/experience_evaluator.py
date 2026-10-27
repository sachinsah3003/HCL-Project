from typing import Optional, Dict, Any


def evaluate_experience(
    required_years: Optional[float],
    candidate_years: Optional[float],
    experience_estimated: bool = False,
) -> Dict[str, Any]:

    if required_years is None:
        return {
            "experience_match_score": None,
            "experience_match_status": "Not required",
        }

    if candidate_years is None:
        return {
            "experience_match_score": None,
            "experience_match_status": "Unknown",
        }

    score = min(
        100.0,
        (candidate_years / required_years) * 100,
    ) if required_years > 0 else 100.0

    if experience_estimated:
        status = "Needs review"
    elif candidate_years >= required_years:
        status = "Meets requirement"
    else:
        status = "Below requirement"

    return {
        "experience_match_score": round(score, 2),
        "experience_match_status": status,
    }
