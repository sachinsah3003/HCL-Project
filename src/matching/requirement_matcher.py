import re


EDUCATION_LEVELS = {
    "phd": 4,
    "doctorate": 4,
    "master": 3,
    "bachelor": 2,
    "associate": 1,
}


def extract_experience_years(text):
    """Extract an explicitly stated number of experience years."""
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)"
        r"\s+(?:of\s+)?(?:relevant\s+)?experience",
        r"experience\s+(?:of\s+)?(\d+(?:\.\d+)?)\s*\+?"
        r"\s*(?:years?|yrs?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None


def extract_education_level(text):
    """Return the highest commonly recognized degree level found."""
    text = text.lower()

    patterns = [
        (4, r"\bph\.?d\.?\b|\bdoctorate\b"),
        (3, r"\bmaster'?s?\b|\bm\.?tech\b|\bm\.?e\.?\b|\bm\.?sc\b|\bmba\b"),
        (2, r"\bbachelor'?s?\b|\bb\.?tech\b|\bb\.?e\.?\b|\bb\.?sc\b|\bbca\b|\bbe\b"),
        (1, r"\bassociate'?s?\b"),
    ]

    for level, pattern in patterns:
        if re.search(pattern, text):
            return level

    return None


def compare_requirements(job_description, resume_text):
    required_years = extract_experience_years(job_description)
    candidate_years = extract_experience_years(resume_text)

    required_education = extract_education_level(job_description)
    candidate_education = extract_education_level(resume_text)

    if required_years is None:
        experience_status = "Not specified"
    elif candidate_years is None:
        experience_status = "Not found"
    elif candidate_years >= required_years:
        experience_status = "Meets requirement"
    else:
        experience_status = "Below requirement"

    if required_education is None:
        education_status = "Not specified"
    elif candidate_education is None:
        education_status = "Not found"
    elif candidate_education >= required_education:
        education_status = "Meets requirement"
    else:
        education_status = "Below requirement"

    return {
        "required_experience_years": required_years,
        "candidate_experience_years": candidate_years,
        "experience_match_status": experience_status,
        "required_education_level": required_education,
        "candidate_education_level": candidate_education,
        "education_match_status": education_status,
    }
