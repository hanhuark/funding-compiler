from __future__ import annotations

import argparse
from pathlib import Path

from funding_compiler.loaders import load_faculty, load_opportunities
from funding_compiler.matching import match_opportunities
from funding_compiler.reports import write_match_report
from funding_compiler.sources import load_funding_sources, sources_by_category


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="funding-compiler")
    subparsers = parser.add_subparsers(dest="command", required=True)

    demo_parser = subparsers.add_parser("demo", help="Run the sample matching workflow.")
    demo_parser.add_argument("--output", default="outputs/demo-report.md")

    match_parser = subparsers.add_parser("match", help="Match opportunities to faculty profiles.")
    match_parser.add_argument("--opportunities", required=True)
    match_parser.add_argument("--faculty", required=True)
    match_parser.add_argument("--output", required=True)
    match_parser.add_argument("--min-score", type=float, default=0.1)

    sources_parser = subparsers.add_parser("sources", help="List curated funding source portals.")
    sources_parser.add_argument("--registry", default="data/funding_sources.yaml")

    args = parser.parse_args(argv)
    if args.command == "demo":
        root = Path(__file__).resolve().parents[2]
        return _run_match(
            root / "examples" / "opportunities.csv",
            root / "examples" / "faculty.csv",
            Path(args.output),
            min_score=0.1,
        )
    if args.command == "match":
        return _run_match(
            Path(args.opportunities),
            Path(args.faculty),
            Path(args.output),
            min_score=args.min_score,
        )
    if args.command == "sources":
        sources = load_funding_sources(args.registry)
        for category, records in sources_by_category(sources).items():
            print(f"{category}:")
            for source in records:
                print(f"  - {source.name} ({source.url})")
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


def _run_match(opportunities_path: Path, faculty_path: Path, output_path: Path, min_score: float) -> int:
    opportunities = load_opportunities(opportunities_path)
    faculty = load_faculty(faculty_path)
    matches = match_opportunities(opportunities, faculty, min_score=min_score)
    write_match_report(output_path, opportunities, matches)
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
