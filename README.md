# funding-compiler

`funding-compiler` is a starter toolkit for compiling funding opportunities, summarizing faculty research capabilities, and aligning opportunities with faculty members who may be interested in leading or joining proposals.

The first version is intentionally transparent: local CSV data, a Python CLI, simple matching logic, tests, and Markdown reports that can be converted into one-pagers, detailed reports, slides, or dashboards later.

Project site: https://hanhuark.github.io/funding-compiler/

Latest screening report: https://hanhuark.github.io/funding-compiler/screenings/2026-06-11.html

## What It Does

1. **Compile funding opportunities** from federal agencies, state agencies, foundations, and private companies. Examples include RFPs, NOFOs, FOAs, solicitations, prize calls, and recurring programs.
2. **Summarize faculty capabilities** for a department, including research interests, methods, facilities, keywords, and profile links.
3. **Align opportunities with faculty** using a transparent keyword-overlap baseline that produces ranked matches and rationale text.

## Quick Start

```powershell
python -m pip install -e ".[dev]"
funding-compiler demo
```

The demo reads sample files in `examples/` and writes a Markdown report to `outputs/demo-report.md`.

## Example Workflow

```powershell
funding-compiler match `
  --opportunities examples/opportunities.csv `
  --faculty examples/faculty.csv `
  --output outputs/matches.md
```

List the curated source registry:

```powershell
funding-compiler sources
```

List faculty directory, profile, and lab sources for the UArk MEEG seed registry:

```powershell
funding-compiler faculty-sources
```

Regenerate the static dashboard JSON after editing registry YAML:

```powershell
$env:PYTHONPATH='src'
python tools/sync_site_data.py
```

## Repository Layout

- `src/funding_compiler/` - Python package and CLI.
- `site/` - Static GitHub Pages dashboard.
- `data/funding_sources.yaml` - Curated registry of funding portals and discovery sources.
- `data/uark_meeg_faculty_sources.yaml` - Seed registry for UArk MEEG faculty directories, profiles, and lab sites.
- `examples/` - Sample opportunity and faculty data.
- `docs/` - Architecture, data schema, and reporting workflow notes.
- `tests/` - Unit tests for loaders, matching, and reports.

## Current Matching Method

The MVP uses a readable scoring method:

- normalize keywords to lowercase;
- compare opportunity keywords to faculty keywords, interests, and capabilities;
- compute an overlap score from 0 to 1;
- generate rationale from matched terms.

This baseline is easy to audit and can later be extended with semantic embeddings, sponsor-specific rules, eligibility checks, and human review workflows.

## Planned Extensions

- API adapters for Grants.gov, SAM.gov, NSF, NIH, DOE, NASA, state portals, foundation pages, and company programs.
- Department profile importers from faculty pages, publication databases, CVs, and award histories.
- Excel workbooks, heatmaps, one-page PDFs, DOCX reports, and PowerPoint briefings.
- Scheduled refresh jobs and dashboard views.
- Human-in-the-loop review for match scores and proposal team recommendations.
