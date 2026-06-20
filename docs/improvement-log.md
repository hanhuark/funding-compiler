# Improvement Log

This log supports the recurring faculty-perspective improvement workflow. Each run should compare its critique against the prior entry; repeated concerns mean the previous implementation was not deep enough.

## 2026-06-20 - Day 1

### Faculty-Perspective Critique

- The public dashboard advertised a stale "days to nearest deadline" value from the June 11 snapshot, which could mislead a faculty member checking the site on June 20.
- The web screening page looked like a priority table, but not a decision surface: it lacked internal review dates, next actions, and risk notes.
- Rolling or accepted-anytime programs were forced into artificial date placeholders, making evergreen opportunities look like fixed-deadline calls.
- The Markdown report warned that sponsor pages remain authoritative, but the web report did not show that caveat.
- The repo had no durable record of critique-versus-implementation cycles for future scheduled runs.

### Changes Made

- Added `data/screenings/2026-06-11/opportunity_actions.yaml` to separate local planning judgment from sponsor opportunity facts.
- Updated `tools/generate_screening_report.py` to generate a faculty action inbox, current days remaining, deadline-type-aware timeline, internal review status, risk notes, and `site/data/screening_summary.json`.
- Updated the homepage to load generated screening summary data instead of relying only on hardcoded snapshot metrics.
- Added shared report styles for action tables, status pills, summary cards, and sponsor-authority notices.
- Updated schema/reporting docs and tests to cover action metadata, current deadline math, rolling opportunity semantics, and the web caveat.

### Validation Notes

- Python 3.12 was required because the default Anaconda Python was 3.9 and the project requires Python >=3.10.
- Dev dependencies were installed with `py -3.12 -m pip install -e ".[dev]"`.
- Generated artifacts were refreshed with `FUNDING_COMPILER_TODAY=2026-06-20`.
