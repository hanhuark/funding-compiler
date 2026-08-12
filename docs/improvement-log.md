# Improvement Log

This log supports the recurring faculty-perspective improvement workflow. Each run should compare its critique against the prior entry; repeated concerns mean the previous implementation was not deep enough.

## 2026-08-12 - Faculty-grade campaign decision workflow

### Comparison With Prior Run

- Earlier cycles correctly added freshness, routing, and proposal-runway gates, but all still began with a keyword match and ended before a proposal campaign could be judged credible.
- This is a deeper follow-through on the repeated adoption concern: it introduces structured evidence, eligibility, scientific-fit, team-gap, and decision fields instead of another dashboard warning.

### Faculty-Perspective Critique

- A MEEG faculty member needs to know whether a call is real and current, whether the proposed research is central to the solicitation, whether a plausible team exists, and what decision is needed next.
- Literal keyword overlap can surface leads but must never be interpreted as scientific fit, eligibility, or commitment.
- A public dashboard must make its local planning judgments visibly distinct from official sponsor evidence and private faculty-interest information.

### Changes Made

- Added a proposal campaign record for every screened opportunity with official sponsor record, evidence scope, MEEG lane, eligibility and scientific-fit disposition, team gap, concept-owner state, required roles, and next decision.
- Added generated campaign-board JSON, a dashboard campaign board with MEEG-lane filtering, and a report table that exposes the gates before proposal work is requested.
- Made stale sponsor verification automatically block campaign readiness and labeled keyword matches as screening evidence only.
- Updated the README and workflow/schema documentation to define the campaign decision boundary and protect against unsupported eligibility or faculty-commitment claims.

### Validation Notes

- Generated artifacts should be refreshed with a fixed `FUNDING_COMPILER_TODAY` value for reproducible tests, then with the current date for operational use.

## 2026-07-20 - Day 7

### Comparison With Prior Run

- Day 6 pushed source gates into per-faculty briefs so matched opportunities no longer looked automatically outreach-ready.
- The Day 7 critique is related but more time-sensitive: with CAREER two days away and CMMA Topic Area 3 three days away, faculty need proposal-runway triage, not only source/outreach gating.
- The live GitHub Pages site remains stale. It still shows the pre-Day-1 June 11 view and does not include the local source-gate or proposal-runway improvements because local commits have not been pushed or deployed.

### Faculty-Perspective Critique

- A faculty member should not be recruited into a new proposal when a deadline is only days away and source/internal gates are unresolved.
- The report should distinguish "do not start a new proposal" from "verify before planning" and "blocked until gate cleared."
- Homepage metrics should surface near-deadline proposal-runway risk alongside stale-source and outreach-block counts.
- Staff and faculty JSON should preserve proposal-runway decisions so downstream dashboards, emails, or briefings do not strip this go/no-go signal.

### Changes Made

- Added proposal-runway decisions with `do not start new proposal`, `emergency only`, `blocked until gate cleared`, `expedited go/no-go`, `verify before planning`, `standing program`, and `normal planning` states.
- Added proposal-runway reasons to the active action inbox, source recheck queue, per-faculty summaries, web Faculty Briefs, and generated JSON.
- Added summary counts for near-deadline items, do-not-start items, expedited go/no-go items, and runway thresholds.
- Added homepage and report styling for proposal-runway badges.
- Refreshed generated artifacts and tests for the 2026-07-20 screening state.

### Validation Notes

- Generated artifacts were refreshed with `FUNDING_COMPILER_TODAY=2026-07-20`.
- Tests should be run with Python 3.12 because the project requires Python >=3.10.

## 2026-07-05 - Day 6

### Comparison With Prior Run

