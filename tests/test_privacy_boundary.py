from pathlib import Path


def test_public_site_and_repo_document_public_data_boundary():
    site = Path("site/index.html").read_text(encoding="utf-8")
    readme = Path("README.md").read_text(encoding="utf-8")
    private_workflow = Path("docs/private-local-workflow.md").read_text(encoding="utf-8")
    gitignore = Path(".gitignore").read_text(encoding="utf-8")

    assert "uses public sponsor records and public faculty or lab evidence only" in site
    assert "does not collect or request protected information" in site
    assert "Public Data Boundary" in readme
    assert "set the fork to private" in private_workflow
    assert "localhost:8000" in private_workflow
    assert "data/private/" in gitignore
    assert "site/private/" in gitignore
