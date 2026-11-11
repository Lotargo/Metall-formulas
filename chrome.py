"""Standalone header and grouped handbook navigation with embedded Lucide icons."""

from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ICONS = json.loads((HERE / "icons.json").read_text(encoding="utf-8"))
SIDEBAR_ART = (HERE / "sidebar-art.svg").read_text(encoding="utf-8")
GROUPS = [
    ("Основа расчёта", ["units", "geometry", "tolerances", "stock", "bars"]),
    (
        "Обработка",
        [
            "feeds",
            "turning",
            "drilling",
            "threading",
            "milling",
            "grinding",
            "machines",
        ],
    ),
    ("Время и смета", ["time", "scenarios", "cost", "metrics"]),
    ("Методы и исследования", ["library", "prepared", "comparison"]),
]
SHORT_TITLES = {
    "tolerances": "Допуски и цепи",
    "stock": "Заготовки и кривизна",
    "bars": "Раскрой и баланс",
    "feeds": "Режимы и мощность",
    "turning": "Точение и расточка",
    "drilling": "Сверление",
    "milling": "Фрезерование",
    "grinding": "Шлифование",
    "machines": "Станки и нагрузки",
    "cost": "Смета и трудоёмкость",
    "library": "Библиотечные методы",
    "prepared": "Подготовленные формулы",
    "comparison": "Исследования и примеры",
}


def icon(key):
    return ICONS[key]


def nav_link(key, title, count=None, current=False, full_title=None):
    attrs = ' aria-current="location"' if current else ""
    count_html = (
        f'<span class="count" data-total="{count}" aria-label="Статей в разделе: {count}">{count}</span>'
        if count is not None
        else ""
    )
    title_attr = f' title="{html.escape(full_title or title, quote=True)}"'
    return f'<a href="#{key}" data-section="{key}"{attrs}{title_attr}><span class="nav-icon">{icon(key)}</span><span class="nav-text">{html.escape(title)}</span>{count_html}</a>'


def handbook_chrome(entries, categories, options):
    counts = Counter(entry["category"] for entry in entries)
    titles = {key: title for key, title, _ in categories}
    groups = []
    for index, (title, keys) in enumerate(GROUPS):
        links = "".join(
            nav_link(
                key,
                SHORT_TITLES.get(key, titles[key]),
                counts[key],
                full_title=titles[key],
            )
            for key in keys
            if counts[key]
        )
        groups.append(
            f'<section class="nav-group" aria-labelledby="nav-group-{index}"><h2 class="nav-label" id="nav-group-{index}">{title}</h2>{links}</section>'
        )
    license_text = (
        (HERE / "ICONS-LICENSE.txt").read_text(encoding="utf-8").replace("---", "")
    )
    sidebar = f"""<!--
{license_text}
--><aside class="sidebar" id="booknav" aria-label="Разделы справочника">
{SIDEBAR_ART}
<div class="sidebar-head"><a class="brand" href="#start" aria-label="Metall: начало справочника"><span class="brand-mark" aria-hidden="true">M</span><span><strong>Metall</strong><small>Инженерная библиотека</small></span></a><button type="button" class="sidebar-close icon-button" id="nav-close" aria-label="Закрыть главы" autofocus>{icon("close")}</button></div>
<nav class="sidebar-scroll" aria-label="Главы пособия">{nav_link("start", "Начало пособия", current=True)}{"".join(groups)}</nav>
<div class="sidebar-footer"><nav class="sidebar-footlinks" aria-label="Материалы справочника">{nav_link("coverage", "Охват справочника")}</nav></div></aside>"""
    header = f"""<header class="topbar" aria-label="Поиск и действия справочника">
<div class="header-main"><div class="header-heading"><button type="button" class="mobile-nav icon-button" id="nav-toggle" aria-controls="booknav" aria-expanded="false" aria-label="Открыть главы" title="Открыть главы">{icon("menu")}</button><span class="header-symbol" aria-hidden="true">{icon("start")}</span><div class="header-title-block"><p class="header-title">Формулы и расчёты</p><div class="header-subline"><span class="header-eyebrow">Учебное пособие Metall</span><span class="header-count" id="result-count" role="status" aria-live="polite">{len(entries)} статей</span></div></div></div>
<div class="header-actions"><button type="button" class="button-primary" id="print" aria-label="Печать справочника" title="Печать справочника">{icon("print")}<span class="action-label">Печать</span></button></div></div>
<div class="header-tools"><div class="header-search"><label class="sr-only" for="search">Поиск по формулам и источникам</label><span class="search-icon">{icon("search")}</span><input type="search" name="search" id="search" placeholder="Найти формулу, обозначение или источник…" autocomplete="off" aria-keyshortcuts="Control+K Meta+K"><kbd class="search-shortcut" aria-hidden="true">Ctrl K</kbd><button type="button" class="search-clear icon-button" id="search-clear" aria-label="Очистить поиск" title="Очистить поиск" hidden>{icon("close")}</button></div><div class="header-filter"><label class="sr-only" for="status">Состояние формулы</label><span class="filter-icon">{icon("filter")}</span><select name="status" id="status">{options}</select><span class="select-chevron">{icon("chevron")}</span></div><button type="button" class="header-reset" id="reset" aria-label="Сбросить поиск и фильтр" title="Сбросить поиск и фильтр">{icon("reset")}<span>Сбросить</span></button></div></header>"""
    dialog = '<dialog class="nav-dialog" id="nav-dialog" aria-label="Разделы справочника"></dialog>'
    return sidebar, header, dialog
