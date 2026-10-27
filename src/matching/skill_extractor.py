import re

from src.utils.helpers import normalize_text

def load_skills(skill_file):
    """
    Load skills from a text file.
    """

    skills = []

    with open(skill_file, "r", encoding="utf-8") as file:

        for line in file:

            skill = line.strip().lower()

            if skill:
                skills.append(skill)

    return skills

def extract_skills(job_description, skills_database):
    """
    Extract skills present in the job description.
    """

    job_description = normalize_text(job_description)

    extracted_skills = []

    for skill in skills_database:

        normalized_skill = normalize_text(skill)

        pattern = (
            r"(?<!\w)"
            + re.escape(normalized_skill)
            + r"(?!\w)"
        )

        if re.search(pattern, job_description):

            extracted_skills.append(skill)

    return extracted_skills