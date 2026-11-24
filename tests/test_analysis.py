import pytest
from education_insights.dataset import generate
from education_insights.analysis import DataValidationError, load_records, summarize
from education_insights.report import plot_report


def test_repeatable_generation(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    generate(a, n=20, seed=11); generate(b, n=20, seed=11)
    assert a.read_bytes() == b.read_bytes()


def test_summary_and_files(tmp_path):
    path = generate(tmp_path / "demo.csv", n=25)
    records = load_records(path)
    result = summarize(records)
    assert result["records"] == 25
    assert 0 <= result["pass_rate"] <= 100
    report = plot_report(records, tmp_path / "out")
    assert report.exists()
    assert (tmp_path / "out" / "course_scores.png").exists()


def test_invalid_scores_rejected(tmp_path):
    path = generate(tmp_path / "bad.csv", n=2)
    path.write_text(path.read_text().replace("DEMO-0001", "DEMO-0002"), encoding="utf-8")
    with pytest.raises(DataValidationError, match="Duplicate"):
        load_records(path)


def test_bad_threshold(tmp_path):
    frame = load_records(generate(tmp_path / "d.csv", n=2))
    with pytest.raises(ValueError, match="Passing"):
        summarize(frame, 110)
