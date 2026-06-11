# Contributing

Contributions should keep the workflow transparent and reproducible.

## Development

```powershell
python -m pip install -e ".[dev]"
python -m pytest
```

## Guidelines

- Add or update tests when changing loaders, matching, or report output.
- Keep sample data realistic but clearly marked as examples.
- Prefer clear schemas and documented assumptions over hidden automation.
- Keep matching rationale human-readable so reviewers can audit recommendations.
