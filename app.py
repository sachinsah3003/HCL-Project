import streamlit as st
import pandas as pd
import os

from src.analysis.resume_analyzer import ResumeAnalyzer
from src.analysis.llm_extractor import (
    extract_job_profile,
    generate_candidate_summary,
)
from src.parsers.pdf_extractor import extract_text_from_pdf
from src.matching.skill_extractor import extract_skills, load_skills

@st.cache_data
def get_skills_database():
    return load_skills("data/skills.txt")


@st.cache_data
def get_job_profile(job_description):
    return extract_job_profile(job_description)

skills_database = get_skills_database()

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "analysis_resume_texts" not in st.session_state:
    st.session_state.analysis_resume_texts = {}
if "analysis_job_description" not in st.session_state:
    st.session_state.analysis_job_description = ""

st.set_page_config(
    page_title="Smart Resume Screening Tool",
    page_icon="📄",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --bg: #F4F6F9;
        --surface: #FFFFFF;
        --border: #E3E7ED;
        --table-border: #C7CEDA;
        --text-primary: #1A2333;
        --text-secondary: #667085;
        --accent: #2D6A4F;
        --accent-dark: #17402E;
        --accent-light: #E7F3ED;
        --success: #2D6A4F;
        --success-bg: #E7F3ED;
        --warn: #92700C;
        --warn-bg: #FBF3D9;
        --danger: #B0281F;
        --danger-bg: #FBEAE8;
        --gold: #C9A227;
    }

    html, body, [class*="css"], .stMarkdown, p, span, label, div {
        font-family: 'Inter', sans-serif;
    }

    .stApp { background: var(--bg); }

    .stApp .block-container,
    .main .block-container {
        min-height: calc(100vh - 4rem);
        display: flex;
        flex-direction: column;
    }

    h1, h2, h3, h4 {
        font-family: 'Sora', sans-serif !important;
        color: var(--text-primary) !important;
    }

    #MainMenu, footer {visibility: hidden;}

    .hero {
        background: linear-gradient(135deg, var(--accent-dark) 0%, var(--accent) 100%);
        border-radius: 18px;
        padding: 2.25rem 2.5rem;
        margin-bottom: 1.75rem;
        box-shadow: 0 10px 30px rgba(23, 64, 46, 0.18);
    }
    .hero h1 {
        color: #FFFFFF !important;
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
    }
    .hero p {
        color: rgba(255,255,255,0.88);
        font-size: 1.02rem;
        max-width: 680px;
        margin: 0;
        line-height: 1.5;
    }
    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1.1rem;
    }
    .hero-pill {
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.35);
        color: #FFFFFF;
        padding: 0.32rem 0.85rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.01em;
    }

    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 0.25rem 0 1rem 0;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid var(--border);
    }
    .section-header .icon {
        font-size: 1.3rem;
    }
    .section-header .title {
        font-family: 'Sora', sans-serif;
        font-weight: 700;
        font-size: 1.25rem;
        color: var(--text-primary);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.03);
        margin-bottom: 1.4rem;
    }

    div.stButton > button {
        background: var(--accent);
        color: #FFFFFF;
        border: none;
        border-radius: 10px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        font-family: 'Inter', sans-serif;
        transition: all 0.15s ease;
    }
    div.stButton > button:hover {
        background: var(--accent-dark);
        color: #FFFFFF;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(45, 106, 79, 0.28);
    }
    div.stDownloadButton > button {
        background: var(--surface);
        color: var(--accent-dark);
        border: 1.5px solid var(--accent);
        border-radius: 10px;
        font-weight: 600;
        padding: 0.65rem 1.3rem;
    }
    div.stDownloadButton > button:hover {
        background: var(--accent-light);
    }

    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label {
        color: var(--text-primary) !important;
    }
    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] *,
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] *,
    [data-testid="stMetricDelta"],
    [data-testid="stMetricDelta"] * {
        color: var(--text-primary) !important;
        opacity: 1 !important;
    }
    .stRadio [data-testid="stMarkdownContainer"] p {
        color: var(--text-primary) !important;
    }

    .stTextArea textarea {
        border-radius: 10px !important;
        border: 1px solid var(--border) !important;
        background: var(--surface) !important;
        color: var(--text-primary) !important;
    }
    .stTextArea textarea::placeholder {
        color: var(--text-secondary) !important;
        opacity: 1 !important;
    }

    div[data-testid="stFileUploaderDropzone"] {
        border-radius: 10px !important;
        background: var(--surface) !important;
        border: 1.5px dashed var(--border) !important;
    }
    div[data-testid="stFileUploaderDropzone"] section,
    div[data-testid="stFileUploaderDropzone"] div,
    div[data-testid="stFileUploaderDropzone"] span,
    div[data-testid="stFileUploaderDropzone"] small {
        color: var(--text-primary) !important;
    }
    div[data-testid="stFileUploaderDropzone"] button {
        background: var(--accent) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
    }
    div[data-testid="stFileUploaderDropzone"] button:hover {
        background: var(--accent-dark) !important;
    }
    [data-testid="stFileUploaderFile"],
    [data-testid="stFileUploaderFile"] *,
    [data-testid="stFileUploaderFileName"] {
        color: var(--text-primary) !important;
    }

    /* ---------------- Expander (candidate cards) ---------------- */
    div[data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        background: var(--surface) !important;
        margin-bottom: 0.7rem;
        overflow: hidden;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] summary div {
        color: var(--text-primary) !important;
    }
    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        background: var(--surface) !important;
    }
    div[data-testid="stExpander"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-primary) !important;
    }

    /* ---------------- Ranking table ---------------- */
    .ranking-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.92rem;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid var(--table-border);
    }
    .ranking-table thead th {
        background: var(--accent-dark);
        color: #FFFFFF;
        text-align: left;
        padding: 0.75rem 1rem;
        font-family: 'Sora', sans-serif;
        font-weight: 600;
        font-size: 0.82rem;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        border-right: 1px solid rgba(255,255,255,0.18);
    }
    .ranking-table thead th:last-child {
        border-right: none;
    }
    .ranking-table tbody td {
        padding: 0.7rem 1rem;
        border-bottom: 1px solid var(--table-border);
        border-right: 1px solid var(--table-border);
        background: var(--surface);
        color: var(--text-primary);
    }
    .ranking-table tbody td:last-child {
        border-right: none;
    }
    .ranking-table tbody tr:last-child td {
        border-bottom: none;
    }
    .ranking-table tbody tr:nth-child(even) td {
        background: #F7F9FB;
    }
    .ranking-table tbody tr:hover td {
        background: var(--accent-light);
    }
    .decision-badge {
        display: inline-block;
        padding: 0.28rem 0.75rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    /* Animated Analyze Resumes loading state */
    .analyzing-status {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        padding: 0.8rem 1.5rem;
        background: #E7F3ED;
        color: #17402E;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        box-sizing: border-box;
    }
    .loading-spinner {
        width: 20px;
        height: 20px;
        border: 3px solid #B7D8C7;
        border-top-color: #2D6A4F;
        border-radius: 50%;
        animation: resume-spin 0.8s linear infinite;
        flex-shrink: 0;
    }
    @keyframes resume-spin {
        to { transform: rotate(360deg); }
    }

    .score-row {
        margin-bottom: 0.85rem;
    }
    .score-row .score-label-row {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-bottom: 0.3rem;
    }
    .score-track {
        background: #EBEEF3;
        border-radius: 999px;
        height: 9px;
        overflow: hidden;
    }
    .score-fill {
        height: 100%;
        border-radius: 999px;
    }

    .pill {
        display: inline-block;
        padding: 0.32rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem 0.35rem 0.2rem 0;
    }

    .site-footer {
        margin-top: auto;
        padding: 8rem 0 1rem;
        border-top: 1px solid var(--border);
        text-align: center;
        color: var(--text-secondary);
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def section_header(icon: str, title: str):
    st.markdown(
        f"""
        <div class="section-header">
            <span class="icon">{icon}</span>
            <span class="title">{title}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def decision_style(decision: str):
    mapping = {
        "Interview": ("#2D6A4F", "#E7F3ED"),  # Green
        "Consider": ("#2563EB", "#DBEAFE"),  # Blue
        "Review": ("#92700C", "#FBF3D9"),    # Yellow
        "Low Match": ("#B0281F", "#FBEAE8"), # Red
    }
    return mapping.get(decision, ("var(--text-secondary)", "#F0F1F4"))


def score_style(value: float):
    if value >= 80:
        return "var(--success)"
    if value >= 40:
        return "var(--warn)"
    return "var(--danger)"


def render_score_bar(label: str, value: float):
    color = score_style(value)
    pct = max(0, min(value, 100))
    st.markdown(
        f"""
        <div class="score-row">
            <div class="score-label-row">
                <span>{label}</span>
                <span style="font-weight:700; color:{color};">{value:.2f}%</span>
            </div>
            <div class="score-track">
                <div class="score-fill" style="width:{pct}%; background:{color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_skill_pills(skills, matched: bool):
    if not skills:
        st.markdown(
            "<span style='color:var(--text-secondary); font-size:0.85rem;'>None</span>",
            unsafe_allow_html=True,
        )
        return
    color = "var(--success)" if matched else "var(--danger)"
    bg = "var(--success-bg)" if matched else "var(--danger-bg)"
    icon = "✓" if matched else "✕"
    pills_html = "".join(
        f"<span class='pill' style='color:{color}; background:{bg};'>{icon} {skill}</span>"
        for skill in skills
    )
    st.markdown(pills_html, unsafe_allow_html=True)


# --------------------------------------------------
# Hero
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>📄 AI-Based Resume Screening and Candidate Shortlisting System</h1>
        <p>
            Automatically analyze and rank multiple resumes against a job description using
            AI, semantic embeddings, Gemini-powered profile extraction, evidence-based skill
            matching, and transparent weighted scoring.
            Built to help recruiters quickly identify the most relevant candidates with a
            clear and efficient screening process.
        </p>
        <div class="hero-pills">
            <span class="hero-pill">🧠 Semantic Embeddings</span>
            <span class="hero-pill">✨ Gemini Profile Extraction</span>
            <span class="hero-pill">🎯 Required &amp; Preferred Skills</span>
            <span class="hero-pill">📊 Weighted Scoring</span>
            <span class="hero-pill">🏆 Candidate Ranking</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        "<div style='font-family:Sora,sans-serif; font-weight:700; font-size:1.05rem; "
        "color:var(--text-color); margin-bottom:0.5rem;'>⚙️ How It Works</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="font-size:0.88rem; color:var(--text-secondary); line-height:1.7;">
        1. Provide the Job Description (paste or upload a PDF)<br>
        2. Upload one or more candidate resumes (PDF)<br>
        3. Click <b>Analyze Resumes</b><br>
        4. Review rankings, scores, and skill gaps<br>
        5. Download the ranking report as CSV
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='border-color:var(--border);'>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size:0.8rem; color:var(--text-secondary); line-height:1.6;">
        <b>Score legend</b><br>
        🟢 80%+ &nbsp;Interview<br>
        🔵 60–79% Consider<br>
        🟡 40–59% Review<br>
        🔴 &lt;40% Low Match
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# Job Description Section
# --------------------------------------------------

with st.container(border=True):
    section_header("📋", "Job Description")

    input_method = st.radio(
        "Choose Job Description Input Method",
        (
            "Paste Job Description",
            "Upload JD PDF",
        ),
    )

    job_description = ""
    uploaded_jd_pdf = None
    required_skills = []
    preferred_skills = []

    if input_method == "Paste Job Description":

        job_description = st.text_area(
            "Paste Job Description",
            height=250,
        )

    else:

        uploaded_jd_pdf = st.file_uploader(
            "Upload Job Description PDF",
            type=["pdf"],
        )
        if uploaded_jd_pdf:
            job_description = extract_text_from_pdf(uploaded_jd_pdf)
    
    # Extract skills only if a JD is available
    if job_description.strip():

        job_profile = get_job_profile(job_description)
        required_skills = job_profile.required_skills or extract_skills(
            job_description,
            skills_database,
        )
        preferred_skills = job_profile.preferred_skills

        if required_skills:

            st.markdown("#### 📋 Extracted Required Skills")

            skill_badges = " ".join(
                f"`🟢 {skill}`" for skill in required_skills
            )

            st.markdown(skill_badges)

        else:

            st.info(
                "No technical skills were detected in the Job Description."
            )

        if preferred_skills:
            st.markdown("#### ⭐ Preferred Skills")

            preferred_skill_badges = " ".join(
                f"`🔵 {skill}`" for skill in preferred_skills
            )

            st.markdown(preferred_skill_badges)
# --------------------------------------------------
# Resume Upload
# --------------------------------------------------

with st.container(border=True):
    section_header("📁", "Upload Resume(s)")

    uploaded_resumes = st.file_uploader(
        "Upload One or More PDF Resumes",
        type=["pdf"],
        accept_multiple_files=True,
    )

# --------------------------------------------------
# Analyze Button
# --------------------------------------------------

# Keep a placeholder so the button can be replaced by a loading animation
# immediately after it is clicked.
analyze_button_placeholder = st.empty()
analyze_button = analyze_button_placeholder.button(
    "🚀 Analyze Resumes",
    use_container_width=True,
    key="analyze_resumes",
)


if analyze_button or st.session_state.analysis_results:

    # -----------------------------
    # Validate Job Description
    # -----------------------------
    analyzer = ResumeAnalyzer("data/skills.txt")

    if not job_description.strip():
        st.error("Please provide a Job Description.")
        st.stop()

    # -----------------------------
    # Validate Resume Upload
    # -----------------------------
    if not uploaded_resumes:
        st.error("Please upload at least one resume.")
        st.stop()

    resumes = []

    for uploaded_resume in uploaded_resumes:

        resume_text = extract_text_from_pdf(uploaded_resume)

        if not resume_text.strip():
            st.warning(
                f"No readable text found in '{uploaded_resume.name}'. "
                "The PDF may be scanned or image-based."
            )
            continue

        candidate_name = os.path.splitext(uploaded_resume.name)[0]
        candidate_name = candidate_name.replace("_", " ")

        resumes.append(
            {
                "name": candidate_name,
                "text": resume_text,
            }
        )
    if not resumes:
        st.error("No valid resumes could be analyzed.")
        st.stop()

    if analyze_button:
        # Replace the clicked button with an animated status indicator.
        analyze_button_placeholder.markdown(
            """
            <div class="analyzing-status">
                <div class="loading-spinner"></div>
                <span>Analyzing Resumes...</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.spinner(
            "Extracting candidate profiles and matching skills..."
        ):
            results = analyzer.analyze_multiple_resumes(
                job_description,
                resumes,
                job_profile,
            )

        st.session_state.analysis_results = results
        st.session_state.analysis_job_description = job_description
        st.session_state.analysis_resume_texts = {
            resume["name"]: resume["text"]
            for resume in resumes
        }
        analyze_button_placeholder.success("✅ Analysis Completed Successfully!")
    else:
        results = st.session_state.analysis_results

    ranking_data = []

    for candidate in results:

        rank = candidate["rank"]

        if rank == 1:
            rank_display = "🥇 1"
        elif rank == 2:
            rank_display = "🥈 2"
        elif rank == 3:
            rank_display = "🥉 3"
        else:
            rank_display = str(rank)

        score = candidate["final_score"]

        if score >= 80:
            decision = "Interview"
        elif score >= 60:
            decision = "Consider"
        elif score >= 40:
            decision = "Review"
        else:
            decision = "Low Match"

        ranking_data.append(
            {
                "Rank": rank_display,
                "Candidate": candidate["candidate_name"],
                "Final Score": f'{candidate["final_score"]:.2f}%',
                "Decision": decision,
            }
        )

    ranking_df = pd.DataFrame(ranking_data)

    csv = ranking_df.to_csv(index=False).encode("utf-8")

    with st.container(border=True):
        section_header("🏆", "Candidate Ranking")

        st.download_button(
            label="📥 Download Ranking Report",
            data=csv,
            file_name="candidate_ranking.csv",
            mime="text/csv",
        )

        st.write("")

        # Custom styled ranking table (built from the same ranking_data used for CSV export).
        row_html_parts = []
        for row in ranking_data:
            color, bg = decision_style(row["Decision"])
            row_html_parts.append(
                "<tr>"
                f"<td>{row['Rank']}</td>"
                f"<td>{row['Candidate']}</td>"
                f"<td>{row['Final Score']}</td>"
                f"<td><span class=\"decision-badge\" style=\"color:{color}; background:{bg};\">{row['Decision']}</span></td>"
                "</tr>"
            )
        table_rows = "".join(row_html_parts)

        table_html = (
            "<table class=\"ranking-table\">"
            "<thead><tr><th>Rank</th><th>Candidate</th><th>Final Score</th><th>Decision</th></tr></thead>"
            f"<tbody>{table_rows}</tbody>"
            "</table>"
        )

        st.markdown(table_html, unsafe_allow_html=True)

    with st.container(border=True):
        section_header("📋", "Candidate Details")

        for candidate in results:

            rank = candidate["rank"]

            if rank == 1:
                icon = "🥇"
            elif rank == 2:
                icon = "🥈"
            elif rank == 3:
                icon = "🥉"
            else:
                icon = "👤"

            with st.expander(
                f"{icon} Rank #{rank} - {candidate['candidate_name']}",
                expanded=False,
            ):

                # AI-generated candidate summary
                st.markdown("### 🤖 AI Candidate Summary")

                summary = candidate.get("candidate_summary")

                if not summary:
                    if st.button(
                        "Generate AI Summary",
                        key=f"generate_summary_{rank}_{candidate['candidate_name']}",
                    ):
                        resume_text = st.session_state.analysis_resume_texts.get(
                            candidate["candidate_name"],
                        )

                        if resume_text is None:
                            st.error("Original resume text is unavailable.")
                        else:
                            try:
                                with st.spinner("Generating candidate summary..."):
                                    candidate["candidate_summary"] = (
                                        generate_candidate_summary(
                                            resume_text=resume_text,
                                            job_description=(
                                                st.session_state.analysis_job_description
                                            ),
                                            required_skills=candidate.get(
                                                "required_skills",
                                                [],
                                            ),
                                            matched_skills=candidate.get(
                                                "matched_skills",
                                                [],
                                            ),
                                            missing_skills=candidate.get(
                                                "missing_skills",
                                                [],
                                            ),
                                        )
                                    )
                            except Exception as exc:
                                print(
                                    f"Summary generation failed for "
                                    f"{candidate['candidate_name']}: {exc}"
                                )
                                candidate["candidate_summary"] = (
                                    "Candidate summary is temporarily unavailable."
                                )

                            st.session_state.analysis_results = results
                            st.rerun()

                if summary:
                    st.write(summary)

                st.divider()

                col1, col2, col3 = st.columns(3)

                with col1:
                    render_score_bar("Final Score", candidate["final_score"])
                with col2:
                    render_score_bar("JD Similarity", candidate["jd_similarity_score"])
                with col3:
                    render_score_bar("Skills Match", candidate["skills_match_score"])

                st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

                left, right = st.columns(2)

                with left:
                    st.markdown("**✅ Matched Skills**")
                    render_skill_pills(candidate["matched_skills"], matched=True)

                with right:
                    st.markdown("**❌ Missing Skills**")
                    render_skill_pills(candidate["missing_skills"], matched=False)

                matched_groups = candidate.get("matched_required_groups", [])
                missing_groups = candidate.get("missing_required_groups", [])

                if matched_groups or missing_groups:
                    with st.expander(
                        "🔀 Alternative Requirements",
                        expanded=True,
                    ):
                        for group_result in matched_groups:
                            alternatives = group_result["alternatives"]
                            matched_alternatives = group_result[
                                "matched_alternatives"
                            ]

                            st.success(
                                f"✓ Satisfied: {' OR '.join(alternatives)} "
                                f"(matched: {', '.join(matched_alternatives)})"
                            )

                        for group_result in missing_groups:
                            alternatives = group_result["alternatives"]

                            st.error(
                                f"✗ Not satisfied: {' OR '.join(alternatives)}"
                            )

                with st.expander("⭐ Preferred Skills", expanded=False):
                    preferred_skills = candidate.get("preferred_skills", [])
                    matched_preferred_skills = candidate.get(
                        "matched_preferred_skills",
                        [],
                    )
                    missing_preferred_skills = candidate.get(
                        "missing_preferred_skills",
                        [],
                    )

                    matched_groups = candidate.get("matched_preferred_groups", [])
                    missing_groups = candidate.get("missing_preferred_groups", [])

                    # Count each individual skill and each alternative group once.
                    total_preferred = (
                        len(preferred_skills)
                        + len(matched_groups)
                        + len(missing_groups)
                    )
                    matched_preferred = (
                        len(matched_preferred_skills)
                        + len(matched_groups)
                    )

                    st.markdown(
                        f"⭐ Preferred Requirements "
                        f"({matched_preferred}/{total_preferred} matched)"
                    )

                    if total_preferred == 0:
                        st.caption("No preferred requirements were identified.")
                    else:
                        if preferred_skills:
                            preferred_left, preferred_right = st.columns(2)

                            with preferred_left:
                                st.markdown("**✅ Matched Preferred Skills**")
                                render_skill_pills(
                                    matched_preferred_skills,
                                    matched=True,
                                )

                            with preferred_right:
                                st.markdown("**❌ Missing Preferred Skills**")
                                render_skill_pills(
                                    missing_preferred_skills,
                                    matched=False,
                                )

                        if matched_groups or missing_groups:
                            st.markdown("**Preferred Alternatives**")

                            for group in matched_groups:
                                alternatives = group["alternatives"]
                                matched_alternatives = group[
                                    "matched_alternatives"
                                ]

                                st.success(
                                    f"✓ Satisfied: {' OR '.join(alternatives)} "
                                    f"(matched: {', '.join(matched_alternatives)})"
                                )

                            for group in missing_groups:
                                alternatives = group["alternatives"]

                                st.error(
                                    f"✗ Not satisfied: {' OR '.join(alternatives)}"
                                )

                st.subheader("Experience Analysis")

                experience_years = candidate.get("candidate_experience_years")
                experience_score = candidate.get("experience_match_score")

                if experience_years is not None:
                    st.write(f"**Candidate experience:** {experience_years} years")
                else:
                    st.info("Candidate experience could not be determined.")

                if experience_score is not None:
                    st.metric("Experience Match", f"{experience_score:.1f}%")
                else:
                    st.caption("Experience was not included in the score.")

                st.subheader("Score Breakdown")

                score_col1, score_col2, score_col3 = st.columns(3)

                score_col1.metric(
                    "Semantic Similarity",
                    f"{candidate['jd_similarity_score']:.1f}%",
                )

                score_col2.metric(
                    "Skills Match",
                    f"{candidate['skills_match_score']:.1f}%",
                )

                if candidate.get("experience_match_score") is not None:
                    score_col3.metric(
                        "Experience Match",
                        f"{candidate['experience_match_score']:.1f}%",
                    )
                else:
                    score_col3.metric("Experience Match", "N/A")

                st.subheader("Skill Score Breakdown")

                required_score = candidate.get("required_skills_score")
                preferred_score = candidate.get("preferred_skills_score")
                skill_col1, skill_col2, skill_col3 = st.columns(3)

                skill_col1.metric(
                    "Required Skills",
                    f"{required_score:.1f}%"
                    if required_score is not None
                    else "N/A",
                )
                skill_col2.metric(
                    "Preferred Skills",
                    f"{preferred_score:.1f}%"
                    if preferred_score is not None
                    else "N/A",
                )
                skill_col3.metric(
                    "Overall Skills Match",
                    f"{candidate['skills_match_score']:.1f}%",
                )

                if required_score is not None and preferred_score is not None:
                    st.caption(
                        "Overall skills score = 80% required skills + "
                        "20% preferred skills."
                    )
                elif required_score is not None:
                    st.caption("Only required skills contribute to the skills score.")
                elif preferred_score is not None:
                    st.caption("Only preferred skills contribute to the skills score.")

                st.subheader("Education")

                education = candidate.get("candidate_education")
                education_in_progress = candidate.get(
                    "education_in_progress",
                    [],
                )

                if education:
                    st.write(f"**Completed education:** {education}")
                else:
                    st.write("Completed education: Not identified")

                if education_in_progress:
                    st.write(
                        "**Education in progress:** "
                        + ", ".join(education_in_progress)
                    )

st.markdown(
        """
    <div class="site-footer">
        Built with ❤️ by <b>Ashish Kumar Pal</b>
    </div>
        """,
        unsafe_allow_html=True,
)
