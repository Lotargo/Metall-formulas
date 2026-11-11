"""Render a self-contained handbook with visible notation and readable provenance."""

from __future__ import annotations

import html
import json
from pathlib import Path

from catalogue import CATEGORIES
from chrome import handbook_chrome
from editorial import coverage_html, footer_html, hero_html
from learning_examples import BY_ARTICLE, PRIMARY_RESULTS
from provenance import group_counts, public_text, reference_text
from statuses import STATUSES, status_badge, status_legend, status_tooltips

HERE = Path(__file__).resolve().parent
LABELS = {key: value[0] for key, value in STATUSES.items()}

UNITS = {
    "mm": "мм",
    "mm²": "мм²",
    "mm³": "мм³",
    "mm2": "мм²",
    "mm3": "мм³",
    "min": "мин",
    "s": "с",
    "kg": "кг",
    "kg/m³": "кг/м³",
    "kg/m3": "кг/м³",
    "g/cm³": "г/см³",
    "deg": "град",
    "rad": "рад",
    "cm³/min": "см³/мин",
    "cm3/min": "см³/мин",
    "rpm": "об/мин",
    "rev/min": "об/мин",
    "mm/min": "мм/мин",
    "mm/rev": "мм/об",
}
COMPARISON_GROUPS = [
    (
        "research",
        "Исследования ВоксаТех",
        "Зависимости из пяти исследовательских документов D383–D387. В них сопоставлены открытый интерфейс, клиентский код, руководство и сохранённые примеры стороннего продукта. У каждой записи приведено исходное свидетельство; инженерная реконструкция не объявляется подтверждённым серверным алгоритмом.",
    ),
    (
        "teaching",
        "Учебные и сравнительные таблицы",
        "Формулы из трёх книг, сохранённых в проекте: расчёт техмаршрута вала II-175, контрольная группа заготовок и учебная карта ручки. Для каждой группы указаны книга, лист и пример ячейки. Наличие книги в проекте не устанавливает авторство и не означает использование её формул в рабочем расчёте.",
    ),
    (
        "control",
        "Нормативные и проверочные зависимости",
        "Контрольная арифметика сортамента, сопоставление с Walter, замер подачи и учебная геометрия ручки. Эти записи объясняют проверку результата в своей области и сохраняют конкретный источник.",
    ),
]


def esc(value):
    return html.escape(public_text(value), quote=True)


def jsdata(value):
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def head(title, description):
    css = (HERE / "handbook.css").read_text(encoding="utf-8")
    return f'<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{esc(description)}"><meta name="color-scheme" content="light"><title>{esc(title)}</title><style>{css}</style></head>'


def provenance_html(entry, heading):
    points = []
    for point in entry["provenance"]:
        source_evidence = reference_text(point.get("evidence", ""))
        source_location = (
            f" · {esc(point['location'])}" if point.get("location") else ""
        )
        evidence = (
            f'<p class="source-evidence"><strong>Свидетельство:</strong> {esc(source_evidence)}</p>'
            if source_evidence
            else ""
        )
        points.append(
            f'<div class="source-point" data-source-id="{point["id"]}"><p class="source-title">{esc(point["title"])}</p><p><span class="source-kind">{esc(point["kind_label"])}</span>{source_location}</p>{evidence}</div>'
        )
    return (
        f'<section class="origin-inline" aria-label="Происхождение формулы"><h{heading}>Откуда взято</h{heading}>'
        + "".join(points)
        + "</section>"
    )


