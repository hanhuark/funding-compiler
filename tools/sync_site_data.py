from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from funding_compiler.faculty_sources import load_faculty_sources
from funding_compiler.sources import load_funding_sources


def main() -> int:
    output_dir = Path("site/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "funding_sources.json").write_text(
        json.dumps(
            {"sources": [asdict(source) for source in load_funding_sources("data/funding_sources.yaml")]},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / "faculty_sources.json").write_text(
        json.dumps(
            {
                "sources": [
                    asdict(source)
                    for source in load_faculty_sources("data/uark_meeg_faculty_sources.yaml")
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
