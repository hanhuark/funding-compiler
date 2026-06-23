from __future__ import annotations

import csv
import html
import json
import os
from collections import defaultdict
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

import yaml

from funding_compiler.loaders import load_faculty, load_opportunities
from funding_compiler.matching import match_opportunities


SNAPSHOT_DATE = date(2026, 6, 11)
SCREENING_DIR = Path("data/screenings/2026-06-11")
ACTION_METADATA_PATH = SCREENING_DIR / "opportunity_actions.yaml"
DOCS_DIR = Path("docs/screenings/2026-06-11")
SITE_DIR = Path("site/screenings")
SITE_DATA_DIR = Path("site/data")
REPORT_URL = "screenings/2026-06-11.html"


def main() -> int:
    as_of = current_date()
    opportunities = load_opportunities(SCREENING_DIR / "opportunities.csv")
    faculty = load_faculty(SCREENING_DIR / "faculty_profiles.csv")
    actions = load_action_metadata(ACTION_METADATA_PATH)
    matches = match_opportunities(opportunities, faculty, min_score=0.1)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    SITE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    write_alignment_csv(DOCS_DIR / "alignment_matrix.csv", matches)
    timeline_svg = render_timeline_svg(opportunities, actions, as_of)
    (DOCS_DIR / "timeline.svg").write_text(timeline_svg, encoding="utf-8")
    report = render_markdown_report(opportunities, matches, actions, as_of)
    (DOCS_DIR / "funding-screening-report.md").write_text(report, encoding="utf-8")
    summary = build_screening_summary(opportunities, matches, actions, as_of)
    (SITE_DATA_DIR / "screening_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    faculty_summary = build_faculty_action_summary(opportunities, matches, actions, as_of)
    (SITE_DATA_DIR / "faculty_action_summary.json").write_text(
        json.dumps(faculty_summary, indent=2) + "\n",
        encoding="utf-8",
    )
    site_page = render_site_page(opportunities, matches, actions, timeline_svg, as_of)
    (SITE_DIR / "2026-06-11.html").write_text(site_page, encoding="utf-8")
    return 0


def current_date() -> date:
    value = os.environ.get("FUNDING_COMPILER_TODAY")
    if value:
        return datetime.strptime(value, "%Y-%m-%d").date()
    return date.today()


def load_action_metadata(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    records = data.get("records", {})
    return {str(key): dict(value or {}) for key, value in records.items()}


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
                "fit_level",
                "matched_keyword_count",
                "matched_keywords",
                "rationale",
            ],
        )
        writer.writeheader()
        for match in matches:
            row = asdict(match)
            row["fit_level"] = fit_level(match.score)
            row["matched_keyword_count"] = len(match.matched_keywords)
            row["matched_keywords"] = "; ".join(match.matched_keywords)
            writer.writerow(row)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def days_until(deadline: str, as_of: date = SNAPSHOT_DATE) -> int:
    parsed = parse_date(deadline)
    if parsed is None:
        raise ValueError("deadline is required")
    return (parsed - as_of).days


def deadline_type(opportunity, actions: dict[str, dict[str, str]]) -> str:
    return actions.get(opportunity.id, {}).get("deadline_type", "fixed")


def has_dated_deadline(opportunity, actions: dict[str, dict[str, str]]) -> bool:
    return deadline_type(opportunity, actions) in {"fixed", "window"} and parse_date(opportunity.deadline) is not None


