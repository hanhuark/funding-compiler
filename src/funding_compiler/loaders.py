from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable

import yaml

from funding_compiler.models import FacultyProfile, Opportunity


def normalize_keywords(value: str | Iterable[str] | None) -> list[str]:
    """Normalize semicolon, comma, or list keyword fields."""

    if value is None:
        return []
    if isinstance(value, str):
        raw_items = value.replace(",", ";").split(";")
    else:
        raw_items = [str(item) for item in value]
    seen: set[str] = set()
    keywords: list[str] = []
    for item in raw_items:
        keyword = " ".join(item.strip().lower().split())
        if keyword and keyword not in seen:
            seen.add(keyword)
            keywords.append(keyword)
    return keywords


def load_opportunities(path: str | Path) -> list[Opportunity]:
    rows = _load_records(path)
    return [
        Opportunity(
            id=str(row.get("id", "")).strip(),
            sponsor=str(row.get("sponsor", "")).strip(),
            program=str(row.get("program", "")).strip(),
            opportunity_type=str(row.get("opportunity_type", "")).strip(),
            deadline=str(row.get("deadline", "")).strip(),
            award_amount=str(row.get("award_amount", "")).strip(),
            eligibility=str(row.get("eligibility", "")).strip(),
            topic_summary=str(row.get("topic_summary", "")).strip(),
            keywords=normalize_keywords(row.get("keywords")),
            source_url=str(row.get("source_url", "")).strip(),
            notes=str(row.get("notes", "")).strip(),
        )
        for row in rows
    ]


def load_faculty(path: str | Path) -> list[FacultyProfile]:
    rows = _load_records(path)
    return [
        FacultyProfile(
            id=str(row.get("id", "")).strip(),
            name=str(row.get("name", "")).strip(),
            title=str(row.get("title", "")).strip(),
            department=str(row.get("department", "")).strip(),
            institution=str(row.get("institution", "")).strip(),
            research_interests=str(row.get("research_interests", "")).strip(),
            capabilities=str(row.get("capabilities", "")).strip(),
            facilities=str(row.get("facilities", "")).strip(),
            keywords=normalize_keywords(row.get("keywords")),
            profile_url=str(row.get("profile_url", "")).strip(),
            evidence=str(row.get("evidence", "")).strip(),
        )
        for row in rows
    ]


def _load_records(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if source.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(source.read_text(encoding="utf-8")) or []
        if isinstance(data, dict):
            data = data.get("records", [])
        return [dict(row) for row in data]
    with source.open(newline="", encoding="utf-8-sig") as handle:
        return [dict(row) for row in csv.DictReader(handle)]
