from src.parsers.pdf_extractor import extract_text_from_pdf
from src.analysis.resume_analyzer import ResumeAnalyzer
from src.analysis.llm_extractor import extract_job_profile


analyzer = ResumeAnalyzer("data/skills.txt")


job_description = extract_text_from_pdf(
    "sample_data/job_description.pdf"
)

resume = extract_text_from_pdf(
    "sample_data/ashish_resume.pdf"
)

job_profile = extract_job_profile(job_description)
required_skills = job_profile.required_skills
preferred_skills = job_profile.preferred_skills


result = analyzer.analyze_resume(
    job_description,
    resume,
    required_skills,
    preferred_skills=preferred_skills,
)


print(result)