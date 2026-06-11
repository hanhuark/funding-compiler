from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Opportunity:
    """A normalized funding opportunity record."""

    id: str
    sponsor: str
    program: str
    opportunity_type: str
    deadline: str
    award_amount: str
    eligibility: str
    topic_summary: str
    keywords: list[str] = field(default_factory=list)
    source_url: str = ""
    notes: str = ""


@dataclass(frozen=True)
class FacultyProfile:
    """A normalized faculty capability profile."""

    id: str
    name: str
    title: str
    department: str
    institution: str
    research_interests: str
    capabilities: str
    facilities: str
    keywords: list[str] = field(default_factory=list)
    profile_url: str = ""
    evidence: str = ""


@dataclass(frozen=True)
class MatchResult:
    """A ranked connection between one opportunity and one faculty member."""

    opportunity_id: str
    faculty_id: str
    faculty_name: str
    program: str
    sponsor: str
    score: float
    matched_keywords: list[str]
    rationale: str


@dataclass(frozen=True)
class FundingSource:
    """A monitored portal or directory where funding opportunities may appear."""

    id: str
    name: str
    category: str
    sponsor_type: str
    url: str
    access: str
    opportunity_types: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)
    refresh_hint: str = ""
    notes: str = ""
