from pathlib import Path

from tools.generate_screening_report import main


def test_generate_screening_report_outputs_expected_files():
    assert main() == 0

    report = Path("docs/screenings/2026-06-11/funding-screening-report.md")
    timeline = Path("docs/screenings/2026-06-11/timeline.svg")
    alignment = Path("docs/screenings/2026-06-11/alignment_matrix.csv")
    site_page = Path("site/screenings/2026-06-11.html")

    assert report.exists()
    assert timeline.exists()
    assert alignment.exists()
    assert site_page.exists()
    assert "Current Funding Opportunity Screening" in report.read_text(encoding="utf-8")
    assert "Critical Minerals &amp; Materials Accelerator Topic Area 2" in site_page.read_text(encoding="utf-8")
