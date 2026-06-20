import json
from pathlib import Path

from tools.generate_screening_report import main


def test_generate_screening_report_outputs_expected_files(monkeypatch):
    monkeypatch.setenv("FUNDING_COMPILER_TODAY", "2026-06-20")

    assert main() == 0

    report = Path("docs/screenings/2026-06-11/funding-screening-report.md")
    timeline = Path("docs/screenings/2026-06-11/timeline.svg")
    alignment = Path("docs/screenings/2026-06-11/alignment_matrix.csv")
    site_page = Path("site/screenings/2026-06-11.html")
    summary = Path("site/data/screening_summary.json")

    assert report.exists()
    assert timeline.exists()
    assert alignment.exists()
    assert site_page.exists()
    assert summary.exists()

    report_text = report.read_text(encoding="utf-8")
    site_text = site_page.read_text(encoding="utf-8")
    summary_data = json.loads(summary.read_text(encoding="utf-8"))

    assert "Current Funding Opportunity Screening" in report_text
    assert "Faculty Action Inbox" in report_text
    assert "5 days remaining as of 2026-06-20" in report_text
    assert "Accepted anytime; no fixed deadline" in report_text
    assert "Critical Minerals &amp; Materials Accelerator Topic Area 2" in site_text
    assert "Sponsor pages remain authoritative" in site_text
    assert "Internal Review Overdue" in site_text
    assert summary_data["nearest_deadline_days"] == 5
    assert summary_data["overdue_internal_review_count"] == 1
    assert summary_data["rolling_count"] == 2
