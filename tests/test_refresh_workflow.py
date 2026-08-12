from pathlib import Path


def test_manual_refresh_workflow_generates_and_publishes_screening_artifacts():
    workflow = Path(".github/workflows/refresh-screening.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "FUNDING_COMPILER_TODAY" in workflow
    assert "python tools/generate_screening_report.py" in workflow
    assert "git diff --check" in workflow
    assert "git add docs/screenings site/data site/screenings" in workflow
    assert "git push" in workflow


def test_dashboard_links_maintainers_to_manual_refresh_workflow():
    dashboard = Path("site/index.html").read_text(encoding="utf-8")

    assert "Run screening" in dashboard
    assert "actions/workflows/refresh-screening.yml" in dashboard
