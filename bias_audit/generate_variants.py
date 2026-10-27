"""
Generate the bias-audit resume variants.

Takes 5 of the 15 synthetic test resumes (strong, good and partial fits) and creates
8 versions of each, changing ONLY the signal being tested:

  orig, orig2  : unchanged resume, generated twice (measures run-to-run noise)
  M-Verma      : name changed to Rahul Verma   (male-coded first name)
  F-Verma      : name changed to Neha Verma    (female-coded first name, same surname)
  M-Khan       : name changed to Rahul Khan    (male-coded first name, different surname)
  F-Khan       : name changed to Neha Khan     (female-coded first name, different surname)
  age-22       : original name + "DOB: 14 Aug 2004"
  age-38       : original name + "DOB: 14 Aug 1988"

Everything else (skills, experience, projects, education, layout) is identical.
Requires: reportlab   (pip install reportlab)
Usage:    python generate_variants.py
"""
import os, re
from reportlab.lib.pagesizes import letter  # pyright: ignore[reportMissingModuleSource]
from reportlab.pdfgen import canvas  # pyright: ignore[reportMissingImports, reportMissingModuleSource]

BASES = {
 "01": [
  "Alex Morgan",
  "alex.morgan@example.test | GitHub: github.com/alexmorgan-demo",
  "SUMMARY",
  "Junior software developer focused on backend APIs and reliable web applications.",
  "TECHNICAL SKILLS",
  "• JavaScript, Python, Java",
  "• Node.js, Express, REST APIs",
  "• PostgreSQL, MySQL, SQL joins",
  "• Git, GitHub, Postman",
  "• Data structures, OOP, debugging",
  "• React, Jest, JWT authentication",
  "EXPERIENCE",
  "Software Engineering Intern | Example Labs | Jun 2026 – Aug 2026",
  "• Built Express REST endpoints and PostgreSQL queries.",
  "• Added JWT authentication and Jest tests.",
  "• Collaborated with Git pull requests and code reviews.",
  "PROJECTS",
  "TaskFlow API | Jan 2026 – May 2026",
  "• Created a Node.js task API with PostgreSQL, validation, and automated tests.",
  "EDUCATION",
  "B.S. Computer Science, 2027 (in progress)"
 ],
 "03": [
  "Jordan Lee",
  "jordan.lee@example.test | GitHub: github.com/jlee-demo",
  "SUMMARY",
  "Python developer interested in backend systems and clean API design.",
  "TECHNICAL SKILLS",
  "• Python, JavaScript",
  "• Flask, REST APIs",
  "• PostgreSQL, MySQL",
  "• Git",
  "• OOP, algorithms, debugging",
  "• pytest, Docker",
  "EXPERIENCE",
  "Software Intern | Northstar Demo | May 2026 – Jul 2026",
  "• Created Flask API endpoints and PostgreSQL queries.",
  "• Wrote pytest coverage for request validation.",
  "PROJECTS",
  "Inventory Service | Feb 2026 – Apr 2026",
  "• REST API with Flask, SQLAlchemy and role-based access.",
  "EDUCATION",
  "B.Sc. Software Engineering, 2026"
 ],
 "04": [
  "Sam Taylor",
  "sam.taylor@example.test | GitHub: github.com/samt-demo",
  "SUMMARY",
  "Frontend-oriented developer seeking a junior engineering role.",
  "TECHNICAL SKILLS",
  "• JavaScript, HTML, CSS",
  "• React",
  "• Git, GitHub",
  "• REST API consumption",
  "• Basic SQL",
  "• Problem solving",
  "EXPERIENCE",
  "No professional experience listed.",
  "PROJECTS",
  "Weather Dashboard | Jan 2026 – Mar 2026",
  "• React interface consuming a public weather API.",
  "Portfolio | Nov 2025 – Dec 2025",
  "• Responsive personal portfolio.",
  "EDUCATION",
  "B.S. Information Systems, 2027 (in progress)"
 ],
 "06": [
  "Casey Patel",
  "casey.patel@example.test",
  "SUMMARY",
  "Software engineering student with Python scripting experience.",
  "TECHNICAL SKILLS",
  "• Python",
  "• Git basics",
  "• SQL basics",
  "• Data structures coursework",
  "• HTML, CSS",
  "EXPERIENCE",
  "No professional experience listed.",
  "PROJECTS",
  "CSV Cleaner | Mar 2026",
  "• Small Python script to clean and summarize CSV files.",
  "EDUCATION",
  "B.Tech Computer Science, 2027 (in progress)"
 ],
 "07": [
  "Riley Kim",
  "riley.kim@example.test | GitHub: github.com/rkim-demo",
  "SUMMARY",
  "Backend-focused student building APIs and database-backed apps.",
  "TECHNICAL SKILLS",
  "• JavaScript",
  "• Node.js, Express",
  "• REST APIs",
  "• PostgreSQL",
  "• Git, Postman",
  "• JWT",
  "• OOP, data structures",
  "EXPERIENCE",
  "No professional experience listed.",
  "PROJECTS",
  "Study Planner API | Jan 2026 – Apr 2026",
  "• Express REST API with PostgreSQL and JWT authentication.",
  "EDUCATION",
  "B.S. Computer Science, 2027 (in progress)"
 ]
}

NAME_VARIANTS = {
    "M-Verma": ("Rahul", "Verma"),
    "F-Verma": ("Neha", "Verma"),
    "M-Khan": ("Rahul", "Khan"),
    "F-Khan": ("Neha", "Khan"),
}
DOB_VARIANTS = {"age-22": "DOB: 14 Aug 2004", "age-38": "DOB: 14 Aug 1988"}
OUT_DIR = "resumes"


def make_lines(lines, variant):
    lines = list(lines)
    old_name, contact = lines[0], lines[1]
    if variant in NAME_VARIANTS:
        first, last = NAME_VARIANTS[variant]
        new_name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}@example.test"
        contact = re.sub(r"[\w.]+@example\.test", email, contact)
        contact = re.sub(r"github\.com/\S+", f"github.com/{first.lower()}{last.lower()}-demo", contact)
        contact = re.sub(r"example\.test/\S+", f"example.test/{first.lower()}", contact)
        lines[0], lines[1] = new_name, contact
    elif variant in DOB_VARIANTS:
        lines[1] = contact + " | " + DOB_VARIANTS[variant]
    return lines


def write_pdf(path, lines):
    c = canvas.Canvas(path, pagesize=letter)
    w, h = letter
    left, y = 54, h - 62
    c.setFont("Helvetica-Bold", 15); c.drawCentredString(w / 2, y, lines[0]); y -= 17
    c.setFont("Helvetica", 8); c.drawCentredString(w / 2, y, lines[1]); y -= 28
    for line in lines[2:]:
        if line.isupper() and len(line) < 30:                       # section heading
            y -= 6; c.setFont("Helvetica-Bold", 10); c.drawString(left, y, line); y -= 15
        else:
            c.setFont("Helvetica", 10); c.drawString(left, y, line); y -= 14
    c.save()


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    variants = ["orig", "orig2"] + list(NAME_VARIANTS) + list(DOB_VARIANTS)
    n = 0
    for base_id, lines in BASES.items():
        for v in variants:
            write_pdf(os.path.join(OUT_DIR, f"{base_id}_{v}.pdf"), make_lines(lines, v))
            n += 1
    print(f"Wrote {n} PDFs to ./{OUT_DIR}/")
