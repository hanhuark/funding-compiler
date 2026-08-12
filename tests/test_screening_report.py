import json
from pathlib import Path

from tools.generate_screening_report import main


def test_generate_current_screening_outputs_actionable_august_snapshot(monkeypatch):
    monkeypatch.setenv("FUNDING_COMPILER_TODAY", "2026-08-12")

    assert main() == 0

    report = Path("docs/screenings/2026-08-12/funding-screening-report.md")
    timeline = Path("docs/screenings/2026-08-12/timeline.svg")
    alignment = Path("docs/screenings/2026-08-12/alignment_matrix.csv")
    site_page = Path("site/screenings/2026-08-12.html")
    summary = Path("site/data/screening_summary.json")
    faculty_summary = Path("site/data/faculty_action_summary.json")
    source_recheck_queue = Path("site/data/source_recheck_queue.json")
    campaign_board = Path("site/data/proposal_campaigns.json")

    assert all(path.exists() for path in [
        report,
        timeline,
        alignment,
        site_page,
        summary,
        faculty_summary,
        source_recheck_queue,
        campaign_board,
    ])

    report_text = report.read_text(encoding="utf-8")
    site_text = site_page.read_text(encoding="utf-8")
    alignment_text = alignment.read_text(encoding="utf-8")
    summary_data = json.loads(summary.read_text(encoding="utf-8"))
    faculty_summary_data = json.loads(faculty_summary.read_text(encoding="utf-8"))
    source_recheck_data = json.loads(source_recheck_queue.read_text(encoding="utf-8"))
    campaign_board_data = json.loads(campaign_board.read_text(encoding="utf-8"))

    assert "Snapshot date: 2026-08-12" in report_text
    assert "Samsung Global Research Outreach 2026" in report_text
    assert "Unlocking the Potential of Data for AI-Enabled Scientific Discovery" in report_text
    assert "FY 2027 Defense University Research Instrumentation Program" in report_text
    assert "EPSCoR E-RISE and E-CORE Planning Proposals" in report_text
    assert "Proposal Campaign Board" in report_text
    assert "Keyword overlap is screening evidence only" in report_text
    assert "August 12, 2026" in site_text
    assert "Sponsor pages remain authoritative" in site_text
    assert "Needs Eligibility Confirmation" in site_text
    assert "fit_level" in alignment_text

    assert summary_data["snapshot_date"] == "2026-08-12"
    assert summary_data["refreshed_on"] == "2026-08-12"
    assert summary_data["report_url"] == "screenings/2026-08-12.html"
    assert summary_data["opportunity_count"] == 11
    assert summary_data["active_opportunity_count"] == 11
    assert summary_data["source_recheck_count"] == 0
    assert summary_data["nearest_deadline_program"] == "Samsung Global Research Outreach 2026"
    assert summary_data["nearest_deadline_days"] == 11
    assert source_recheck_data == []

    assert len(campaign_board_data["records"]) == 11
    samsung_campaign = next(
        item for item in campaign_board_data["records"]
        if item["opportunity_id"] == "opp-samsung-gro-2026"
    )
    assert samsung_campaign["campaign_readiness"] == "needs eligibility confirmation"
    assert "agreement" in samsung_campaign["eligibility_disposition"]
    assert all(not item["source_recheck_required"] for item in campaign_board_data["records"])
    assert any(
        item["campaign_readiness"] == "blocked by partner eligibility"
        for item in campaign_board_data["records"]
    )
    assert any(record["faculty_name"] == "Han Hu" for record in faculty_summary_data)
