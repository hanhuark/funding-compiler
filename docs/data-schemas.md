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
