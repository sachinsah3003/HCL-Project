import re

from src.utils.helpers import normalize_text


def parse_required_skills(skills_input):
    """
    Convert comma-separated skills input into a normalized list.
    """

    skills = skills_input.split(",")

    normalized_skills = []

    for skill in skills:
        normalized_skill = normalize_text(skill)

        if normalized_skill:
            normalized_skills.append(normalized_skill)

    return normalized_skills


from src.analysis.llm_extractor import match_skills_with_llm



def match_required_skills(
    resume_text,
    required_skills,
    preferred_skills=None,
    return_details=False,
):
    preferred_skills = preferred_skills or []

    def normalize_name(value):
        return " ".join(value.lower().split()).strip()

    def deduplicate(skills):
        result = []
        seen = set()

        for skill in skills:
            skill = skill.strip()
            key = normalize_name(skill)

            if key and key not in seen:
                result.append(skill)
                seen.add(key)

        return result

    required_skills = deduplicate(required_skills)
    preferred_skills = deduplicate(preferred_skills)

    required_names = {normalize_name(s) for s in required_skills}
    preferred_skills = [
        s for s in preferred_skills
        if normalize_name(s) not in required_names
    ]

    all_skills = deduplicate(required_skills + preferred_skills)

    if not all_skills:
        details = {
            "matched_required": [],
            "missing_required": [],
            "matched_preferred": [],
            "missing_preferred": [],
            "required_score": None,
            "preferred_score": None,
            "skills_score": 0.0,
        }
        if return_details:
            return details
        return [], [], 0.0

    response = match_skills_with_llm(resume_text, all_skills)

    skills_by_name = {normalize_name(s): s for s in all_skills}
    resume_normalized = normalize_name(resume_text)
    matched_names = set()

    for item in response.results:
        key = normalize_name(item.required_skill)

        if key not in skills_by_name:
            continue

        evidence = item.resume_evidence
        if not item.equivalent or not evidence:
            continue

        if normalize_name(evidence) not in resume_normalized:
            continue

        matched_names.add(key)

    matched_required = [
        s for s in required_skills if normalize_name(s) in matched_names
    ]
    missing_required = [
        s for s in required_skills if normalize_name(s) not in matched_names
    ]
    matched_preferred = [
        s for s in preferred_skills if normalize_name(s) in matched_names
    ]
    missing_preferred = [
        s for s in preferred_skills if normalize_name(s) not in matched_names
    ]

    required_score = (
        len(matched_required) / len(required_skills) * 100
        if required_skills else None
    )
    preferred_score = (
        len(matched_preferred) / len(preferred_skills) * 100
        if preferred_skills else None
    )

    if required_score is not None and preferred_score is not None:
        skills_score = 0.80 * required_score + 0.20 * preferred_score
    elif required_score is not None:
        skills_score = required_score
    elif preferred_score is not None:
        skills_score = preferred_score
    else:
        skills_score = 0.0

    details = {
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
        "required_score": round(required_score, 2) if required_score is not None else None,
        "preferred_score": round(preferred_score, 2) if preferred_score is not None else None,
        "skills_score": round(skills_score, 2),
    }

    if return_details:
        return details

    return matched_required + matched_preferred, missing_required, details["skills_score"]
