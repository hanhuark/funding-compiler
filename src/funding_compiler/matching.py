from __future__ import annotations

from funding_compiler.loaders import normalize_keywords
from funding_compiler.models import FacultyProfile, MatchResult, Opportunity


def match_opportunities(
    opportunities: list[Opportunity],
    faculty: list[FacultyProfile],
    min_score: float = 0.1,
) -> list[MatchResult]:
    """Rank faculty matches for each opportunity."""

    results: list[MatchResult] = []
    for opportunity in opportunities:
        opportunity_terms = set(opportunity.keywords)
        if not opportunity_terms:
            opportunity_terms = set(normalize_keywords(opportunity.topic_summary))
        for profile in faculty:
            matched = sorted(opportunity_terms & _faculty_terms(profile))
            score = len(matched) / len(opportunity_terms) if opportunity_terms else 0.0
            if score >= min_score:
                results.append(
                    MatchResult(
                        opportunity_id=opportunity.id,
                        faculty_id=profile.id,
                        faculty_name=profile.name,
                        program=opportunity.program,
                        sponsor=opportunity.sponsor,
                        score=round(score, 3),
                        matched_keywords=matched,
                        rationale=_rationale(profile, opportunity, matched),
                    )
                )
    return sorted(results, key=lambda item: (item.opportunity_id, -item.score, item.faculty_name))


def _faculty_terms(profile: FacultyProfile) -> set[str]:
    text_terms = normalize_keywords(
        ";".join(
            [
                profile.research_interests,
                profile.capabilities,
                profile.facilities,
                profile.evidence,
            ]
        )
    )
    return set(profile.keywords) | set(text_terms)


def _rationale(profile: FacultyProfile, opportunity: Opportunity, matched: list[str]) -> str:
    if matched:
        terms = ", ".join(matched)
        return f"{profile.name} matches {opportunity.program} through shared terms: {terms}."
    return f"{profile.name} has no explicit keyword overlap with {opportunity.program}."
