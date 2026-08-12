from funding_compiler.sources import load_funding_sources, sources_by_category


def test_load_funding_source_registry_contains_user_sources():
    sources = load_funding_sources("data/funding_sources.yaml")
    names = {source.name for source in sources}

    assert "NSF Funding Search" in names
    assert "NASA NSPIRES Solicitations" in names
    assert "University of Arkansas InfoReady" in names
    assert "Arkansas Space Grant Consortium InfoReady" in names
    assert "NIST Funding Opportunities" in names
    assert "Samsung Global Research Outreach" in names
    assert "Sony Research Award Program" in names
    assert "PowerAmerica Project Calls" in names
    assert "Semiconductor Research Corporation Global Research Collaboration" in names
    assert "Walton Family Foundation Grant Proposals" in names


def test_source_registry_tracks_access_and_categories():
    sources = load_funding_sources("data/funding_sources.yaml")
    nsf = next(source for source in sources if source.id == "nsf-funding")

    assert nsf.category == "federal"
    assert nsf.access == "public"
    assert "engineering" in nsf.focus_areas


def test_sources_by_category_groups_registry_records():
    sources = load_funding_sources("data/funding_sources.yaml")
    grouped = sources_by_category(sources)

    assert "federal" in grouped
    assert "internal" in grouped
    assert "early career" in grouped
    assert "EPSCoR" in grouped
    assert "startup and commercialization" in grouped
    assert any(source.id == "uark-infoready" for source in grouped["internal"])


def test_relationship_gated_sources_preserve_access_constraints():
    sources = {source.id: source for source in load_funding_sources("data/funding_sources.yaml")}

    assert sources["poweramerica-rfp"].access == "membership or public call"
    assert sources["semiconductor-research-corporation"].access == "relationship-based"
    assert sources["walton-family-foundation-grant-proposals"].access == "letter of inquiry or invitation"
    assert "TIP" in sources["nsf-entrepreneurial-researchers-tip"].notes
