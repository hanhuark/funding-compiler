from __future__ import annotations

import csv
import html
from collections import defaultdict
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from funding_compiler.loaders import load_faculty, load_opportunities
from funding_compiler.matching import match_opportunities


SNAPSHOT_DATE = date(2026, 6, 11)
SCREENING_DIR = Path("data/screenings/2026-06-11")
DOCS_DIR = Path("docs/screenings/2026-06-11")
SITE_DIR = Path("site/screenings")


def main() -> int:
    opportunities = load_opportunities(SCREENING_DIR / "opportunities.csv")
    faculty = load_faculty(SCREENING_DIR / "faculty_profiles.csv")
    matches = match_opportunities(opportunities, faculty, min_score=0.1)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    write_alignment_csv(DOCS_DIR / "alignment_matrix.csv", matches)
    timeline_svg = render_timeline_svg(opportunities)
    (DOCS_DIR / "timeline.svg").write_text(timeline_svg, encoding="utf-8")
    report = render_markdown_report(opportunities, matches)
    (DOCS_DIR / "funding-screening-report.md").write_text(report, encoding="utf-8")
    site_page = render_site_page(opportunities, matches, timeline_svg)
    (SITE_DIR / "2026-06-11.html").write_text(site_page, encoding="utf-8")
    return 0


def write_alignment_csv(path: Path, matches) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "opportunity_id",
                "program",
                "sponsor",
                "faculty_id",
                "faculty_name",
                "score",
                "matched_keywords",
                "rationale",
            ],
        )
        writer.writeheader()
        for match in matches:
            row = asdict(match)
            row["matched_keywords"] = "; ".join(match.matched_keywords)
            writer.writerow(row)


def days_until(deadline: str) -> int:
    return (datetime.strptime(deadline, "%Y-%m-%d").date() - SNAPSHOT_DATE).days


def urgency(deadline: str) -> str:
    days = days_until(deadline)
    if days <= 21:
        return "urgent"
    if days <= 60:
        return "soon"
    if days <= 120:
        return "planning"
    return "watch"


def render_timeline_svg(opportunities) -> str:
    width = 1120
    row_height = 34
    left = 300
    top = 44
    chart_width = 700
    max_days = max(days_until(opp.deadline) for opp in opportunities)
    height = top + row_height * len(opportunities) + 50
    colors = {
        "urgent": "#be123c",
        "soon": "#b7791f",
        "planning": "#2563eb",
        "watch": "#0f766e",
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Funding opportunity timeline">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="24" y="28" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#1b2a32">Funding opportunity timeline from June 11, 2026</text>',
        f'<line x1="{left}" y1="{top - 12}" x2="{left + chart_width}" y2="{top - 12}" stroke="#cbd5dc" stroke-width="1"/>',
    ]
    for index, opp in enumerate(sorted(opportunities, key=lambda item: item.deadline)):
        y = top + index * row_height
        days = max(days_until(opp.deadline), 0)
        bar_width = max(8, int(chart_width * days / max_days))
        band = urgency(opp.deadline)
        lines.extend(
            [
                f'<text x="24" y="{y + 16}" font-family="Arial, sans-serif" font-size="12" fill="#33444e">{html.escape(opp.program[:42])}</text>',
                f'<rect x="{left}" y="{y}" width="{bar_width}" height="18" rx="4" fill="{colors[band]}"/>',
                f'<text x="{left + bar_width + 8}" y="{y + 14}" font-family="Arial, sans-serif" font-size="12" fill="#33444e">{opp.deadline} ({days} days)</text>',
            ]
        )
    lines.append("</svg>")
    return "\n".join(lines)


def top_matches_by_opportunity(matches, limit: int = 3):
    grouped = defaultdict(list)
    for match in matches:
        grouped[match.opportunity_id].append(match)
    return {key: sorted(value, key=lambda item: (-item.score, item.faculty_name))[:limit] for key, value in grouped.items()}


