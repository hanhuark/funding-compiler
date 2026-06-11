from funding_compiler.loaders import load_faculty, load_opportunities, normalize_keywords


def test_normalize_keywords_splits_and_deduplicates():
    assert normalize_keywords(" Thermal fluids;AI, thermal fluids ;  ") == ["thermal fluids", "ai"]


def test_load_sample_opportunities():
    opportunities = load_opportunities("examples/opportunities.csv")

    assert opportunities[0].sponsor == "U.S. Department of Energy"
    assert "thermal management" in opportunities[0].keywords


def test_load_sample_faculty():
    faculty = load_faculty("examples/faculty.csv")

    assert faculty[0].institution == "University of Arkansas"
    assert "phase change heat transfer" in faculty[0].keywords
