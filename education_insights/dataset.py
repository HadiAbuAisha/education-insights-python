"""Create strictly synthetic assessment records for a repeatable demo."""
from pathlib import Path
import random
import csv

COURSES = ["Algorithms", "Databases", "Web Development", "Programming", "Statistics", "Networks"]
COHORTS = ["2023", "2024", "2025"]


def generate(path: str | Path, n: int = 360, seed: int = 42) -> Path:
    if n < 1:
        raise ValueError("n must be positive")
    rng = random.Random(seed)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["record_id", "cohort", "course", "attendance_pct", "assignment_pct", "exam_pct", "final_score"])
        for i in range(n):
            cohort = rng.choice(COHORTS)
            course = rng.choice(COURSES)
            attendance = round(min(100, max(35, rng.gauss(82, 13))), 1)
            assignment = round(min(100, max(10, rng.gauss(72 + (attendance - 80) * 0.30, 17))), 1)
            exam = round(min(100, max(5, rng.gauss(69 + (attendance - 80) * 0.42, 19))), 1)
            final = round(0.30 * assignment + 0.70 * exam, 1)
            writer.writerow([f"DEMO-{i+1:04d}", cohort, course, attendance, assignment, exam, final])
    return target