def render_markdown_report(opportunities, matches) -> str:
    top = top_matches_by_opportunity(matches)
    lines = [
        "# Current Funding Opportunity Screening",
        "",
        "Snapshot date: 2026-06-11",
        "",
        "This screening is a curated scan of active or actionable opportunities from the source registry. Sponsor pages remain authoritative, and internal eligibility, cost share, and routing should be verified before action.",
        "",
        "![Funding opportunity timeline](timeline.svg)",
        "",
        "## Priority View",
        "",
        "| Urgency | Sponsor | Program | Deadline | Top aligned faculty/labs |",
        "| --- | --- | --- | --- | --- |",
    ]
    for opp in sorted(opportunities, key=lambda item: item.deadline):
        names = ", ".join(match.faculty_name for match in top.get(opp.id, [])[:3]) or "Manual review"
        lines.append(
            f"| {urgency(opp.deadline)} | {opp.sponsor} | [{opp.program}]({opp.source_url}) | {opp.deadline} | {names} |"
        )

    lines.extend(["", "## Opportunity Notes", ""])
    for opp in sorted(opportunities, key=lambda item: item.deadline):
        lines.extend(
            [
                f"### {opp.program}",
                "",
                f"- Sponsor: {opp.sponsor}",
                f"- Deadline: {opp.deadline} ({days_until(opp.deadline)} days from snapshot)",
                f"- Urgency: {urgency(opp.deadline)}",
                f"- Summary: {opp.topic_summary}",
                f"- Notes: {opp.notes}",
                "- Top matches:",
            ]
        )
        for match in top.get(opp.id, [])[:5]:
            lines.append(
                f"  - {match.faculty_name}: score {match.score:.3f}; terms: {', '.join(match.matched_keywords)}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_site_page(opportunities, matches, timeline_svg: str) -> str:
    top = top_matches_by_opportunity(matches)
    rows = []
    for opp in sorted(opportunities, key=lambda item: item.deadline):
        names = ", ".join(match.faculty_name for match in top.get(opp.id, [])[:3]) or "Manual review"
        rows.append(
            "<tr>"
            f"<td>{html.escape(urgency(opp.deadline).title())}</td>"
            f"<td><a href=\"{html.escape(opp.source_url)}\">{html.escape(opp.program)}</a><br><span>{html.escape(opp.sponsor)}</span></td>"
            f"<td>{html.escape(opp.deadline)}</td>"
            f"<td>{html.escape(names)}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Funding Screening - 2026-06-11</title>
  <link rel="stylesheet" href="../styles.css">
  <style>
    .report-table {{ width: 100%; border-collapse: collapse; background: #fff; }}
    .report-table th, .report-table td {{ border-bottom: 1px solid #d8e1e6; padding: 10px; text-align: left; vertical-align: top; }}
    .report-table th {{ background: #edf3f5; }}
    .timeline-wrap {{ overflow-x: auto; border: 1px solid #d8e1e6; border-radius: 8px; background: #fff; }}
  </style>
</head>
<body>
  <header class="topbar">
    <div><p class="eyebrow">Funding Screening</p><h1>June 11, 2026</h1></div>
    <nav><a href="../index.html">Dashboard</a><a href="https://github.com/hanhuark/funding-compiler">GitHub</a></nav>
  </header>
  <main>
    <section class="overview">
      <div class="overview-copy">
        <p class="eyebrow">Current opportunity snapshot</p>
        <h2>Timeline and faculty alignment for active funding opportunities.</h2>
        <p>Curated scan of opportunities that appear actionable for UArk MEEG based on public sponsor pages checked on June 11, 2026.</p>
      </div>
      <div class="metrics">
        <div class="metric"><span>{len(opportunities)}</span><p>Opportunities screened</p></div>
        <div class="metric"><span>{len(matches)}</span><p>Faculty alignments</p></div>
      </div>
    </section>
    <section class="panel">
      <div class="section-heading"><p class="eyebrow">Timeline</p><h2>Deadlines and planning horizon</h2></div>
      <div class="timeline-wrap">{timeline_svg}</div>
    </section>
    <section class="panel">
      <div class="section-heading"><p class="eyebrow">Alignment</p><h2>Priority view</h2></div>
      <table class="report-table">
        <thead><tr><th>Urgency</th><th>Opportunity</th><th>Deadline</th><th>Top aligned faculty/labs</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
