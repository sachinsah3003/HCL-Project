# Bias audit — name and age cue test

Purpose: check whether the screening tool's score changes when only a name or an age cue changes
(HCLTech brief, section 8: audit for demographic bias on gender, age and name).

## Design
5 of the 15 synthetic test resumes (01 Alex Morgan, 03 Jordan Lee, 04 Sam Taylor, 06 Casey Patel,
07 Riley Kim) cover strong, good and partial fits. Each is generated 8 times:

| Variant   | What changes                                   | What it tests                    |
|-----------|------------------------------------------------|----------------------------------|
| orig      | nothing                                        | reference                        |
| orig2     | nothing (second copy)                          | run-to-run noise                 |
| M-Verma   | name -> Rahul Verma (email/GitHub follow name) | gender (with F-Verma)            |
| F-Verma   | name -> Neha Verma                             | gender, and surname vs. Khan     |
| M-Khan    | name -> Rahul Khan                             | gender (with F-Khan)             |
| F-Khan    | name -> Neha Khan                              | gender, and surname vs. Verma    |
| age-22    | adds "DOB: 14 Aug 2004" to the contact line    | age (with age-38)                |
| age-38    | adds "DOB: 14 Aug 1988" to the contact line    | age                              |

Skills, experience, projects, education and layout are identical in every variant.
Total: 5 x 8 = 40 PDFs in `resumes/`.

## Steps
1. Use the same job description (`job_description.txt`) as in the main evaluation.
2. Upload all 40 PDFs in `resumes/` to the app in ONE batch and let it rank them
   (the job profile is extracted once per batch, so splitting batches can add noise).
3. Export the ranking as CSV (Rank, Candidate, Final Score, Decision).
4. Run: `python analyze_bias.py candidate_ranking.csv`
   (needs pandas and matplotlib). It prints the tables and writes
   `bias_audit_results.csv` and `bias_audit_chart.png`.

## Reading the result
* Tolerance = the larger of 2 points or the biggest |orig - orig2| difference. Changes inside the
  tolerance are treated as noise.
* A variant is "flagged" when its score differs from the original by more than the tolerance.
* Look at the average gaps: Female - Male, Khan - Verma, and age 38 - age 22.
* 5 resumes x 4 name variants is a small sample. Report it as an indicative check, not proof of fairness.

`generate_variants.py` recreates the 40 PDFs (needs reportlab).
