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
| `notes` | Optional internal notes. |

## Screening Action Metadata

Curated screening folders may include an `opportunity_actions.yaml` sidecar. This keeps sponsor facts in the opportunity CSV separate from local planning judgment.

| Field | Description |
| --- | --- |
| `deadline_type` | Deadline semantics: `fixed`, `window`, `rolling`, or `accepted_anytime`. |
| `display_deadline` | Optional faculty-facing deadline label when the raw date is a window close date or placeholder. |
| `verified_on` | Date the sponsor page or source evidence was last checked. |
| `internal_review_by` | Suggested local go/no-go or routing date before the public sponsor deadline. |
| `decision_stage` | Short workflow state, such as eligibility screen, team formation, or partner watch. |
| `next_action` | Concrete action a research development lead or faculty member should take next. |
| `risk_notes` | Eligibility, cost share, partner, limited-submission, or fit concerns that should be checked before outreach. |

The generated screening report uses this sidecar to distinguish real deadlines from rolling programs, show current days remaining, and build the faculty-facing action inbox.

Generated screening artifacts also include:

| File | Description |
| --- | --- |
| `site/data/screening_summary.json` | Homepage summary with snapshot date, refresh date, active opportunity count, passed-deadline count, nearest active deadline, urgent action count, and rolling-item count. |
| `site/data/faculty_action_summary.json` | Per-faculty opportunity brief data with status, deadline context, fit level, score, matched terms, and next action. |
| `docs/screenings/*/alignment_matrix.csv` | Match matrix with score, fit level, matched keyword count, matched terms, and rationale. |

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
| `facilities` | Labs, equipment, or unique infrastructure. |
| `keywords` | Semicolon-delimited expertise tags. |
| `profile_url` | Public faculty profile URL. |
| `evidence` | Optional evidence snippet from profiles, papers, or awards. |

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