- Day 5 converted stale source checks into an operational staff worklist with owner, due date, overdue days, routing gate, and verification focus.
- The Day 6 critique still overlaps source gating, which means the prior fix was not deep enough at the faculty-facing layer: faculty briefs could still read like proposal-action recommendations without showing the same outreach readiness gate.
- The live GitHub Pages site remains stale. It still shows the pre-Day-1 June 11 view, including 14 days to the now-passed June 25 CMMA Topic Area 2 deadline, because local commits have not been pushed or deployed.

### Faculty-Perspective Critique

- Faculty should not have to cross-reference a staff worklist to know whether a matched opportunity is safe to act on.
- A per-faculty match should clearly distinguish "interesting fit" from "ready for outreach."
- Source-gated opportunities should show whether outreach is blocked or verification should happen first, along with the recheck due date and verification focus.
- Faculty-facing JSON should preserve those readiness fields so downstream dashboards or emails do not strip the gate.

### Changes Made

- Added an `outreach_readiness` model with `outreach blocked`, `verify first`, and `ready after normal review` states.
- Added routing gate, source recheck due date, overdue days, verification focus, and recheck-required fields to `site/data/faculty_action_summary.json`.
- Expanded Markdown and web Faculty Briefs with readiness gates and source recheck context beside each matched opportunity.
- Added report styling for outreach readiness badges and updated schema/workflow docs.
- Refreshed generated artifacts and tests for the 2026-07-05 screening state.

### Validation Notes

- Generated artifacts were refreshed with `FUNDING_COMPILER_TODAY=2026-07-05`.
- Tests should be run with Python 3.12 because the project requires Python >=3.10.

## 2026-07-02 - Day 5

### Comparison With Prior Run

- Day 4 added source verification age, stale-source summary metrics, and a source recheck queue.
- The Day 5 critique overlaps Day 4 on data freshness, which means the prior change was not deep enough operationally: it showed that sources needed recheck but did not define ownership, due dates, routing gates, or the specific checks needed to clear each item.
- The live GitHub Pages site remains stale. It still shows the pre-Day-1 static June 11 deadline math, including the June 25 CMMA Topic Area 2 item as urgent, because local commits have not been pushed or deployed.

### Faculty-Perspective Critique

- A faculty member deciding whether to act needs to know not only that a source is stale, but whether outreach is blocked until staff recheck sponsor text.
- Research development staff need an owner, due date, overdue count, and program-specific verification focus for each stale item.
- Near-term and internally overdue items should sort ahead of lower-urgency watchlist items in the source recheck queue.
- The homepage should distinguish source recheck volume from operational severity: overdue checks and outreach-blocking checks are different signals.

### Changes Made

- Added source recheck owner, due date, and verification focus metadata for each screening opportunity.
- Generated `site/data/source_recheck_queue.json` with status, deadline context, verification age, source recheck due date, overdue days, owner, routing gate, and verification focus.
- Expanded the Markdown and web source recheck queue into an operational worklist sorted by action urgency.
- Added summary fields for overdue source checks and faculty outreach blocked pending source recheck.
- Updated homepage copy, docs, generated artifacts, and tests for the operational source recheck workflow.

### Validation Notes

- Generated artifacts were refreshed with `FUNDING_COMPILER_TODAY=2026-07-02`.
- Tests should be run with Python 3.12 because the project requires Python >=3.10.

## 2026-06-29 - Day 4

### Comparison With Prior Run

- Day 3 addressed opportunity lifecycle handling by separating passed public deadlines from active faculty routing.
- The Day 4 critique is not the same lifecycle issue. The new issue is source verification age: as of 2026-06-29, active opportunities were last checked against sponsor pages on 2026-06-11, so the report needed to distinguish report refresh from sponsor-source verification before faculty outreach.
- The live GitHub Pages site remains stale because local commits have not been pushed or deployed. This remains an operations gap outside the local commit workflow requested by the automation.

### Faculty-Perspective Critique

