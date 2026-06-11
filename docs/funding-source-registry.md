# Funding Source Registry

The source registry in `data/funding_sources.yaml` is a curated list of places to check for funding opportunities. It includes federal portals, aggregators, internal University of Arkansas sources, regional programs, and industry-partnership intelligence sources.

## Current Categories

- `federal` - Agency-specific funding pages and solicitation portals.
- `federal aggregator` - Cross-agency search tools such as Grants.gov, SAM.gov, and SBIR.gov.
- `aggregator` - Subscription or third-party funding databases.
- `internal` - University-managed internal competitions and limited submissions.
- `state or regional` - Arkansas or regional consortium sources.
- `industry partnership` - Sources that may reveal company collaboration or sponsored research opportunities.

## Suggested Review Cadence

Weekly checks are useful for high-volume federal portals such as NSF, NASA NSPIRES, DOE eXCHANGE, Grants.gov, SBIR.gov, and NIH. Monthly checks are usually enough for university, regional, and industry partnership sources unless a specific competition cycle is known.

## CLI

```powershell
funding-compiler sources
```

The command prints the registry grouped by category.

## Curation Notes

Some pages are direct opportunity lists. Others are discovery or relationship-building sources. For example, UIDP is tracked as an industry-partnership intelligence source, while SAM.gov is tracked because many BAAs and contract-style research solicitations appear there.
