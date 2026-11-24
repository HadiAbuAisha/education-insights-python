"""Produce a self-contained report and four charts, without network calls."""
from pathlib import Path
from html import escape
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from .analysis import summarize


def plot_report(frame: pd.DataFrame, out_dir: str | Path, passing_score: float = 60) -> Path:
    folder = Path(out_dir)
    folder.mkdir(parents=True, exist_ok=True)
    summary = summarize(frame, passing_score)
    by_course = summary["by_course"]
    by_cohort = summary["by_cohort"]

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.barh(by_course["course"], by_course["average_score"])
    ax.set(xlim=(0, 100), xlabel="Average score / 100", title="Average performance by course")
    ax.invert_yaxis(); fig.tight_layout(); fig.savefig(folder / "course_scores.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(frame["final_score"], bins=12, edgecolor="white")
    ax.axvline(passing_score, linestyle="--", label=f"Pass threshold ({passing_score:g})")
    ax.set(xlabel="Final score / 100", ylabel="Number of records", title="Distribution of final scores")
    ax.legend(); fig.tight_layout(); fig.savefig(folder / "score_distribution.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.scatter(frame["attendance_pct"], frame["final_score"], alpha=0.38, s=22)
    ax.set(xlabel="Attendance (%)", ylabel="Final score / 100", xlim=(30, 105), ylim=(0, 105),
           title="Attendance and score (descriptive, not causal)")
    fig.tight_layout(); fig.savefig(folder / "attendance_vs_score.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(by_cohort["cohort"].astype(str), by_cohort["pass_rate"] * 100)
    ax.set(ylim=(0, 100), xlabel="Cohort", ylabel="Pass rate (%)", title="Pass rate by cohort")
    fig.tight_layout(); fig.savefig(folder / "cohort_pass_rates.png", dpi=150); plt.close(fig)

    by_course.to_csv(folder / "course_summary.csv", index=False)
    by_cohort.to_csv(folder / "cohort_summary.csv", index=False)
    rows = "".join(
        f"<tr><td>{escape(str(r.course))}</td><td>{int(r.learners)}</td>"
        f"<td>{r.average_score:.1f}</td><td>{r.pass_rate*100:.1f}%</td></tr>"
        for r in by_course.itertuples())
    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Education Insights | Synthetic Data</title><style>
:root{{--ink:#17233c;--light:#eff4fa;--primary:#2463eb}}
*{{box-sizing:border-box}}body{{margin:0;background:#f5f7fb;color:var(--ink);font:16px system-ui,sans-serif}}
header{{background:#142447;color:white;padding:52px max(20px,calc((100vw - 1050px)/2))}}
header p{{color:#b6c8e3;max-width:60ch}} main{{max-width:1050px;margin:auto;padding:25px 20px 70px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:16px;margin-top:-52px}}
.card,.panel{{background:white;border-radius:16px;padding:22px;box-shadow:0 6px 22px #14244712}}
.value{{font-size:32px;font-weight:800;margin:6px 0}} .hint{{font-size:13px;color:#54657e}}
.charts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:18px;margin:25px 0}}
img{{width:100%;height:auto}}table{{width:100%;border-collapse:collapse}}th,td{{padding:12px;border-bottom:1px solid #e8edf5;text-align:left}}th{{background:#edf3ff}}
footer{{color:#52617c;font-size:13px;padding-top:25px}}@media(max-width:500px){{.charts{{grid-template-columns:1fr}}}}
</style></head><body>
<header><h1>Education Insights</h1><p>Open, reproducible analysis of <strong>fictional student records</strong>. Not a real institution's data.</p></header>
<main><div class="cards">
<div class="card"><div>Records</div><div class="value">{summary['records']}</div><div class="hint">Synthetic examples</div></div>
<div class="card"><div>Courses</div><div class="value">{summary['courses']}</div><div class="hint">Distinct course names</div></div>
<div class="card"><div>Mean score</div><div class="value">{summary['average_score']:.1f}</div><div class="hint">Out of 100</div></div>
<div class="card"><div>Pass rate</div><div class="value">{summary['pass_rate']:.1f}%</div><div class="hint">Threshold: {summary['passing_score']:g}</div></div>
</div><div class="charts">
<div class="panel"><img src="course_scores.png" alt="Average score by course"></div>
<div class="panel"><img src="score_distribution.png" alt="Distribution of final scores"></div>
<div class="panel"><img src="attendance_vs_score.png" alt="Attendance score scatter plot"></div>
<div class="panel"><img src="cohort_pass_rates.png" alt="Pass rates by cohort"></div>
</div><div class="panel"><h2>Course summary</h2><div style="overflow-x:auto"><table><thead><tr><th>Course</th><th>Records</th><th>Mean score</th><th>Pass rate</th></tr></thead><tbody>{rows}</tbody></table></div></div>
<footer>Generated with Python, pandas and matplotlib · Data is synthetic · Observed relationships do not establish causality.</footer></main></body></html>"""
    report = folder / "index.html"
    report.write_text(html, encoding="utf-8")
    return report
