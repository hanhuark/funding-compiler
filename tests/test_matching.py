from funding_compiler.loaders import load_faculty, load_opportunities
from funding_compiler.matching import match_opportunities


def test_relevant_faculty_rank_above_unrelated_faculty():
    opportunities = load_opportunities("examples/opportunities.csv")
    faculty = load_faculty("examples/faculty.csv")

    matches = match_opportunities([opportunities[0]], faculty, min_score=0.1)

    assert matches[0].faculty_name == "Han Hu"
    assert matches[0].score > matches[-1].score
    assert "thermal management" in matches[0].matched_keywords