- A faculty member should not infer that sponsor pages were rechecked just because the report was regenerated.
- Opportunities older than a reasonable verification window should be queued for source recheck before faculty are asked to spend proposal-planning time.
- The homepage should expose source-verification risk next to deadline urgency, active opportunity count, and passed-deadline count.
- Archived passed-deadline items should preserve source-verification context so recurrence reviews do not rely on stale assumptions.

### Changes Made

- Added source-verification age helpers and a 14-day stale-verification threshold to the screening report generator.
- Added source-verification status columns to the active action inbox and passed-deadline archive.
- Added a source recheck queue to the Markdown and web screening reports.
- Extended `site/data/screening_summary.json` and the homepage with source recheck count, oldest active verification age, and verification threshold fields.
- Updated reporting/schema docs and regression tests for the source-verification workflow.

### Validation Notes

- Generated artifacts were refreshed with `FUNDING_COMPILER_TODAY=2026-06-29`.
- Tests should be run with Python 3.12 because the project requires Python >=3.10.

## 2026-06-26 - Day 3

### Comparison With Prior Run

- Day 2 addressed evidence-backed matching and per-faculty "why me?" briefs.
- The Day 3 critique is not a repeat of that matching-evidence issue. The new issue is lifecycle handling: the June 25 CMMA Topic Area 2 deadline has now passed, so the tool must stop treating it as active faculty routing work.
- The live GitHub Pages site remains stale because local commits have not been pushed or deployed. This remains an operations gap outside the local commit workflow requested by the automation.

### Faculty-Perspective Critique

- A faculty member should not see an expired call mixed into the same active action inbox as submit-ready opportunities.
- Homepage metrics should distinguish active opportunities from total screened items and passed public deadlines.
- Per-faculty briefs should omit passed-deadline items so PIs are not nudged toward opportunities they can no longer act on.
- Passed opportunities should remain visible for lessons learned, recurrence tracking, and future-cycle planning.

### Changes Made

- Added lifecycle helpers for active versus past-due opportunities.
- Updated generated screening summary data with `active_opportunity_count` and `past_due_count`.
- Moved passed-deadline opportunities into a separate web/Markdown archive section.
- Updated faculty briefs to omit past-due opportunities while keeping match evidence in the archive.
- Updated homepage summary metrics, docs, and tests for the lifecycle behavior.

### Validation Notes

- Generated artifacts were refreshed with `FUNDING_COMPILER_TODAY=2026-06-26`.
- Tests should be run with Python 3.12 because the project requires Python >=3.10.

## 2026-06-23 - Day 2

### Comparison With Prior Run

- Day 1 addressed freshness, action status, deadline semantics, and web caveats in the local repo.
- The live GitHub Pages site still showed the old June 11 snapshot because the Day 1 commit had not been pushed or deployed. This is an operations/deployment gap, not evidence that the local Day 1 implementation was shallow.
- The remaining faculty adoption gap was different: the report named matched faculty but did not explain enough of the "why me?" evidence or provide a per-faculty view.

### Faculty-Perspective Critique

- Faculty need evidence-backed matches, not only names in a "top aligned" column.
- A PI scanning the report should be able to find their own name and see the highest-priority opportunities, matched terms, score strength, and next action.
- The alignment matrix should preserve fit labels and matched-term counts for downstream review, export, and calibration.
- Strong evergreen fits should remain visible in faculty views even when they do not have an urgent deadline.

### Changes Made

- Added fit-level labels and matched keyword counts to the generated alignment matrix.
- Added match-evidence text to the action inbox so top matches show fit strength, score, and matched terms.
- Generated `site/data/faculty_action_summary.json` for per-faculty opportunity briefs.
- Added a Faculty Briefs section to the web and Markdown screening reports.
- Updated report styling, docs, and tests to cover the evidence-backed matching and faculty brief outputs.

### Validation Notes

- Generated artifacts were refreshed with `FUNDING_COMPILER_TODAY=2026-06-23`.
- Tests should be run with Python 3.12 because the project requires Python >=3.10.

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
