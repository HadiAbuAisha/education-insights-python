"""Command-line entry point."""
import argparse
from pathlib import Path
from .dataset import generate
from .analysis import load_records, summarize
from .report import plot_report


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Synthetic education analytics dashboard")
    parser.add_argument("--data", default="sample_data/synthetic_student_records.csv", help="Input CSV file")
    parser.add_argument("--out", default="reports", help="Output folder")
    parser.add_argument("--generate", action="store_true", help="Regenerate synthetic data before analysis")
    parser.add_argument("--count", type=int, default=360)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--pass-mark", type=float, default=60)
    args = parser.parse_args(argv)
    path = Path(args.data)
    if args.generate or not path.exists():
        generate(path, args.count, args.seed)
    frame = load_records(path)
    summary = summarize(frame, args.pass_mark)
    report = plot_report(frame, args.out, args.pass_mark)
    print(f"Analyzed {summary['records']} synthetic records across {summary['courses']} courses")
    print(f"Average score: {summary['average_score']:.1f}/100 · pass rate: {summary['pass_rate']:.1f}%")
    print(f"Open locally: {report.resolve()}")

if __name__ == "__main__":
    main()
