"""Portable display normalization; no external project files are read."""

import re
from collections import Counter


def public_text(value: object) -> str:
    """Keep mathematical text and source names, suppress machine-local addresses."""
    text = str(value or "")
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"(?:file:///?|[A-Za-z]:[\\/])[^\s<>\"'`]+", "[адрес исключён]", text)
    text = re.sub(r"(?:https?://)[^\s<>\"'`]+", "[внешний источник]", text)
    text = re.sub(
        r"(?<!\w)(?:src|metall_mvp|mvp|machining-calc|stock-selection|web|docs|library|output|voksa-metall-comparison|План|scripts|seeds|trace-console|splav-parser)[\\/][^\s<>\"'`|;,)]*",
        "[внутренний источник]",
        text,
    )
    text = re.sub(
        r"(?<!\w)(?:\.\.?[\\/])[^\s<>\"'`|;,)]*", "[внутренний источник]", text
    )
    text = re.sub(
        r"(?:xl/worksheets/[^\s;]+|word/document\.xml)",
        "структура исходного документа",
        text,
    )
    text = text.replace(
        "полный список сохранён в office_formulas.json",
        "все адреса ячеек сохранены в техническом реестре",
    )
    return text


SOURCE_POSITION = re.compile(
    r"(?:[,;]\s*)?\b(?:строка|строки|строку|абзац)\s+\d+(?:\s*[–—-]\s*\d+)?(?!\d|\.\d|\s*[%–—-])",
    re.IGNORECASE,
)


def reference_text(value: object) -> str:
    """Remove positional pointers while retaining names and substantive evidence."""
    return SOURCE_POSITION.sub("", public_text(value)).strip(" ,;·")


def group_counts(entries: list[dict]) -> dict[str, int]:
    return dict(
        Counter(e["provenance_group"] for e in entries if e["provenance_group"])
    )
