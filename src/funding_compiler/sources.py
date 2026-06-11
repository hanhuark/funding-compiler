from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from funding_compiler.loaders import normalize_keywords
from funding_compiler.models import FundingSource


def load_funding_sources(path: str | Path) -> list[FundingSource]:
    """Load a curated registry of funding source portals."""

    source_path = Path(path)
    data = yaml.safe_load(source_path.read_text(encoding="utf-8")) or []
    records = data.get("sources", data) if isinstance(data, dict) else data
    return [_source_from_record(record) for record in records]


def sources_by_category(sources: list[FundingSource]) -> dict[str, list[FundingSource]]:
    grouped: dict[str, list[FundingSource]] = defaultdict(list)
    for source in sources:
        grouped[source.category].append(source)
    return dict(sorted(grouped.items()))


def _source_from_record(record: dict[str, Any]) -> FundingSource:
    return FundingSource(
        id=str(record.get("id", "")).strip(),
        name=str(record.get("name", "")).strip(),
        category=str(record.get("category", "")).strip(),
        sponsor_type=str(record.get("sponsor_type", "")).strip(),
        url=str(record.get("url", "")).strip(),
        access=str(record.get("access", "public")).strip(),
        opportunity_types=normalize_keywords(record.get("opportunity_types")),
        focus_areas=normalize_keywords(record.get("focus_areas")),
        refresh_hint=str(record.get("refresh_hint", "")).strip(),
        notes=str(record.get("notes", "")).strip(),
    )