def article(entry, level=3):
    ident = entry["id"]
    rows = "".join(
        f"<tr><td>{esc(v['symbol'])}</td><td>{esc(v['meaning'])}</td><td>{esc(UNITS.get(v['unit'], v['unit']))}</td></tr>"
        for v in entry["variables"]
    )
    notation = f'<aside class="notation-panel" aria-labelledby="notation-{ident}"><h{level + 1} id="notation-{ident}">Обозначения и единицы</h{level + 1}><div class="table-scroll"><table class="notation-table"><thead><tr><th scope="col">Обозначение</th><th scope="col">Смысл</th><th scope="col">Единица</th></tr></thead><tbody>{rows}</tbody></table></div></aside>'
    family = entry.get("family") or ""
    if entry.get("formula_id"):
        family += " · " + entry["formula_id"]
    if not family:
        family = next(
            (label for key, label, _ in CATEGORIES if key == entry["category"]), ""
        )
    example = (
        f'<p class="worked"><strong>Пример.</strong> {esc(entry["example"])}</p>'
        if entry.get("example")
        else ""
    )
    kind = BY_ARTICLE.get(ident)
    primary = PRIMARY_RESULTS.get(ident)
    primary_attribute = (
        f' data-primary="{html.escape(jsdata(primary), quote=True)}"' if primary else ""
    )
    learning = (
        f'<section class="learning-example" data-example="{kind}"{primary_attribute} id="learn-{ident}" aria-labelledby="learn-title-{ident}"><div class="learning-heading"><span class="learning-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M8 7h8M8 11h2m4 0h2M8 15h2m4 0h2M8 18h2m4 0h2"/></svg></span><h{level + 1} id="learn-title-{ident}">Калькулятор</h{level + 1}><span class="learning-kind">Интерактивный пример</span></div><div class="learning-content"></div></section>'
        if kind
        else ""
    )
    return f'''<article class="entry" id="{ident}" data-category="{entry["category"]}" data-status="{entry["status"]}" data-provenance-group="{entry.get("provenance_group", "")}"><div class="entry-grid"><div class="entry-main"><div class="entry-top"><h{level}>{esc(entry["title"])}</h{level}>{status_badge(entry["status"])}</div><div class="entry-meta">{esc(family)}</div><div class="equation">{esc(entry["expression"])}</div><p>{esc(entry["explanation"])}</p><p class="condition"><strong>Условия.</strong> {esc(reference_text(entry["conditions"]))}</p>{example}</div>{notation}</div>{learning}{provenance_html(entry, level + 1)}</article>'''


def comparison_html(entries):
    counts = group_counts(entries)
    overview = (
        '<div class="origin-guide">'
        + "".join(
            f"<div><h3>{esc(title)} · {counts[key]}</h3><p>{esc({'research': 'Извлечены из исследований стороннего продукта D383–D387.', 'teaching': 'Группы формул из учебных и контрольных книг; точные ячейки сохранены.', 'control': 'Нормативная арифметика, измерения, Walter и геометрические примеры.'}[key])}</p></div>"
            for key, title, _ in COMPARISON_GROUPS
        )
        + "</div>"
    )
    for key, title, intro in COMPARISON_GROUPS:
        selected = [e for e in entries if e.get("provenance_group") == key]
        overview += (
            f'<section class="provenance-group" id="comparison-{key}"><h3>{esc(title)} · {len(selected)} записей</h3><p>{esc(intro)}</p>'
            + "".join(article(e, 4) for e in selected)
            + "</section>"
        )
    return overview


