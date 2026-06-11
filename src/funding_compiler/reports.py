from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from funding_compiler.models import MatchResult, Opportunity


def render_match_report(opportunities: list[Opportunity], matches: list[MatchResult]) -> str:
    """Render a Markdown report for opportunity-faculty alignment."""

    by_opportunity: dict[str, list[MatchResult]] = defaultdict(list)
    for match in matches:
        by_opportunity[match.opportunity_id].append(match)

    lines = [
        "# Funding Opportunity Match Report",
        "",
        f"Opportunities reviewed: {len(opportunities)}",
        f"Faculty matches found: {len(matches)}",
        "",
    ]
    for opportunity in opportunities:
        lines.extend(
            [
                f"## {opportunity.program}",
                "",
                f"- Sponsor: {opportunity.sponsor}",
                f"- Type: {opportunity.opportunity_type}",
                f"- Deadline: {opportunity.deadline}",
                f"- Award amount: {opportunity.award_amount}",
                f"- Eligibility: {opportunity.eligibility}",
                f"- Source: {opportunity.source_url or 'Not provided'}",
                "",
                opportunity.topic_summary,
                "",
                "| Rank | Faculty | Score | Matched keywords | Rationale |",
                "| --- | --- | ---: | --- | --- |",
            ]
        )
        ranked = by_opportunity.get(opportunity.id, [])
        if not ranked:
            lines.append("| - | No matches above threshold | 0.000 | - | Review manually |")
        for index, match in enumerate(ranked, start=1):
            keywords = ", ".join(match.matched_keywords) if match.matched_keywords else "-"
            lines.append(
                f"| {index} | {match.faculty_name} | {match.score:.3f} | {keywords} | {match.rationale} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_match_report(path: str | Path, opportunities: list[Opportunity], matches: list[MatchResult]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_match_report(opportunities, matches), encoding="utf-8")
    return output
