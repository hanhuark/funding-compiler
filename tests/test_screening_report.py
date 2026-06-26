import json
from pathlib import Path

from tools.generate_screening_report import main


def test_generate_screening_report_outputs_expected_files(monkeypatch):
    monkeypatch.setenv("FUNDING_COMPILER_TODAY", "2026-06-26")

    assert main() == 0

    report = Path("docs/screenings/2026-06-11/funding-screening-report.md")
    timeline = Path("docs/screenings/2026-06-11/timeline.svg")
    alignment = Path("docs/screenings/2026-06-11/alignment_matrix.csv")
    site_page = Path("site/screenings/2026-06-11.html")
    summary = Path("site/data/screening_summary.json")
    faculty_summary = Path("site/data/faculty_action_summary.json")

    assert report.exists()
    assert timeline.exists()
    assert alignment.exists()
    assert site_page.exists()
    assert summary.exists()
    assert faculty_summary.exists()

    report_text = report.read_text(encoding="utf-8")
    site_text = site_page.read_text(encoding="utf-8")
    alignment_text = alignment.read_text(encoding="utf-8")
    summary_data = json.loads(summary.read_text(encoding="utf-8"))
    faculty_summary_data = json.loads(faculty_summary.read_text(encoding="utf-8"))

    assert "Current Funding Opportunity Screening" in report_text
    assert "Faculty Action Inbox" in report_text
    assert "Faculty Briefs" in report_text
    assert "Match evidence" in report_text
    assert "26 days remaining as of 2026-06-26" in report_text
    assert "Passed Deadlines" in report_text
    assert "passed 1 day ago as of 2026-06-26" in report_text
    assert "Accepted anytime; no fixed deadline" in report_text
    assert "Critical Minerals &amp; Materials Accelerator Topic Area 2" in site_text
    assert "Sponsor pages remain authoritative" in site_text
    assert "Past Due" in site_text
    assert "Archive, do not route" in site_text
    assert "Who should look at what" in site_text
    assert "Strong fit; score 0.600" in site_text
    assert "fit_level" in alignment_text
    assert summary_data["active_opportunity_count"] == 9
    assert summary_data["past_due_count"] == 1
    assert summary_data["nearest_deadline_days"] == 26
    assert summary_data["overdue_internal_review_count"] == 0
    assert summary_data["rolling_count"] == 2
    assert any(record["faculty_name"] == "Han Hu" for record in faculty_summary_data)
    assert all(
        item["program"] != "Critical Minerals & Materials Accelerator Topic Area 2"
        for record in faculty_summary_data
        for item in record["priority_opportunities"]
    )