EXAMPLE = """<section class="example" id="practice" aria-labelledby="example-title"><h2 id="example-title">Разберём один рез круглого прутка</h2><p>Учебный пример связывает площадь сечения с производительностью. При неизменной площадной производительности время растёт пропорционально квадрату диаметра.</p><div class="example-layout"><svg viewBox="0 0 160 160" role="img" aria-label="Круглое сечение с диаметром D"><circle cx="80" cy="80" r="59" fill="#e8f1f7" stroke="#255f85" stroke-width="2"/><path d="M21 80h118" stroke="#255f85" stroke-width="1.5"/><path d="m21 80 8-4v8zm118 0-8-4v8z" fill="#255f85"/><text x="80" y="66" text-anchor="middle" fill="#255f85" font-size="22" font-family="Cambria Math,serif">D</text></svg><div><div class="example-inputs"><div class="field"><label for="ex-d">Диаметр D, мм</label><input id="ex-d" name="diameter" type="number" min="0.001" max="10000" step="any" value="75" aria-describedby="ex-error"></div><div class="field"><label for="ex-r">Производительность R, см²/мин</label><input id="ex-r" name="area_rate" type="number" min="0.001" max="100000" step="any" value="20" aria-describedby="ex-error"></div><div class="field"><label for="ex-k">Пропил k, мм</label><input id="ex-k" name="kerf" type="number" min="0.001" max="100" step="any" value="3" aria-describedby="ex-error"></div></div><div class="steps" id="example-steps"></div><div class="example-result"><output id="example-time" for="ex-d ex-r ex-k"></output> <span>на один рез</span></div><p class="muted" id="example-volume"></p><div class="error" id="ex-error" aria-live="polite"></div></div></div><p class="muted">R=20 см²/мин является учебным входом. Скорость полотна в м/мин не подставляется вместо R. Загрузка, зажим, возврат и наладка учитываются отдельно.</p></section>"""


def index_html(entries, code, docs, office_count):
    chapters = []
    for key, title, intro in CATEGORIES:
        selected = [e for e in entries if e["category"] == key]
        if not selected:
            continue
        content = (
            comparison_html(selected)
            if key == "comparison"
            else "".join(article(e) for e in selected)
        )
        chapters.append(
            f'<section class="chapter" id="{key}"><div class="chapter-title"><h2>{esc(title)}</h2><span>{len(selected)} статей</span></div><p class="chapter-intro">{esc(intro)}</p>{content}</section>'
        )
    options = '<option value="all">Все состояния</option>' + "".join(
        f'<option value="{key}">{label}</option>' for key, label in LABELS.items()
    )
    sidebar, header, dialog = handbook_chrome(entries, CATEGORIES, options)
    search_data = [
        {
            "id": e["id"],
            "text": public_text(
                " ".join(
                    reference_text(e.get(k))
                    if k == "conditions"
                    else str(e.get(k) or "")
                    for k in (
                        "id",
                        "title",
                        "expression",
                        "explanation",
                        "conditions",
                        "family",
                        "formula_id",
                    )
                )
                + " "
                + " ".join(
                    " ".join(
                        reference_text(p.get(k, ""))
                        for k in ("title", "kind_label", "location", "evidence")
                    )
                    for p in e["provenance"]
                )
            ),
        }
        for e in entries
    ]
    script = (
        (HERE / "handbook.js").read_text(encoding="utf-8")
        + "\n"
        + (HERE / "learning.js").read_text(encoding="utf-8")
        + "\n"
        + (HERE / "status-help.js").read_text(encoding="utf-8")
    )
    body = f"""<body><a class="skip" href="#main">К содержимому</a>{dialog}{sidebar}<div class="layout"><div id="header-sentinel" aria-hidden="true"></div>{header}<main class="main" id="main"><section class="intro" id="start">{hero_html(entries, len(CATEGORIES))}{status_legend()}<p class="intro-note">UNKNOWN обозначает неразрешённое значение. Ноль используется как известное значение. <a href="#comparison">Исследования и контрольные примеры</a> разделены по происхождению и не включены в число подключённых методов.</p>{EXAMPLE}</section><div class="empty" id="empty" hidden><h2>Совпадений нет</h2><p>Попробуйте часть названия, обозначение или название источника.</p></div><div id="chapters">{"".join(chapters)}</div>{coverage_html(entries, code, docs, office_count)}</main>{footer_html()}</div>{status_tooltips()}<script id="search-data" type="application/json">{jsdata(search_data)}</script><script>{script}</script></body></html>"""
    return (
        head(
            "Формулы Metall: учебное пособие",
            "Расчётные формулы Metall: обозначения, единицы, условия и происхождение каждой записи.",
        )
        + body
    )
