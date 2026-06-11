from funding_compiler.loaders import load_faculty, load_opportunities
from funding_compiler.matching import match_opportunities
from funding_compiler.reports import render_match_report


def test_report_contains_opportunity_and_ranked_match():
    opportunities = load_opportunities("examples/opportunities.csv")
    faculty = load_faculty("examples/faculty.csv")
    matches = match_opportunities(opportunities, faculty, min_score=0.1)

    report = render_match_report(opportunities, matches)

    assert "# Funding Opportunity Match Report" in report
    assert "Advanced Energy Systems" in report
    assert "| 1 | Han Hu |" in report
