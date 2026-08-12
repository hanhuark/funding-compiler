# Data Schemas

The MVP accepts CSV and YAML files. CSV files should use the headers below.

## Funding Opportunities

| Field | Description |
| --- | --- |
| `id` | Stable opportunity identifier. |
| `sponsor` | Agency, foundation, company, or program sponsor. |
| `program` | Funding program or call name. |
| `opportunity_type` | RFP, NOFO, FOA, solicitation, prize, or similar. |
| `deadline` | Submission or concept paper deadline. |
| `award_amount` | Expected award size or range. |
| `eligibility` | Eligible applicants or major constraints. |
| `topic_summary` | Short description of the opportunity. |
| `keywords` | Semicolon-delimited keywords. |
| `source_url` | Source page or announcement URL. |
| `notes` | Public curation notes only in this repository. |

## Screening Action Metadata

Curated screening folders may include an `opportunity_actions.yaml` sidecar. This keeps sponsor facts in the opportunity CSV separate from local planning judgment.

| Field | Description |
| --- | --- |
| `deadline_type` | Deadline semantics: `fixed`, `window`, `rolling`, or `accepted_anytime`. |
| `display_deadline` | Optional faculty-facing deadline label when the raw date is a window close date or placeholder. |
| `verified_on` | Date the sponsor page or source evidence was last checked; this is separate from the report refresh date. |
| `source_recheck_owner` | Person or role responsible for the next sponsor-source verification. |
| `source_recheck_by` | Date by which the sponsor-source recheck should be completed. |
| `source_recheck_focus` | Program-specific checklist for the recheck, such as deadline, eligibility, cost-share, partner, or routing details. |
| `internal_review_by` | Suggested local go/no-go or routing date before the public sponsor deadline. |
| `decision_stage` | Short workflow state, such as eligibility screen, team formation, or partner watch. |
| `next_action` | Concrete action a research development lead or faculty member should take next. |
| `risk_notes` | Eligibility, cost share, partner, limited-submission, or fit concerns that should be checked before outreach. |

The generated screening report uses this sidecar to distinguish real deadlines from rolling programs, show current days remaining, flag stale sponsor-source verification, and build the faculty-facing action inbox.

Generated screening artifacts also include:

| File | Description |
| --- | --- |
| `site/data/screening_summary.json` | Homepage summary with snapshot date, refresh date, active opportunity count, passed-deadline count, nearest active deadline, urgent action count, emergency-runway count, do-not-start count, expedited go/no-go count, source recheck count, overdue source recheck count, faculty outreach block count, oldest active verification age, verification staleness threshold, and rolling-item count. |
| `site/data/faculty_action_summary.json` | Per-faculty opportunity brief data with status, deadline context, outreach readiness, routing gate, source recheck requirement, verification focus, proposal runway, proposal runway reason, fit level, score, matched terms, and next action. |
| `site/data/source_recheck_queue.json` | Operational worklist for active opportunities needing source recheck, including owner, recheck due date, overdue days, routing gate, proposal runway, verification focus, and deadline context. |
| `docs/screenings/*/alignment_matrix.csv` | Match matrix with score, fit level, matched keyword count, matched terms, and rationale. |
| `site/data/proposal_campaigns.json` | Proposal-campaign board with sponsor-evidence scope, MEEG lanes, eligibility and scientific-fit dispositions, team gaps, next decision, and clearly limited keyword-screening evidence. |

## Proposal Campaign Metadata

Each screening may include `proposal_campaigns.yaml`. These records are local planning judgments and must not be presented as sponsor facts, a faculty commitment, or a final eligibility determination.

| Field | Description |
| --- | --- |
| `official_source_url` | Direct official sponsor record used to verify the opportunity. |
| `sponsor_evidence_scope` | Sponsor facts that must be checked before routing. |
| `eligibility_disposition` | Explicit screening state; use `manual review required` until verified. |
| `scientific_fit_disposition` | Scientific-centrality judgment, separate from keyword overlap. |
| `meeg_lanes` | Controlled MEEG planning lanes such as `thermal-fluids`, `diagnostics-ai`, `energy-systems`, `advanced-manufacturing`, `materials`, `robotics-controls`, and `aerospace-systems`. |
| `campaign_status` | Local phase such as eligibility screen, concept shaping, team formation, or recurrence watch. |
| `concept_owner` | Assigned owner, or `Unassigned`; do not infer a commitment. |
| `proposed_roles` | Capabilities needed for a credible team. |
| `team_gap` | Missing capability, partner, facility, or commitment that blocks a viable campaign. |
| `next_decision` | Smallest specific go/no-go decision required before drafting. |

The generated campaign board automatically blocks a campaign when sponsor-source verification is stale, and labels keyword matches as screening evidence only.

## Faculty Profiles

| Field | Description |
| --- | --- |
| `id` | Stable faculty identifier. |
| `name` | Faculty member name. |
| `title` | Academic title. |
| `department` | Department name. |
| `institution` | Institution name. |
| `research_interests` | Short research interest summary. |
| `capabilities` | Methods, tools, or technical capabilities. |
| `facilities` | Publicly described labs, equipment, or infrastructure only; leave blank rather than inferring or requesting protected details. |
| `keywords` | Semicolon-delimited expertise tags. |
| `profile_url` | Public faculty profile URL. |
| `evidence` | Optional public evidence snippet from profiles, papers, or awards. |

The public repository must contain public information only. Protected inputs can be used only in a private fork under the ignored `data/private/` path, and their derived reports must remain local. See `docs/private-local-workflow.md`.

## Faculty Sources

Faculty source registries, such as `data/uark_meeg_faculty_sources.yaml`, track where profile evidence comes from before it is normalized into faculty profile records.

| Field | Description |
| --- | --- |
| `id` | Stable source identifier. |
| `name` | Directory, profile, lab, or source name. |
| `kind` | Source type such as `faculty directory`, `faculty profile`, or `lab website`. |
| `url` | Public URL for the source. |
| `owners` | Faculty member names associated with the source. |
| `department` | Department name. |
| `institution` | Institution name. |
| `focus_areas` | Semicolon- or YAML-list research themes inferred from the source. |
| `evidence_type` | Type of evidence, such as official directory or lab website. |
| `notes` | Curation notes. |