def days_remaining(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> int | None:
    if not has_dated_deadline(opportunity, actions):
        return None
    return days_until(opportunity.deadline, as_of)


def urgency_from_days(days: int) -> str:
    if days < 0:
        return "past due"
    if days <= 7:
        return "urgent"
    if days <= 30:
        return "soon"
    if days <= 90:
        return "planning"
    return "watch"


def urgency(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> str:
    days = days_remaining(opportunity, actions, as_of)
    if days is None:
        kind = deadline_type(opportunity, actions)
        return "accepted anytime" if kind == "accepted_anytime" else "rolling"
    return urgency_from_days(days)


def action_status(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> str:
    metadata = actions.get(opportunity.id, {})
    review_by = parse_date(metadata.get("internal_review_by"))
    days = days_remaining(opportunity, actions, as_of)
    if review_by and review_by < as_of and days is not None and days >= 0:
        return "internal review overdue"
    return urgency(opportunity, actions, as_of)


def deadline_display(opportunity, actions: dict[str, dict[str, str]]) -> str:
    metadata = actions.get(opportunity.id, {})
    if metadata.get("display_deadline"):
        return metadata["display_deadline"]
    kind = deadline_type(opportunity, actions)
    if kind == "accepted_anytime":
        return "Accepted anytime"
    if kind == "rolling":
        return "Rolling while open"
    return opportunity.deadline or "Manual review"


def days_phrase(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> str:
    days = days_remaining(opportunity, actions, as_of)
    if days is None:
        kind = deadline_type(opportunity, actions)
        if kind == "accepted_anytime":
            return "no fixed deadline"
        if kind == "rolling":
            return "rolling while open"
        return kind.replace("_", " ")
    if days < 0:
        return f"passed {abs(days)} days ago as of {as_of.isoformat()}"
    if days == 0:
        return f"due today as of {as_of.isoformat()}"
    return f"{days} days remaining as of {as_of.isoformat()}"


def deadline_context(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> str:
    display = deadline_display(opportunity, actions)
    phrase = days_phrase(opportunity, actions, as_of)
    if display.lower() == phrase.lower():
        return display
    return f"{display}; {phrase}"


def internal_review_display(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> str:
    value = actions.get(opportunity.id, {}).get("internal_review_by", "")
    if not value:
        return "Not set"
    review_by = parse_date(value)
    if review_by and review_by < as_of:
        return f"{value} (overdue)"
    return value


def next_action(opportunity, actions: dict[str, dict[str, str]]) -> str:
    return actions.get(opportunity.id, {}).get("next_action", "Manual review")


def risk_notes(opportunity, actions: dict[str, dict[str, str]]) -> str:
    return actions.get(opportunity.id, {}).get("risk_notes", opportunity.notes or "Review sponsor page")


def verified_on(opportunity, actions: dict[str, dict[str, str]]) -> str:
    return actions.get(opportunity.id, {}).get("verified_on", "")


def sort_opportunities(opportunities, actions: dict[str, dict[str, str]]):
    def key(opportunity):
        parsed = parse_date(opportunity.deadline)
        if has_dated_deadline(opportunity, actions) and parsed:
            return (0, parsed.isoformat(), opportunity.program)
        return (1, deadline_display(opportunity, actions), opportunity.program)

    return sorted(opportunities, key=key)


def render_timeline_svg(opportunities, actions: dict[str, dict[str, str]], as_of: date) -> str:
    dated_opportunities = [opp for opp in opportunities if has_dated_deadline(opp, actions)]
    width = 1120
    row_height = 34
    left = 300
    top = 44
    chart_width = 700
    max_days = (
        max(max(days_remaining(opp, actions, as_of) or 0, 1) for opp in dated_opportunities)
        if dated_opportunities
        else 1
    )
    height = top + row_height * max(len(dated_opportunities), 1) + 70
    colors = {
        "past due": "#64748b",
        "urgent": "#be123c",
        "soon": "#b7791f",
        "planning": "#2563eb",
        "watch": "#0f766e",
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Funding opportunity timeline">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="24" y="28" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#1b2a32">Funding opportunity timeline as of {as_of.isoformat()}</text>',
        f'<line x1="{left}" y1="{top - 12}" x2="{left + chart_width}" y2="{top - 12}" stroke="#cbd5dc" stroke-width="1"/>',
    ]
    if not dated_opportunities:
        lines.append('<text x="24" y="60" font-family="Arial, sans-serif" font-size="12" fill="#33444e">No fixed or windowed deadlines in this screening.</text>')
    for index, opp in enumerate(sort_opportunities(dated_opportunities, actions)):
        y = top + index * row_height
        remaining = days_remaining(opp, actions, as_of) or 0
        days = max(remaining, 0)
        bar_width = max(8, int(chart_width * days / max_days))
        band = urgency_from_days(remaining)
        lines.extend(
            [
                f'<text x="24" y="{y + 16}" font-family="Arial, sans-serif" font-size="12" fill="#33444e">{html.escape(opp.program[:42])}</text>',
                f'<rect x="{left}" y="{y}" width="{bar_width}" height="18" rx="4" fill="{colors[band]}"/>',
                f'<text x="{left + bar_width + 8}" y="{y + 14}" font-family="Arial, sans-serif" font-size="12" fill="#33444e">{html.escape(deadline_display(opp, actions))} ({html.escape(days_phrase(opp, actions, as_of))})</text>',
            ]
        )
    foot_y = top + row_height * max(len(dated_opportunities), 1) + 24
    lines.append(
        f'<text x="24" y="{foot_y}" font-family="Arial, sans-serif" font-size="12" fill="#61717b">Rolling and accepted-anytime items are tracked in the action table instead of shown as fixed deadline bars.</text>'
    )
    lines.append("</svg>")
    return "\n".join(lines)


def top_matches_by_opportunity(matches, limit: int = 3):
    grouped = defaultdict(list)
    for match in matches:
        grouped[match.opportunity_id].append(match)
    return {key: sorted(value, key=lambda item: (-item.score, item.faculty_name))[:limit] for key, value in grouped.items()}


def fit_level(score: float) -> str:
    if score >= 0.5:
        return "strong"
    if score >= 0.25:
        return "promising"
    return "exploratory"


def match_terms(match, limit: int = 5) -> str:
    if not match.matched_keywords:
        return "manual review"
    terms = match.matched_keywords[:limit]
    suffix = "" if len(match.matched_keywords) <= limit else f"; +{len(match.matched_keywords) - limit} more"
    return ", ".join(terms) + suffix


def match_evidence_text(matches) -> str:
    if not matches:
        return "Manual review"
    return "; ".join(
        f"{match.faculty_name} ({fit_level(match.score)}, score {match.score:.3f}): {match_terms(match)}"
        for match in matches
    )


def match_evidence_html(matches) -> str:
    if not matches:
        return "Manual review"
    parts = []
    for match in matches:
        parts.append(
            f"<strong>{html.escape(match.faculty_name)}</strong>"
            f"<br><span>{html.escape(fit_level(match.score).title())} fit; score {match.score:.3f}; terms: {match_terms(match)}</span>"
        )
    return "<br><br>".join(parts)


def action_priority(status: str) -> int:
    order = {
        "internal review overdue": 0,
        "urgent": 1,
        "soon": 2,
        "planning": 3,
        "accepted anytime": 4,
        "watch": 5,
        "rolling": 6,
        "past due": 7,
    }
    return order.get(status, 9)


def build_faculty_action_summary(opportunities, matches, actions: dict[str, dict[str, str]], as_of: date) -> list[dict[str, object]]:
    opportunity_by_id = {opportunity.id: opportunity for opportunity in opportunities}
    grouped = defaultdict(list)
    for match in matches:
        opportunity = opportunity_by_id.get(match.opportunity_id)
        if opportunity:
            grouped[match.faculty_name].append((match, opportunity))

    summary = []
    for faculty_name, records in sorted(grouped.items()):
        ranked = sorted(
            records,
            key=lambda record: (
                action_priority(action_status(record[1], actions, as_of)),
                -record[0].score,
                record[1].program,
            ),
        )
        opportunities_summary = []
        for match, opportunity in ranked[:4]:
            opportunities_summary.append(
                {
                    "program": opportunity.program,
                    "sponsor": opportunity.sponsor,
                    "source_url": opportunity.source_url,
                    "status": action_status(opportunity, actions, as_of),
                    "deadline": deadline_context(opportunity, actions, as_of),
                    "score": match.score,
                    "fit_level": fit_level(match.score),
                    "matched_terms": match.matched_keywords,
                    "next_action": next_action(opportunity, actions),
                }
            )
        summary.append(
            {
                "faculty_name": faculty_name,
                "opportunity_count": len(records),
                "priority_opportunities": opportunities_summary,
            }
        )
    return summary


def build_screening_summary(opportunities, matches, actions: dict[str, dict[str, str]], as_of: date) -> dict[str, object]:
    future_dated = [
        (days_remaining(opp, actions, as_of), opp)
        for opp in opportunities
        if days_remaining(opp, actions, as_of) is not None and days_remaining(opp, actions, as_of) >= 0
    ]
    nearest_days, nearest = min(future_dated, key=lambda item: item[0]) if future_dated else (None, None)
    overdue_reviews = [
        opp
        for opp in opportunities
        if action_status(opp, actions, as_of) == "internal review overdue"
    ]
    urgent_items = [
        opp
        for opp in opportunities
        if action_status(opp, actions, as_of) in {"urgent", "internal review overdue"}
    ]
    rolling_items = [
        opp
        for opp in opportunities
        if not has_dated_deadline(opp, actions)
    ]
    return {
        "snapshot_date": SNAPSHOT_DATE.isoformat(),
        "refreshed_on": as_of.isoformat(),
        "report_url": REPORT_URL,
        "opportunity_count": len(opportunities),
        "alignment_count": len(matches),
        "urgent_action_count": len(urgent_items),
        "overdue_internal_review_count": len(overdue_reviews),
        "rolling_count": len(rolling_items),
        "nearest_deadline_days": nearest_days,
        "nearest_deadline_program": nearest.program if nearest else "",
        "nearest_deadline_label": deadline_display(nearest, actions) if nearest else "",
        "nearest_deadline_status": action_status(nearest, actions, as_of) if nearest else "",
    }


def markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown_report(opportunities, matches, actions: dict[str, dict[str, str]], as_of: date) -> str:
    top = top_matches_by_opportunity(matches)
    summary = build_screening_summary(opportunities, matches, actions, as_of)
    lines = [
        "# Current Funding Opportunity Screening",
        "",
        "Snapshot date: 2026-06-11",
        f"Report refreshed: {as_of.isoformat()}",
        "",
        "This screening is a curated scan of active or actionable opportunities from the source registry. Sponsor pages remain authoritative, and internal eligibility, cost share, and routing should be verified before action.",
        "",
        "## Decision Summary",
        "",
        f"- Opportunities screened: {summary['opportunity_count']}",
        f"- Faculty alignments found: {summary['alignment_count']}",
        f"- Urgent or overdue action items: {summary['urgent_action_count']}",
        f"- Internal review dates already overdue: {summary['overdue_internal_review_count']}",
        f"- Rolling or accepted-anytime items tracked separately: {summary['rolling_count']}",
        "",
        "## Faculty Action Inbox",
        "",
        "| Action status | Sponsor | Program | Public deadline | Internal review by | Match evidence | Next action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for opp in sort_opportunities(opportunities, actions):
        evidence = match_evidence_text(top.get(opp.id, [])[:3])
        lines.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in [
                    action_status(opp, actions, as_of),
                    opp.sponsor,
                    f"[{opp.program}]({opp.source_url})",
                    deadline_context(opp, actions, as_of),
                    internal_review_display(opp, actions, as_of),
                    evidence,
                    next_action(opp, actions),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Deadline Timeline",
            "",
        ]
    )
    lines.extend(
        [
        "![Funding opportunity timeline](timeline.svg)",
        "",
        "## Priority View",
        "",
        "| Urgency | Sponsor | Program | Deadline | Top aligned faculty/labs | Risk notes |",
        "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for opp in sort_opportunities(opportunities, actions):
        names = ", ".join(match.faculty_name for match in top.get(opp.id, [])[:3]) or "Manual review"
        lines.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in [
                    urgency(opp, actions, as_of),
                    opp.sponsor,
                    f"[{opp.program}]({opp.source_url})",
                    deadline_context(opp, actions, as_of),
                    names,
                    risk_notes(opp, actions),
                ]
            )
            + " |"
        )

    lines.extend(["", "## Faculty Briefs", ""])
    lines.extend(
        [
            "| Faculty | Priority opportunities | Evidence to verify | Suggested follow-up |",
            "| --- | --- | --- | --- |",
        ]
    )
    for brief in build_faculty_action_summary(opportunities, matches, actions, as_of):
        items = brief["priority_opportunities"]
        priority = "; ".join(
            f"[{item['program']}]({item['source_url']}) ({item['status']}; {item['deadline']})"
            for item in items[:4]
        )
        evidence = "; ".join(
            f"{item['fit_level']} fit, score {item['score']:.3f}, terms: {', '.join(item['matched_terms'][:5]) or 'manual review'}"
            for item in items[:4]
        )
        follow_up = items[0]["next_action"] if items else "Manual review"
        lines.append(
            "| "
            + " | ".join(
                markdown_cell(value)
                for value in [
                    brief["faculty_name"],
                    priority,
                    evidence,
                    follow_up,
                ]
            )
            + " |"
        )

    lines.extend(["", "## Opportunity Notes", ""])
    for opp in sort_opportunities(opportunities, actions):
        lines.extend(
            [
                f"### {opp.program}",
                "",
                f"- Sponsor: {opp.sponsor}",
                f"- Deadline: {deadline_context(opp, actions, as_of)}",
                f"- Deadline type: {deadline_type(opp, actions).replace('_', ' ')}",
                f"- Internal review by: {internal_review_display(opp, actions, as_of)}",
                f"- Verified on: {verified_on(opp, actions) or 'Not recorded'}",
                f"- Action status: {action_status(opp, actions, as_of)}",
                f"- Next action: {next_action(opp, actions)}",
                f"- Risk notes: {risk_notes(opp, actions)}",
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


def status_class(value: str) -> str:
    return value.replace(" ", "-").replace("_", "-")


def deadline_html(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> str:
    display = deadline_display(opportunity, actions)
    phrase = days_phrase(opportunity, actions, as_of)
    escaped_display = html.escape(display)
    if display.lower() == phrase.lower():
        return escaped_display
    return f"{escaped_display}<br><span>{html.escape(phrase)}</span>"


def render_faculty_briefs(opportunities, matches, actions: dict[str, dict[str, str]], as_of: date) -> str:
    cards = []
    for brief in build_faculty_action_summary(opportunities, matches, actions, as_of):
        items = []
        for item in brief["priority_opportunities"][:4]:
            terms = ", ".join(item["matched_terms"][:5]) if item["matched_terms"] else "manual review"
            items.append(
                "<li>"
                f"<a href=\"{html.escape(item['source_url'])}\">{html.escape(item['program'])}</a>"
                f"<span class=\"status-pill {html.escape(status_class(item['status']))}\">{html.escape(item['status'].title())}</span>"
                f"<p>{html.escape(item['deadline'])}</p>"
                f"<p>{html.escape(item['fit_level'].title())} fit; score {item['score']:.3f}; terms: {html.escape(terms)}</p>"
                "</li>"
            )
        cards.append(
            "<article class=\"faculty-brief\">"
            f"<h3>{html.escape(brief['faculty_name'])}</h3>"
            f"<p>{brief['opportunity_count']} matched {'opportunity' if brief['opportunity_count'] == 1 else 'opportunities'} in this screening.</p>"
            f"<ul>{''.join(items)}</ul>"
            "</article>"
        )
    return "".join(cards)


def render_site_page(opportunities, matches, actions: dict[str, dict[str, str]], timeline_svg: str, as_of: date) -> str:
    top = top_matches_by_opportunity(matches)
    summary = build_screening_summary(opportunities, matches, actions, as_of)
    rows = []
    for opp in sort_opportunities(opportunities, actions):
        evidence = match_evidence_html(top.get(opp.id, [])[:3])
        rows.append(
            "<tr>"
            f"<td><span class=\"status-pill {html.escape(status_class(action_status(opp, actions, as_of)))}\">{html.escape(action_status(opp, actions, as_of).title())}</span></td>"
            f"<td><a href=\"{html.escape(opp.source_url)}\">{html.escape(opp.program)}</a><br><span>{html.escape(opp.sponsor)}</span></td>"
            f"<td>{deadline_html(opp, actions, as_of)}</td>"
            f"<td>{html.escape(internal_review_display(opp, actions, as_of))}</td>"
            f"<td>{evidence}</td>"
            f"<td>{html.escape(next_action(opp, actions))}</td>"
            f"<td>{html.escape(risk_notes(opp, actions))}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Funding Screening - 2026-06-11</title>
  <link rel="stylesheet" href="../styles.css">
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
        <h2>Faculty action inbox for active funding opportunities.</h2>
        <p>Curated scan of opportunities that appear actionable for UArk MEEG based on public sponsor pages checked on June 11, 2026 and refreshed on {as_of.isoformat()}.</p>
      </div>
      <div class="metrics">
        <div class="metric"><span>{len(opportunities)}</span><p>Opportunities screened</p></div>
        <div class="metric"><span>{len(matches)}</span><p>Faculty alignments</p></div>
        <div class="metric"><span>{summary['urgent_action_count']}</span><p>Urgent or overdue actions</p></div>
      </div>
    </section>
    <section class="notice" role="note">
      Sponsor pages remain authoritative. Eligibility, cost share, limited-submission rules, and internal routing should be verified before faculty commit proposal-development time.
    </section>
    <section class="panel">
      <div class="section-heading"><p class="eyebrow">Decision Summary</p><h2>What needs attention first</h2></div>
      <div class="summary-grid">
        <article><span>{summary['nearest_deadline_days']}</span><p>Days to nearest dated deadline</p><strong>{html.escape(summary['nearest_deadline_program'])}</strong></article>
        <article><span>{summary['overdue_internal_review_count']}</span><p>Internal reviews overdue</p><strong>Check routing before outreach</strong></article>
        <article><span>{summary['rolling_count']}</span><p>Rolling or accepted-anytime items</p><strong>Track separately from fixed deadlines</strong></article>
      </div>
    </section>
    <section class="panel">
      <div class="section-heading"><p class="eyebrow">Timeline</p><h2>Deadlines and planning horizon</h2></div>
      <div class="timeline-wrap">{timeline_svg}</div>
    </section>
    <section class="panel">
      <div class="section-heading"><p class="eyebrow">Action Inbox</p><h2>Faculty-facing triage table</h2></div>
      <div class="table-wrap"><table class="report-table">
        <thead><tr><th>Status</th><th>Opportunity</th><th>Public deadline</th><th>Internal review</th><th>Match evidence</th><th>Next action</th><th>Risk notes</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table></div>
    </section>
    <section class="panel">
      <div class="section-heading"><p class="eyebrow">Faculty Briefs</p><h2>Who should look at what</h2></div>
      <div class="faculty-briefs">{render_faculty_briefs(opportunities, matches, actions, as_of)}</div>
    </section>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
