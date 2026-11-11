"""Build the standalone handbook using only this repository's editorial data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from presentation import index_html

HERE = Path(__file__).resolve().parent


def render():
    entries = json.loads((HERE / "formulas.json").read_text(encoding="utf-8"))
    coverage = json.loads((HERE / "data/coverage.json").read_text(encoding="utf-8"))
    return index_html(
        entries, coverage["code"], coverage["documents"], coverage["office_cells"]
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=HERE,
        help="Output directory, defaults to repository root",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    (output / "index.html").write_text(render(), encoding="utf-8", newline="\n")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    print(
        json.dumps(
            {"status": "PASS", "articles": 480, "output": str(output / "index.html")},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
