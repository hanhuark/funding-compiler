# Faculty Expertise Intake

The public repository tracks only public faculty expertise sources separately from normalized public profiles. This keeps provenance visible and makes it easier to refresh profiles when department pages or lab sites change.

## UArk MEEG Sources

The seed registry lives in `data/uark_meeg_faculty_sources.yaml`.

It includes:

- the official Mechanical Engineering faculty and staff directory;
- Steve Tung's separate College of Engineering administration profile;
- lab websites compiled from the local `MEEG Labs.docx` file.

## CLI

```powershell
funding-compiler faculty-sources
```

The command prints faculty source records grouped by kind.

## Recommended Profile-Building Workflow

1. Use the official directory as the roster source.
2. Use profile pages to collect titles, contact information, and public research statements.
3. Use lab websites to collect only public capability evidence and public research themes.
4. Store normalized public profiles in a faculty CSV or YAML file.
5. Keep extracted claims traceable to a profile URL, lab URL, or document source.

## Notes

The source registry is not a final faculty expertise summary. It is the evidence map used to build and update public summaries. Do not ask faculty to provide private facility, equipment, project, proposal, partner, student, or restricted information for the public repository. A faculty member who wants a more personalized search should use a private fork and the local-only workflow in `docs/private-local-workflow.md`.
