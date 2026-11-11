"""Validate mathematical snapshot integrity and the generated standalone page."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from build import render
from catalogue import CATEGORIES
from learning_examples import BY_ARTICLE, PRIMARY_RESULTS
from provenance import SOURCE_POSITION, reference_text
from statuses import STATUSES

HERE = Path(__file__).resolve().parent
LOCAL_ADDRESS = re.compile(
    r"file:/{2,3}|(?<!\w)[A-Za-z]:[\\/]|(?<!\w)(?:src|metall_mvp|mvp|docs|library|web|stock-selection|machining-calc)/[A-Za-z_]"
)


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.scripts = []
        self.script = None

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if data.get("id"):
            self.ids.append(data["id"])
        if tag == "a":
            self.links.append(data.get("href", ""))
        if tag == "script":
            self.script = {"type": data.get("type", "js"), "text": ""}
        if tag in {"input", "select"} and not data.get("name"):
            raise AssertionError("Form control without a name")
        if tag == "button" and not data.get("type"):
            raise AssertionError("Button without a type")

    def handle_data(self, text):
        if self.script is not None:
            self.script["text"] += text

    def handle_endtag(self, tag):
        if tag == "script" and self.script is not None:
            self.scripts.append(self.script)
            self.script = None


def main():
    entries = json.loads((HERE / "formulas.json").read_text(encoding="utf-8"))
    baseline = json.loads(
        (HERE / "data/content-baseline.json").read_text(encoding="utf-8")
    )
    text = (HERE / "index.html").read_text(encoding="utf-8")
    page = Page()
    page.feed(text)
    checks = []

    def check(name, condition):
        checks.append({"name": name, "passed": bool(condition)})

    check(
        "All 480 articles retained",
        len(entries) == 480 and len({e["id"] for e in entries}) == 480,
    )
    check(
        "All 19 categories retained",
        len(CATEGORIES) == 19
        and {e["category"] for e in entries} == {c[0] for c in CATEGORIES},
    )
    check(
        "All ten technical states retained",
        set(STATUSES) == {e["status"] for e in entries},
    )
    check(
        "Baseline covers exactly the complete catalogue",
        set(baseline["articles"]) == {e["id"] for e in entries},
    )
    for entry in entries:
        payload = json.dumps(
            {key: entry.get(key) for key in baseline["fields"]},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
        check(
            "Mathematical snapshot: " + entry["id"],
            hashlib.sha256(payload).hexdigest()
            == baseline["articles"].get(entry["id"]),
        )
        check(
            "Named source identity: " + entry["id"],
            bool(entry["provenance"])
            and [r["id"] for r in entry["source"]]
            == [p["id"] for p in entry["provenance"]]
            and all(
                p["title"]
                and p["kind_label"]
                and (p["kind"] != "code" or p["location"])
                for p in entry["provenance"]
            ),
        )
    references = [p for entry in entries for p in entry["provenance"]]
    check(
        "All 492 source references and 86 source identities retained",
        len(references) == 492 and len({p["id"] for p in references}) == 86,
    )
    check(
        "No raw source excerpts, positions or paths in public source references",
        all(set(r) == {"id"} for e in entries for r in e["source"]),
    )
    check(
        "All 138 versioned Go formula IDs retained",
        len({e["formula_id"] for e in entries if e.get("formula_id")}) == 138,
    )
    check(
        "Comparison groups retained",
        Counter(e["provenance_group"] for e in entries if e.get("provenance_group"))
        == {"research": 150, "teaching": 47, "control": 6},
    )
    check(
        "Original formula states retained",
        Counter(e["status"] for e in entries)
        == {
            "active": 186,
            "documented": 34,
            "conditional": 12,
            "library": 25,
            "archive": 7,
            "boundary": 2,
            "prepared": 10,
            "unverified": 1,
            "reference": 6,
            "comparison": 197,
        },
    )
    check("Generated page matches this repository's data", text == render())
    check("No duplicate DOM identifiers", len(page.ids) == len(set(page.ids)))
    for link in page.links:
        check(
            "Only valid in-page navigation: " + link,
            link.startswith("#") and link[1:] in page.ids,
        )
    visible = re.sub(r"<script\b.*?</script>", "", text, flags=re.DOTALL)
    check(
        "No local file addresses in the visible document",
        not LOCAL_ADDRESS.search(visible),
    )
    check("No source line or paragraph pointers", not SOURCE_POSITION.search(visible))
    check(
        "Source registry and offline/date status not restored",
        'id="origins"' not in text and "offline-state" not in text,
    )
    check(
        "All source citations remain in the formula cards",
        text.count('class="source-point"') == 492,
    )
    check(
        "All formulas retain visible notation",
        text.count('class="notation-panel"') == 480,
    )
    check(
        "Sixty mapped calculators stay visible",
        len(BY_ARTICLE) == 60
        and set(BY_ARTICLE) <= {e["id"] for e in entries}
        and set(PRIMARY_RESULTS) <= set(BY_ARTICLE)
        and text.count('<section class="learning-example"') == 60
        and '<details class="learning-example"' not in text,
    )
    check(
        "Every status has a clear label and description",
        all(f"status-help-{key}" in page.ids for key in STATUSES),
    )
    check(
        "Every badge has a native explanation target",
        all(
            text.count(f'popovertarget="status-help-{key}"')
            == sum(e["status"] == key for e in entries) + 1
            for key in STATUSES
        ),
    )
    check(
        "Removing source pointers preserves percentage values",
        reference_text("строки 14% и 16%") == "строки 14% и 16%"
        and reference_text("строки 14 – 16 %") == "строки 14 – 16 %",
    )
    output = HERE / ".test-results"
    output.mkdir(exist_ok=True)
    for i, script in enumerate(page.scripts):
        if script["type"] == "application/json":
            json.loads(script["text"])
            check(
                "Embedded search data has no local paths",
                not LOCAL_ADDRESS.search(script["text"]),
            )
        else:
            (output / f"index.script-{i}.js").write_text(
                script["text"], encoding="utf-8", newline="\n"
            )
    report = {
        "status": "PASS" if all(c["passed"] for c in checks) else "FAIL",
        "articles": len(entries),
        "categories": len(CATEGORIES),
        "source_references": len(references),
        "checks": checks,
    }
    (output / "verification.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": report["status"],
                "checks": len(checks),
                "failures": [c["name"] for c in checks if not c["passed"]],
            },
            ensure_ascii=False,
        )
    )
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
