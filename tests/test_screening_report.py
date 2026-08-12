import json
from pathlib import Path

from tools.generate_screening_report import main


def test_generate_screening_report_outputs_expected_files(monkeypatch):
    monkeypatch.setenv("FUNDING_COMPILER_TODAY", "2026-07-20")

    assert main() == 0

    report = Path("docs/screenings/2026-06-11/funding-screening-report.md")
    timeline = Path("docs/screenings/2026-06-11/timeline.svg")
    alignment = Path("docs/screenings/2026-06-11/alignment_matrix.csv")
    site_page = Path("site/screenings/2026-06-11.html")
    summary = Path("site/data/screening_summary.json")
    faculty_summary = Path("site/data/faculty_action_summary.json")
    source_recheck_queue = Path("site/data/source_recheck_queue.json")
    campaign_board = Path("site/data/proposal_campaigns.json")

    assert report.exists()
    assert timeline.exists()
    assert alignment.exists()
    assert site_page.exists()
    assert summary.exists()
    assert faculty_summary.exists()
    assert source_recheck_queue.exists()
    assert campaign_board.exists()

    report_text = report.read_text(encoding="utf-8")
    site_text = site_page.read_text(encoding="utf-8")
    alignment_text = alignment.read_text(encoding="utf-8")
    summary_data = json.loads(summary.read_text(encoding="utf-8"))
    faculty_summary_data = json.loads(faculty_summary.read_text(encoding="utf-8"))
    source_recheck_data = json.loads(source_recheck_queue.read_text(encoding="utf-8"))
    campaign_board_data = json.loads(campaign_board.read_text(encoding="utf-8"))

    assert "Current Funding Opportunity Screening" in report_text
    assert "Faculty Action Inbox" in report_text
    assert "Faculty Briefs" in report_text
    assert "Match evidence" in report_text
    assert "2 days remaining as of 2026-07-20" in report_text
    assert "Passed Deadlines" in report_text
    assert "passed 25 days ago as of 2026-07-20" in report_text
    assert "Source Recheck Queue" in report_text
    assert "Last checked 2026-06-11; 39 days old; recheck before action" in report_text
    assert "Active dated deadlines within 7 days: 2" in report_text
    assert "Do not start new-proposal items: 2" in report_text
    assert "Active opportunities needing sponsor-source recheck: 9" in report_text
    assert "Source rechecks overdue: 9" in report_text
    assert "Faculty outreach blocked pending source recheck: 4" in report_text
    assert "Readiness gate" in report_text
    assert "Source recheck by 2026-06-25; 25 days overdue." in report_text
    assert "do not start new proposal" in report_text
    assert "Public deadline is 2 days away" in report_text
    assert "Research development lead" in report_text
    assert "Proposal Campaign Board" in report_text
    assert "Keyword overlap is screening evidence only" in report_text
    assert "Block faculty outreach until source and internal-review status are rechecked." in report_text
    assert "Accepted anytime; no fixed deadline" in report_text
    assert "Critical Minerals &amp; Materials Accelerator Topic Area 2" in site_text
    assert "Sponsor pages remain authoritative" in site_text
    assert "Past Due" in site_text
    assert "Needs Recheck" in site_text
    assert "Verify before outreach" in site_text
    assert "Outreach Blocked" in site_text
    assert "Do Not Start New Proposal" in site_text
    assert "Archive, do not route" in site_text
    assert "Who should look at what" in site_text
    assert "Scientific fit, eligibility, and team gaps before drafting" in site_text
    assert "Strong fit; score 0.600" in site_text
    assert "fit_level" in alignment_text
    assert summary_data["active_opportunity_count"] == 9
    assert summary_data["past_due_count"] == 1
    assert summary_data["nearest_deadline_days"] == 2
    assert summary_data["overdue_internal_review_count"] == 4
    assert summary_data["near_deadline_count"] == 2
    assert summary_data["do_not_start_count"] == 2
    assert summary_data["expedited_go_no_go_count"] == 0
    assert summary_data["emergency_runway_days"] == 7
    assert summary_data["source_recheck_count"] == 9
    assert summary_data["source_recheck_overdue_count"] == 9
    assert summary_data["faculty_outreach_blocked_count"] == 4
    assert summary_data["oldest_verification_age_days"] == 39
    assert summary_data["verification_stale_after_days"] == 14
    assert summary_data["rolling_count"] == 2
    assert len(source_recheck_data) == 9
    assert source_recheck_data[0]["program"] == "Faculty Early Career Development Program (CAREER)"
    assert source_recheck_data[0]["source_recheck_by"] == "2026-06-25"
    assert source_recheck_data[0]["source_recheck_days_overdue"] == 25
    assert source_recheck_data[0]["routing_gate"].startswith("Block")
    assert source_recheck_data[0]["proposal_runway"] == "do not start new proposal"
    assert "do not recruit faculty" in source_recheck_data[0]["proposal_runway_reason"]
    assert "PI eligibility" in source_recheck_data[0]["verification_focus"]
    assert all(
        "outreach_readiness" in item and "routing_gate" in item and "proposal_runway" in item
        for record in faculty_summary_data
        for item in record["priority_opportunities"]
    )
    assert len(campaign_board_data["records"]) == 10
    cdse_campaign = next(
        item for item in campaign_board_data["records"]
        if item["opportunity_id"] == "opp-nsf-cdse-cbet-cmmi-2026"
    )
    assert "diagnostics-ai" in cdse_campaign["meeg_lanes"]
    assert cdse_campaign["campaign_readiness"] == "blocked by source verification"
    assert "scientific centrality" in cdse_campaign["match_evidence_limit"]
    assert any(
        item["proposal_runway"] == "do not start new proposal"
        for record in faculty_summary_data
        for item in record["priority_opportunities"]
    )
    assert any(record["faculty_name"] == "Han Hu" for record in faculty_summary_data)
    assert all(
        item["program"] != "Critical Minerals & Materials Accelerator Topic Area 2"
        for record in faculty_summary_data
        for item in record["priority_opportunities"]
    )
