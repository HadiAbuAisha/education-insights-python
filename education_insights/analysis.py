"""Schema validation, summary statistics and a transparent pass-rate definition."""
from pathlib import Path
import pandas as pd

COLUMNS = ["record_id", "cohort", "course", "attendance_pct", "assignment_pct", "exam_pct", "final_score"]
NUMERIC = ["attendance_pct", "assignment_pct", "exam_pct", "final_score"]


class DataValidationError(ValueError):
    pass


def load_records(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    missing = set(COLUMNS) - set(frame.columns)
    if missing:
        raise DataValidationError("Missing columns: " + ", ".join(sorted(missing)))
    frame = frame[COLUMNS].copy()
    if frame.isna().any().any():
        raise DataValidationError("Missing values are not allowed in this demo")
    if frame["record_id"].duplicated().any():
        raise DataValidationError("Duplicate record IDs")
    for col in NUMERIC:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
        if frame[col].isna().any() or not frame[col].between(0, 100).all():
            raise DataValidationError(f"{col} must be a number from 0 to 100")
    if frame.empty:
        raise DataValidationError("Dataset must not be empty")
    if (frame["cohort"].astype(str).str.strip() == "").any() or (frame["course"].astype(str).str.strip() == "").any():
        raise DataValidationError("cohort and course must not be empty")
    return frame


def summarize(frame: pd.DataFrame, passing_score: float = 60) -> dict:
    if not (0 <= passing_score <= 100):
        raise ValueError("Passing score must be between 0 and 100")
    with_pass = frame.assign(passed=frame["final_score"] >= passing_score)
    by_course = (with_pass.groupby("course", as_index=False)
                 .agg(learners=("record_id", "size"), average_score=("final_score", "mean"),
                      pass_rate=("passed", "mean"))
                 .sort_values("average_score", ascending=False))
    by_cohort = (with_pass.groupby("cohort", as_index=False)
                 .agg(learners=("record_id", "size"), average_score=("final_score", "mean"),
                      pass_rate=("passed", "mean")).sort_values("cohort"))
    return {
        "records": int(len(frame)),
        "courses": int(frame["course"].nunique()),
        "average_score": round(float(frame["final_score"].mean()), 1),
        "median_score": round(float(frame["final_score"].median()), 1),
        "pass_rate": round(float(with_pass["passed"].mean() * 100), 1),
        "passing_score": passing_score,
        "by_course": by_course,
        "by_cohort": by_cohort,
    }
