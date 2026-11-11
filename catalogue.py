"""The independent handbook category list."""

import json
from pathlib import Path

CATEGORIES = json.loads(
    (Path(__file__).resolve().parent / "categories.json").read_text(encoding="utf-8")
)
