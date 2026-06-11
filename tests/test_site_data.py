import json
from pathlib import Path

from funding_compiler.faculty_sources import load_faculty_sources
from funding_compiler.sources import load_funding_sources


def test_site_funding_json_matches_source_registry_ids():
    registry_ids = {source.id for source in load_funding_sources("data/funding_sources.yaml")}
    site_data = json.loads(Path("site/data/funding_sources.json").read_text(encoding="utf-8"))
    site_ids = {source["id"] for source in site_data["sources"]}

    assert site_ids == registry_ids


def test_site_faculty_json_matches_source_registry_ids():
    registry_ids = {source.id for source in load_faculty_sources("data/uark_meeg_faculty_sources.yaml")}
    site_data = json.loads(Path("site/data/faculty_sources.json").read_text(encoding="utf-8"))
    site_ids = {source["id"] for source in site_data["sources"]}

    assert site_ids == registry_ids
