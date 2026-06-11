from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from funding_compiler.loaders import normalize_keywords
from funding_compiler.models import FacultySource


def load_faculty_sources(path: str | Path) -> list[FacultySource]:
    """Load faculty profile, directory, and lab website source records."""

    source_path = Path(path)
    data = yaml.safe_load(source_path.read_text(encoding="utf-8")) or []
    records = data.get("sources", data) if isinstance(data, dict) else data
    return [_source_from_record(record) for record in records]


def faculty_sources_by_kind(sources: list[FacultySource]) -> dict[str, list[FacultySource]]:
    grouped: dict[str, list[FacultySource]] = defaultdict(list)
    for source in sources:
        grouped[source.kind].append(source)
    return dict(sorted(grouped.items()))


def _source_from_record(record: dict[str, Any]) -> FacultySource:
    return FacultySource(
        id=str(record.get("id", "")).strip(),
        name=str(record.get("name", "")).strip(),
        kind=str(record.get("kind", "")).strip(),
        url=str(record.get("url", "")).strip(),
        owners=_normalize_people(record.get("owners")),
        department=str(record.get("department", "")).strip(),
        institution=str(record.get("institution", "")).strip(),
        focus_areas=normalize_keywords(record.get("focus_areas")),
        evidence_type=str(record.get("evidence_type", "")).strip(),
        notes=str(record.get("notes", "")).strip(),
    )


def _normalize_people(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    raw_items = value.replace(",", ";").split(";") if isinstance(value, str) else value
    names: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        name = " ".join(str(item).strip().split())
        key = name.lower()
        if name and key not in seen:
            seen.add(key)
            names.append(name)
    return names
