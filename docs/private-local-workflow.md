# Private Fork and Local Personalization

## Public Repository Boundary

The public `funding-compiler` repository and GitHub Pages site use public sponsor records and public faculty or lab evidence only. They are not a channel for collecting protected information.

Do not add unpublished research plans, proposal drafts, nonpublic facility or equipment details, partner information, student information, controlled data, credentials, sponsor-restricted materials, or identifying derivatives to the public repository, GitHub issues, pull requests, GitHub Pages, or any public derived report.

## Private Local Workflow

1. Fork the repository into an account or organization you control and set the fork to private before adding any protected information.
2. Clone the private fork locally and install its dependencies.

```powershell
git clone <your-private-fork-url>
Set-Location funding-compiler
py -3.12 -m pip install -e ".[dev]"
```

3. Copy `examples/private-faculty.example.csv` to `data/private/faculty.csv`. The entire `data/private/` directory is ignored by Git in this project.
4. Add only the minimum information necessary for the local question. Record provenance and access restrictions alongside the data in your local process.
5. Run a local match or local screening. Do not put protected inputs in a GitHub Actions workflow or a hosted deployment.

```powershell
funding-compiler match `
  --opportunities examples/opportunities.csv `
  --faculty data/private/faculty.csv `
  --output outputs/private-match-report.md
```

6. To inspect the static dashboard locally, generate the site artifacts you intend to use and serve the `site/` directory only from localhost.

```powershell
py -3.12 -m http.server 8000 --directory site
```

Open `http://localhost:8000` in a browser on the same machine. Stop the server when finished with `Ctrl+C`.

## Before Commit or Deployment

Run these checks before any commit or publication:

```powershell
git status --ignored
git check-ignore -v data/private/faculty.csv
git diff --cached --name-only
```

`data/private/faculty.csv` should be reported as ignored. If any protected input or derived output appears in `git status` or the staged file list, remove it from the commit and keep it local. A private repository protects access but does not make it appropriate to publish restricted material through Pages or share it beyond its authorized audience.
