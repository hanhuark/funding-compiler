from __future__ import annotations

import csv
import html
import json
import os
from collections import defaultdict
from dataclasses import asdict
from datetime import date, datetime, timedelta
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
VERIFICATION_STALE_AFTER_DAYS = 14


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
    source_recheck_queue = build_source_recheck_queue(opportunities, actions, as_of)
    (SITE_DATA_DIR / "source_recheck_queue.json").write_text(
        json.dumps(source_recheck_queue, indent=2) + "\n",
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


def is_past_due(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> bool:
    days = days_remaining(opportunity, actions, as_of)
    return days is not None and days < 0


def active_opportunities(opportunities, actions: dict[str, dict[str, str]], as_of: date):
    return [opportunity for opportunity in opportunities if not is_past_due(opportunity, actions, as_of)]


def past_due_opportunities(opportunities, actions: dict[str, dict[str, str]], as_of: date):
    return [opportunity for opportunity in opportunities if is_past_due(opportunity, actions, as_of)]


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
        count = abs(days)
        unit = "day" if count == 1 else "days"
        return f"passed {count} {unit} ago as of {as_of.isoformat()}"
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


def verified_date(opportunity, actions: dict[str, dict[str, str]]) -> date | None:
    return parse_date(verified_on(opportunity, actions))


def verification_age_days(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> int | None:
    value = verified_date(opportunity, actions)
    if value is None:
        return None
    return (as_of - value).days


def needs_source_recheck(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> bool:
    age = verification_age_days(opportunity, actions, as_of)
    return age is None or age > VERIFICATION_STALE_AFTER_DAYS


def verification_context(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> str:
    value = verified_on(opportunity, actions)
    age = verification_age_days(opportunity, actions, as_of)
    if age is None:
        return "Not recorded; recheck before action"
    suffix = "recheck before action" if needs_source_recheck(opportunity, actions, as_of) else "current enough for triage"
    return f"Last checked {value}; {age} days old; {suffix}"


def verification_html(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> str:
    status = "Needs Recheck" if needs_source_recheck(opportunity, actions, as_of) else "Recently Checked"
    class_name = "source-recheck" if needs_source_recheck(opportunity, actions, as_of) else "source-current"
    return (
        f"<span class=\"status-pill {class_name}\">{status}</span>"
        f"<br><span>{html.escape(verification_context(opportunity, actions, as_of))}</span>"
    )


def source_recheck_owner(opportunity, actions: dict[str, dict[str, str]]) -> str:
    return actions.get(opportunity.id, {}).get("source_recheck_owner", "Research development lead")


def source_recheck_focus(opportunity, actions: dict[str, dict[str, str]]) -> str:
    return actions.get(opportunity.id, {}).get(
        "source_recheck_focus",
        "Confirm deadline, eligibility, sponsor text, and internal routing constraints before faculty outreach.",
    )


def source_recheck_by(opportunity, actions: dict[str, dict[str, str]]) -> date | None:
    metadata = actions.get(opportunity.id, {})
    explicit = parse_date(metadata.get("source_recheck_by"))
    if explicit:
        return explicit
    checked = verified_date(opportunity, actions)
    if checked:
        return checked + timedelta(days=VERIFICATION_STALE_AFTER_DAYS)
    return None


def source_recheck_days_overdue(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> int | None:
    due = source_recheck_by(opportunity, actions)
    if due is None:
        return None
    return max((as_of - due).days, 0)


def routing_gate(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> str:
    if not needs_source_recheck(opportunity, actions, as_of):
        return "Open for routing"
    status = action_status(opportunity, actions, as_of)
    remaining = days_remaining(opportunity, actions, as_of)
    if status == "internal review overdue":
        return "Block faculty outreach until source and internal-review status are rechecked."
    if remaining is not None and remaining <= 30:
        return "Block near-term faculty outreach until sponsor page is rechecked."
    if remaining is not None and remaining <= 90:
        return "Verify before concept-routing outreach."
    return "Verify before watchlist forwarding."


def outreach_readiness(opportunity, actions: dict[str, dict[str, str]], as_of: date) -> str:
    gate = routing_gate(opportunity, actions, as_of)
    if gate.startswith("Block"):
        return "outreach blocked"
    if needs_source_recheck(opportunity, actions, as_of):
        return "verify first"
    return "ready after normal review"


def build_source_recheck_queue(opportunities, actions: dict[str, dict[str, str]], as_of: date) -> list[dict[str, object]]:
    queue = []
    for opportunity in active_opportunities(opportunities, actions, as_of):
        if not needs_source_recheck(opportunity, actions, as_of):
            continue
        due = source_recheck_by(opportunity, actions)
        remaining = days_remaining(opportunity, actions, as_of)
        queue.append(
            {
                "program": opportunity.program,
                "sponsor": opportunity.sponsor,
                "source_url": opportunity.source_url,
                "status": action_status(opportunity, actions, as_of),
                "deadline": deadline_context(opportunity, actions, as_of),
                "deadline_days_remaining": remaining,
                "verified_on": verified_on(opportunity, actions) or "",
                "verification_age_days": verification_age_days(opportunity, actions, as_of),
                "source_recheck_by": due.isoformat() if due else "",
                "source_recheck_days_overdue": source_recheck_days_overdue(opportunity, actions, as_of),
                "source_recheck_owner": source_recheck_owner(opportunity, actions),
                "routing_gate": routing_gate(opportunity, actions, as_of),
                "verification_focus": source_recheck_focus(opportunity, actions),
            }
        )
    return sorted(
        queue,
        key=lambda item: (
            action_priority(str(item["status"])),
            item["deadline_days_remaining"] is None,
            item["deadline_days_remaining"] if item["deadline_days_remaining"] is not None else 9999,
            str(item["program"]),
        ),
    )


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
        if opportunity and not is_past_due(opportunity, actions, as_of):
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
            due = source_recheck_by(opportunity, actions)
            opportunities_summary.append(
                {
                    "program": opportunity.program,
                    "sponsor": opportunity.sponsor,
                    "source_url": opportunity.source_url,
                    "status": action_status(opportunity, actions, as_of),
                    "deadline": deadline_context(opportunity, actions, as_of),
                    "outreach_readiness": outreach_readiness(opportunity, actions, as_of),
                    "routing_gate": routing_gate(opportunity, actions, as_of),
                    "source_recheck_required": needs_source_recheck(opportunity, actions, as_of),
                    "source_recheck_by": due.isoformat() if due else "",
                    "source_recheck_days_overdue": source_recheck_days_overdue(opportunity, actions, as_of),
                    "verification_focus": source_recheck_focus(opportunity, actions),
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
    active = active_opportunities(opportunities, actions, as_of)
    past_due = past_due_opportunities(opportunities, actions, as_of)
    source_recheck_queue = build_source_recheck_queue(opportunities, actions, as_of)
    verification_ages = [
        age
        for opportunity in active
        if (age := verification_age_days(opportunity, actions, as_of)) is not None
    ]
    future_dated = [
        (days_remaining(opp, actions, as_of), opp)
        for opp in active
        if days_remaining(opp, actions, as_of) is not None and days_remaining(opp, actions, as_of) >= 0
    ]
    nearest_days, nearest = min(future_dated, key=lambda item: item[0]) if future_dated else (None, None)
    overdue_reviews = [
        opp
        for opp in active
        if action_status(opp, actions, as_of) == "internal review overdue"
    ]
    urgent_items = [
        opp
        for opp in active
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
        "active_opportunity_count": len(active),
        "past_due_count": len(past_due),
        "alignment_count": len(matches),
        "urgent_action_count": len(urgent_items),
        "overdue_internal_review_count": len(overdue_reviews),
        "source_recheck_count": len(source_recheck_queue),
        "source_recheck_overdue_count": sum(
            1
            for item in source_recheck_queue
            if item["source_recheck_days_overdue"] is not None and item["source_recheck_days_overdue"] > 0
        ),
        "faculty_outreach_blocked_count": sum(
            1
            for item in source_recheck_queue
            if str(item["routing_gate"]).startswith("Block")
        ),
        "oldest_verification_age_days": max(verification_ages) if verification_ages else None,
        "verification_stale_after_days": VERIFICATION_STALE_AFTER_DAYS,
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
    active = active_opportunities(opportunities, actions, as_of)
    past_due = past_due_opportunities(opportunities, actions, as_of)
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
        f"- Active opportunities: {summary['active_opportunity_count']}",
        f"- Passed public deadlines: {summary['past_due_count']}",
        f"- Faculty alignments found: {summary['alignment_count']}",
        f"- Urgent or overdue action items: {summary['urgent_action_count']}",
        f"- Internal review dates already overdue: {summary['overdue_internal_review_count']}",
        f"- Active opportunities needing sponsor-source recheck: {summary['source_recheck_count']}",
        f"- Source rechecks overdue: {summary['source_recheck_overdue_count']}",
        f"- Faculty outreach blocked pending source recheck: {summary['faculty_outreach_blocked_count']}",
        "- Oldest active source verification age: "
        + (
            f"{summary['oldest_verification_age_days']} days"
            if summary["oldest_verification_age_days"] is not None
            else "Not recorded"
        ),
        f"- Rolling or accepted-anytime items tracked separately: {summary['rolling_count']}",
        "",
        "## Faculty Action Inbox",
        "",
        "| Action status | Sponsor | Program | Public deadline | Source verification | Internal review by | Match evidence | Next action |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for opp in sort_opportunities(active, actions):
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
                    verification_context(opp, actions, as_of),
                    internal_review_display(opp, actions, as_of),
                    evidence,
                    next_action(opp, actions),
                ]
            )
            + " |"
        )

    source_recheck = build_source_recheck_queue(opportunities, actions, as_of)
    if source_recheck:
        lines.extend(
            [
                "",
                "## Source Recheck Queue",
                "",
                "| Status | Sponsor | Program | Last checked | Age | Recheck by | Overdue days | Owner | Routing gate | Verification focus |",
                "| --- | --- | --- | --- | ---: | --- | ---: | --- | --- | --- |",
            ]
        )
        for item in source_recheck:
            lines.append(
                "| "
                + " | ".join(
                    markdown_cell(value)
                    for value in [
                        item["status"],
                        item["sponsor"],
                        f"[{item['program']}]({item['source_url']})",
                        item["verified_on"] or "Not recorded",
                        "" if item["verification_age_days"] is None else str(item["verification_age_days"]),
                        item["source_recheck_by"] or "Not set",
                        "" if item["source_recheck_days_overdue"] is None else str(item["source_recheck_days_overdue"]),
                        item["source_recheck_owner"],
                        item["routing_gate"],
                        item["verification_focus"],
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
        if is_past_due(opp, actions, as_of):
            continue
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

    if past_due:
        lines.extend(
            [
                "",
                "## Passed Deadlines",
                "",
                "| Sponsor | Program | Deadline | Source verification | Prior match evidence | Follow-up |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for opp in sort_opportunities(past_due, actions):
            lines.append(
                "| "
                + " | ".join(
                    markdown_cell(value)
                    for value in [
                        opp.sponsor,
                        f"[{opp.program}]({opp.source_url})",
                        deadline_context(opp, actions, as_of),
                        verification_context(opp, actions, as_of),
                        match_evidence_text(top.get(opp.id, [])[:3]),
                        "Archive for lessons learned or mark as recurring only after the sponsor posts a new cycle.",
                    ]
                )
                + " |"
            )

    lines.extend(["", "## Faculty Briefs", ""])
    lines.extend(
        [
            "| Faculty | Priority opportunities | Readiness gate | Evidence to verify | Suggested follow-up |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for brief in build_faculty_action_summary(opportunities, matches, actions, as_of):
        items = brief["priority_opportunities"]
        priority = "; ".join(
            f"[{item['program']}]({item['source_url']}) ({item['status']}; {item['deadline']})"
            for item in items[:4]
        )
        readiness = "; ".join(
            f"{item['program']}: {item['outreach_readiness']}; {item['routing_gate']}"
            + (
                f" Source recheck by {item['source_recheck_by']}; {item['source_recheck_days_overdue']} days overdue."
                if item["source_recheck_required"]
                else ""
            )
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
                    readiness,
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
            recheck_due = item["source_recheck_by"] or "Not set"
            overdue = item["source_recheck_days_overdue"]
            overdue_context = f"{overdue} days overdue" if overdue is not None else "overdue status unknown"
            recheck_context = (
                f"Source recheck by {recheck_due}; {overdue_context}."
                if item["source_recheck_required"]
                else "Source verification current enough for routing."
            )
            items.append(
                "<li>"
                f"<a href=\"{html.escape(item['source_url'])}\">{html.escape(item['program'])}</a>"
                f"<span class=\"status-pill {html.escape(status_class(item['status']))}\">{html.escape(item['status'].title())}</span>"
                f"<span class=\"status-pill {html.escape(status_class(item['outreach_readiness']))}\">{html.escape(item['outreach_readiness'].title())}</span>"
                f"<p>{html.escape(item['deadline'])}</p>"
                f"<p>{html.escape(item['routing_gate'])}</p>"
                f"<p>{html.escape(recheck_context)}</p>"
                f"<p>{html.escape(item['fit_level'].title())} fit; score {item['score']:.3f}; terms: {html.escape(terms)}</p>"
                f"<p>Verify: {html.escape(item['verification_focus'])}</p>"
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


def render_passed_deadlines(opportunities, matches, actions: dict[str, dict[str, str]], as_of: date) -> str:
    past_due = past_due_opportunities(opportunities, actions, as_of)
    if not past_due:
        return ""
    top = top_matches_by_opportunity(matches)
    rows = []
    for opp in sort_opportunities(past_due, actions):
        rows.append(
            "<tr>"
            f"<td><span class=\"status-pill past-due\">Past Due</span></td>"
            f"<td><a href=\"{html.escape(opp.source_url)}\">{html.escape(opp.program)}</a><br><span>{html.escape(opp.sponsor)}</span></td>"
            f"<td>{deadline_html(opp, actions, as_of)}</td>"
            f"<td>{verification_html(opp, actions, as_of)}</td>"
            f"<td>{match_evidence_html(top.get(opp.id, [])[:3])}</td>"
            "<td>Archive for lessons learned or mark as recurring only after the sponsor posts a new cycle.</td>"
            "</tr>"
        )
    return f"""
    <section class="panel">
      <div class="section-heading"><p class="eyebrow">Passed Deadlines</p><h2>Archive, do not route</h2></div>
      <div class="table-wrap"><table class="report-table">
        <thead><tr><th>Status</th><th>Opportunity</th><th>Public deadline</th><th>Source verification</th><th>Prior match evidence</th><th>Follow-up</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table></div>
    </section>
"""


def render_source_recheck_queue(opportunities, actions: dict[str, dict[str, str]], as_of: date) -> str:
    recheck = build_source_recheck_queue(opportunities, actions, as_of)
    if not recheck:
        return ""
    rows = []
    for item in recheck:
        rows.append(
            "<tr>"
            f"<td><span class=\"status-pill {html.escape(status_class(str(item['status'])))}\">{html.escape(str(item['status']).title())}</span></td>"
            f"<td><a href=\"{html.escape(str(item['source_url']))}\">{html.escape(str(item['program']))}</a><br><span>{html.escape(str(item['sponsor']))}</span></td>"
            f"<td>{html.escape(str(item['verified_on']) or 'Not recorded')}<br><span>{html.escape(str(item['verification_age_days']) if item['verification_age_days'] is not None else 'unknown')} days old</span></td>"
            f"<td>{html.escape(str(item['source_recheck_by']) or 'Not set')}<br><span>{html.escape(str(item['source_recheck_days_overdue']) if item['source_recheck_days_overdue'] is not None else 'unknown')} days overdue</span></td>"
            f"<td>{html.escape(str(item['source_recheck_owner']))}</td>"
            f"<td>{html.escape(str(item['routing_gate']))}</td>"
            f"<td>{html.escape(str(item['verification_focus']))}</td>"
            "</tr>"
        )
    return f"""
    <section class="panel">
      <div class="section-heading"><p class="eyebrow">Source Recheck Queue</p><h2>Verify before outreach</h2></div>
      <div class="table-wrap"><table class="report-table">
        <thead><tr><th>Status</th><th>Opportunity</th><th>Last checked</th><th>Recheck due</th><th>Owner</th><th>Routing gate</th><th>Verification focus</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table></div>
    </section>
"""


def render_site_page(opportunities, matches, actions: dict[str, dict[str, str]], timeline_svg: str, as_of: date) -> str:
    top = top_matches_by_opportunity(matches)
    summary = build_screening_summary(opportunities, matches, actions, as_of)
    active = active_opportunities(opportunities, actions, as_of)
    passed_deadline_section = render_passed_deadlines(opportunities, matches, actions, as_of)
    source_recheck_section = render_source_recheck_queue(opportunities, actions, as_of)
    rows = []
    for opp in sort_opportunities(active, actions):
        evidence = match_evidence_html(top.get(opp.id, [])[:3])
        rows.append(
            "<tr>"
            f"<td><span class=\"status-pill {html.escape(status_class(action_status(opp, actions, as_of)))}\">{html.escape(action_status(opp, actions, as_of).title())}</span></td>"
            f"<td><a href=\"{html.escape(opp.source_url)}\">{html.escape(opp.program)}</a><br><span>{html.escape(opp.sponsor)}</span></td>"
            f"<td>{deadline_html(opp, actions, as_of)}</td>"
            f"<td>{verification_html(opp, actions, as_of)}</td>"
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
        <article><span>{summary['active_opportunity_count']}</span><p>Active opportunities</p><strong>{summary['opportunity_count']} total screened</strong></article>
        <article><span>{summary['nearest_deadline_days']}</span><p>Days to nearest dated deadline</p><strong>{html.escape(summary['nearest_deadline_program'])}</strong></article>
        <article><span>{summary['past_due_count']}</span><p>Passed public deadlines</p><strong>Move out of active routing</strong></article>
        <article><span>{summary['source_recheck_count']}</span><p>Need source recheck</p><strong>{summary['source_recheck_overdue_count']} overdue; {summary['faculty_outreach_blocked_count']} block outreach</strong></article>
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
        <thead><tr><th>Status</th><th>Opportunity</th><th>Public deadline</th><th>Source verification</th><th>Internal review</th><th>Match evidence</th><th>Next action</th><th>Risk notes</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table></div>
    </section>
{source_recheck_section}
{passed_deadline_section}
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
