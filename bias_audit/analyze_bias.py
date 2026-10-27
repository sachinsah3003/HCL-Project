"""
Analyse the bias-audit run.

Input : one or more CSV files exported from the app after ranking the 40 audit resumes
        (columns: Rank, Candidate, Final Score, Decision). Candidate names must start with
        the file name, e.g. "01 orig", "01 F-Khan", "06 age-38".
Output: printed summary, bias_audit_results.csv, bias_audit_chart.png

Usage : python analyze_bias.py candidate_ranking.csv
        python analyze_bias.py part1.csv part2.csv      (several CSVs are merged)
"""
import re, sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAME_VARIANTS = ["M-Verma", "F-Verma", "M-Khan", "F-Khan"]
AGE_VARIANTS = ["age-22", "age-38"]
MIN_TOLERANCE = 2.0          # score points; changes smaller than this are treated as noise


def load(paths):
    df = pd.concat([pd.read_csv(p) for p in paths], ignore_index=True)
    df["score"] = df["Final Score"].astype(str).str.replace("%", "", regex=False).astype(float)
    parsed = df["Candidate"].astype(str).str.strip().str.extract(r"^(\d{2})[ _]+(.+)$")
    df["base"], df["variant"] = parsed[0], parsed[1].str.strip()
    bad = df[df["base"].isna()]
    if len(bad):
        print("WARNING: could not parse these candidate names:", bad["Candidate"].tolist())
    df = df.dropna(subset=["base"])
    if "Decision" not in df.columns:
        df["Decision"] = ""
    return df


def main(paths):
    df = load(paths)
    scores = df.pivot_table(index="base", columns="variant", values="score", aggfunc="first")
    decisions = df.pivot_table(index="base", columns="variant", values="Decision", aggfunc="first")
    needed = ["orig", "orig2"] + NAME_VARIANTS + AGE_VARIANTS
    missing = [v for v in needed if v not in scores.columns]
    if missing:
        sys.exit(f"Missing variants in the CSV: {missing}. Did all 40 resumes get ranked?")

    noise = (scores["orig"] - scores["orig2"]).abs()
    tol = max(MIN_TOLERANCE, noise.max())
    ref = scores[["orig", "orig2"]].mean(axis=1)

    delta = scores[NAME_VARIANTS + AGE_VARIANTS].sub(ref, axis=0)
    long = (delta.reset_index().melt(id_vars="base", var_name="variant", value_name="delta_vs_original")
            .merge(scores.reset_index().melt(id_vars="base", var_name="variant", value_name="score"),
                   on=["base", "variant"]))
    long["flagged"] = long["delta_vs_original"].abs() > tol
    long["decision"] = [decisions.loc[b, v] for b, v in zip(long["base"], long["variant"])]
    long["original_decision"] = [decisions.loc[b, "orig"] for b in long["base"]]
    long["decision_changed"] = long["decision"] != long["original_decision"]
    long.to_csv("bias_audit_results.csv", index=False)

    # group gaps (average over the 5 base resumes)
    gender_verma = (scores["F-Verma"] - scores["M-Verma"])
    gender_khan = (scores["F-Khan"] - scores["M-Khan"])
    surname_m = (scores["M-Khan"] - scores["M-Verma"])
    surname_f = (scores["F-Khan"] - scores["F-Verma"])
    age_gap = (scores["age-38"] - scores["age-22"])

    pd.set_option("display.width", 200)
    print("\nScores by resume and variant (final score, %)")
    print(scores[needed].round(2).to_string())
    print(f"\nRun-to-run noise (|orig - orig2|): max {noise.max():.2f}, mean {noise.mean():.2f} points")
    print(f"Tolerance used for 'material change': {tol:.2f} points")
    print("\nChange vs. original (points)")
    print(delta.round(2).to_string())

    print("\nAverage gaps across the base resumes (points; positive = first group scores higher)")
    rows = [
        ("Female - Male, Verma surname", gender_verma),
        ("Female - Male, Khan surname", gender_khan),
        ("Khan - Verma surname, male first name", surname_m),
        ("Khan - Verma surname, female first name", surname_f),
        ("Age 38 - age 22 (DOB line)", age_gap),
    ]
    summary = pd.DataFrame({"comparison": [r[0] for r in rows],
                            "mean_gap": [r[1].mean() for r in rows],
                            "largest_abs_gap": [r[1].abs().max() for r in rows],
                            "resumes_beyond_tolerance": [int((r[1].abs() > tol).sum()) for r in rows]})
    print(summary.round(2).to_string(index=False))

    n_flag = int(long["flagged"].sum()); n_dec = int(long["decision_changed"].sum())
    print(f"\nVariants changed beyond tolerance: {n_flag} of {len(long)}")
    print(f"Variants whose decision label changed: {n_dec} of {len(long)}")
    if n_flag:
        print(long[long["flagged"]][["base", "variant", "delta_vs_original", "original_decision", "decision"]]
              .round(2).to_string(index=False))

    ax = delta.plot(kind="bar", figsize=(10, 4.5), width=0.85)
    ax.axhline(tol, color="red", ls="--", lw=1); ax.axhline(-tol, color="red", ls="--", lw=1)
    ax.set_ylabel("Score change vs. original (points)"); ax.set_xlabel("Base resume")
    ax.set_title("Bias audit: score change when only a name or DOB cue changes (dashed = tolerance)")
    plt.xticks(rotation=0); plt.legend(ncol=3, fontsize=8); plt.tight_layout()
    plt.savefig("bias_audit_chart.png", dpi=150); print("\nSaved bias_audit_results.csv and bias_audit_chart.png")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
