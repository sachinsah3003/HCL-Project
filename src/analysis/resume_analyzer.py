from concurrent.futures import ThreadPoolExecutor

from src.utils.text_preprocessor import preprocess_text
from src.matching.semantic_similarity import calculate_semantic_similarity
from models.analysis_result import AnalysisResult
from src.analysis.experience_evaluator import evaluate_experience

from src.analysis.llm_extractor import (
    extract_resume_profile,
)

from src.matching.skill_extractor import (
    load_skills,
    extract_skills,
)

from src.matching.skill_matcher import (
    match_required_skills,
)


class ResumeAnalyzer:

    def __init__(self, skills_database_path):

        self.skills_database = load_skills(
            skills_database_path
        )

    
    def analyze_resume(
        self,
        job_description,
        resume_text,
        required_skills,
        required_experience_years=None,
        preferred_skills=None,
    ):
        similarity_score = calculate_semantic_similarity(
            job_description,
            resume_text,
        )

        with ThreadPoolExecutor(max_workers=2) as executor:
            skill_future = executor.submit(
                match_required_skills,
                resume_text,
                required_skills,
                preferred_skills,
                return_details=True,
            )

            profile_future = executor.submit(
                extract_resume_profile,
                resume_text,
            )

            skill_results = skill_future.result()
            profile = profile_future.result()

        matched_skills = skill_results["matched_required"]
        missing_skills = skill_results["missing_required"]
        skills_score = skill_results["skills_score"]

        experience_results = evaluate_experience(
            required_experience_years,
            profile.total_experience_years,
            profile.experience_estimated,
        )

        experience_score = experience_results["experience_match_score"]

        components = [
            (similarity_score, 0.30),
            (skills_score, 0.50),
        ]

        if experience_score is not None:
            components.append((experience_score, 0.20))

        total_weight = sum(weight for _, weight in components)
        final_score = sum(
            score * weight for score, weight in components
        ) / total_weight

        return {
            "jd_similarity_score": round(similarity_score, 2),
            "skills_match_score": round(skills_score, 2),
            "experience_match_score": experience_score,
            "final_score": round(final_score, 2),
            "required_skills": (
                skill_results["matched_required"]
                + skill_results["missing_required"]
            ),
            "preferred_skills": (
                skill_results["matched_preferred"]
                + skill_results["missing_preferred"]
            ),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "matched_preferred_skills": skill_results[
                "matched_preferred"
            ],
            "missing_preferred_skills": skill_results[
                "missing_preferred"
            ],
            "required_skills_score": skill_results["required_score"],
            "preferred_skills_score": skill_results["preferred_score"],
            "required_experience_years": required_experience_years,
            "candidate_experience_years": profile.total_experience_years,
            "candidate_education": profile.highest_completed_education,
            "education_in_progress": profile.education_in_progress,
            "experience_match_status": experience_results[
                "experience_match_status"
            ],
        }


    def analyze_multiple_resumes(
        self,
        job_description,
        resumes,
        job_profile,
    ):

        required_skills = job_profile.required_skills
        results = []

        for resume in resumes:
            result = self.analyze_resume(
                job_description=job_description,
                resume_text=resume["text"],
                required_skills=required_skills,
                required_experience_years=(
                    job_profile.minimum_experience_years
                ),
                preferred_skills=job_profile.preferred_skills,
            )

            result["candidate_name"] = resume["name"]

            validated_result = AnalysisResult(**result)
            results.append(validated_result.model_dump())

        results.sort(
            key=lambda candidate: candidate["final_score"],
            reverse=True,
        )

        for index, candidate in enumerate(results, start=1):
            candidate["rank"] = index

        return results
