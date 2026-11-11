"""Opening banner, source coverage and footer for the standalone handbook."""

from __future__ import annotations

import html

from chrome import icon
from learning_examples import BY_ARTICLE

DIAGRAM = """<svg class="hero-drawing" viewBox="0 0 460 290" aria-hidden="true" focusable="false">
<defs><pattern id="hero-grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="currentColor" stroke-opacity=".08"/></pattern><clipPath id="hero-face"><ellipse cx="334" cy="142" rx="28" ry="66"/></clipPath></defs>
<rect x="1" y="1" width="458" height="288" rx="12" fill="url(#hero-grid)"/>
<g fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round">
<path d="M18 36V18H36m388 0h18v18M18 254v18h18m388 0h18v-18" stroke-opacity=".4"/>
<path d="M122 76H334a28 66 0 0 1 0 132H122a28 66 0 0 0 0-132Z" fill="#255f85" fill-opacity=".55"/>
<path d="M122 76a28 66 0 0 0 0 132" stroke-opacity=".5"/>
<ellipse cx="122" cy="142" rx="28" ry="66" stroke-dasharray="4 5" stroke-opacity=".35"/>
<ellipse cx="334" cy="142" rx="28" ry="66" fill="#255f85"/>
<g clip-path="url(#hero-face)" stroke-opacity=".18"><path d="m298 84 72 72m-72-56 72 72m-72-56 72 72m-72-56 72 72m-72-56 72 72m-72-56 72 72m-72-56 72 72m-72-56 72 72"/></g>
<path d="M68 142H398" stroke-dasharray="12 5 2 5" stroke-opacity=".6"/>
<path d="M122 62V36m212 26V36M122 42H334m-212-4v8m212-8v8M378 76h30m-30 132h30M400 76V208m-4-132h8m-8 132h8" stroke-opacity=".6"/>
<path d="m122 42 7-3v6Zm212 0-7-3v6ZM400 76l-3 7h6Zm0 132-3-7h6Z" fill="currentColor" stroke="none"/>
<path d="M306 142h56m-28-9v18" stroke-opacity=".75"/>
</g><g fill="currentColor" font-family="Cambria Math,serif" font-style="italic"><text x="228" y="31" text-anchor="middle" font-size="18">L</text><text x="415" y="148" font-size="18">D</text><text x="228" y="254" text-anchor="middle" font-size="20">V = πD²L / 4</text></g>
</svg>"""


def number(value):
    return f"{value:,}".replace(",", "\u202f")


def hero_html(entries, category_count):
    metrics = (
        (len(entries), "статей и расчётных правил"),
        (category_count, "тематических разделов"),
        (len(BY_ARTICLE), "интерактивных примеров"),
        (sum(e["status"] == "prepared" for e in entries), "подготовленных методов"),
    )
    stats = "".join(
        f'<div class="hero-metric"><dt>{label}</dt><dd>{number(value)}</dd></div>'
        for value, label in metrics
    )
    steps = (
        ("Определите объект", "Деталь, заготовка, пруток, движение или партия."),
        (
            "Проверьте единицы",
            "Обозначения и размерности — в таблице рядом с формулой.",
        ),
        (
            "Уточните условия",
            "Учитывайте состояние метода, исходные данные и их происхождение.",
        ),
        (
            "Разберите пример",
            "Меняйте входы в калькуляторе и проследите подстановку до результата.",
        ),
    )
    guide = "".join(
        f'<li><span class="reading-step" aria-hidden="true">{index:02d}</span><div><h3>{title}</h3><p>{text}</p></div></li>'
        for index, (title, text) in enumerate(steps, 1)
    )
    return f"""<div class="book-hero" aria-labelledby="handbook-title">
<div class="hero-body"><div class="hero-copy"><p class="hero-eyebrow"><span aria-hidden="true">{icon("start")}</span>Metall · Инженерная библиотека</p>
<h1 id="handbook-title">От геометрии<span>до времени и сметы</span></h1>
<p class="hero-lead">Геометрия и масса, режимы обработки, время и стоимость. Формулы с понятными обозначениями, условиями и примерами.</p>
<div class="hero-actions"><a class="hero-link hero-link-primary" href="#units">К формулам<span aria-hidden="true">{icon("chevron")}</span></a><a class="hero-link hero-link-secondary" href="#practice">Разобрать пример</a></div></div>
<figure class="hero-visual">{DIAGRAM}<figcaption><span>Размеры</span><span aria-hidden="true">→</span><span>Формула</span><span aria-hidden="true">→</span><span>Результат</span></figcaption></figure></div>
<dl class="hero-metrics" aria-label="Содержание пособия">{stats}</dl></div>
<aside class="reading" aria-labelledby="reading-title"><div class="reading-heading"><span class="reading-symbol" aria-hidden="true">{icon("start")}</span><h2 id="reading-title">Как работать с формулой</h2></div><ol>{guide}</ol></aside>"""


def coverage_html(entries, code, docs, office_count):
    corpora = (
        (
            "library",
            code["files"],
            "файлов исходного кода",
            "Python · Go · JavaScript · TypeScript",
            f"{code['runtime_files']} с меткой runtime. Учтены арифметические выражения, ветвления и исходные функции.",
        ),
        (
            "metrics",
            138,
            "уникальных ID формул Go",
            "141 объявление в реестре",
            "Каждый идентификатор включён; варианты общей формулы сохранены.",
        ),
        (
            "start",
            docs["documents"],
            "текстовых документов",
            "Документация · справочники · исследования",
            "Рассмотрены текущие и архивные материалы проекта.",
        ),
        (
            "comparison",
            office_count,
            "формульных ячеек",
            "Таблицы и 6 документов Word",
            "Сохранены имена листов, адреса ячеек и порядок абзацев.",
        ),
        (
            "coverage",
            52,
            "документа PDF",
            "199 страниц · 98 текстовых кандидатов",
            "34 страницы без достаточного текстового слоя; их содержимое не объявлено разобранным.",
        ),
        (
            "prepared",
            len(entries),
            "статей и расчётных правил",
            "Формулы · условия · единицы · примеры",
            "Происхождение сохранено у каждой записи. Подготовленные методы выделены отдельно.",
        ),
    )
    cards = "".join(
        f'<li class="coverage-card"><div class="coverage-card-top"><span class="coverage-icon" aria-hidden="true">{icon(key)}</span><span class="coverage-number">{number(value)}</span></div><h3>{label}</h3><p class="coverage-detail">{detail}</p><p>{explanation}</p></li>'
        for key, value, label, detail, explanation in corpora
    )
    notes = (
        (
            "Число записей",
            "Число статей включает отдельные формулы и документальные комплекты. Одна зависимость может повторяться в разных методах с разными условиями.",
        ),
        (
            "Состояние методов",
            "Десять подготовленных зависимостей выделены отдельно. Для огибающей смещённого отверстия трубы подключение не установлено; она не объявлена доказанно неиспользуемой.",
        ),
        (
            "Происхождение сравнений",
            "Исследования ВоксаТех, учебные таблицы и контрольные примеры имеют собственное происхождение. Сопоставление не переносит автоматически правила стороннего продукта в Metall.",
        ),
        (
            "Проверка единиц",
            "В учебной книге вала сохранена отмеченная ошибка мощности: при Q в см³/мин знаменатель 60000η вместо 60η даёт расхождение в 1000 раз.",
        ),
        (
            "Границы исходных материалов",
            "Сканы без достаточного текстового слоя, весь математический аппарат неиспользуемых книг, зависимости пакетов, бинарные сборки, базы и история Git не объявлены полностью разобранными.",
        ),
        (
            "Неподтверждённые значения",
            "UNKNOWN сохраняется для неподтверждённых входов и результатов. Арифметическая проверка примера не назначает производственный режим, тариф или норму цеха.",
        ),
    )
    boundaries = "".join(
        f'<li class="coverage-note"><span class="coverage-note-index" aria-hidden="true">{index:02d}</span><div><h4>{title}</h4><p>{html.escape(text)}</p></div></li>'
        for index, (title, text) in enumerate(notes, 1)
    )
    return f"""<section class="coverage" id="coverage" aria-labelledby="coverage-title"><header class="coverage-heading"><div><p class="section-eyebrow">Состав и источники</p><h2 id="coverage-title">Охват справочника</h2></div><p class="coverage-date">Срез исходных материалов<br><span>11.11.2026</span></p></header>
<p class="coverage-lead">Код, документация и таблицы собраны в единое пособие. Здесь показано, какие материалы исследованы и что означают полученные числа.</p>
<ul class="coverage-grid" aria-label="Исследованные материалы">{cards}</ul>
<div class="coverage-boundaries"><div class="coverage-boundaries-heading"><span aria-hidden="true">{icon("coverage")}</span><h3>Границы применения</h3></div><p class="coverage-method">«В рабочем расчёте» означает наличие зависимости в подключённом коде. Её применение на конкретной детали зависит от входов и выбранного метода.</p><ol class="coverage-notes">{boundaries}</ol></div></section>"""


def footer_html():
    return f"""<footer class="book-footer" aria-label="О пособии и навигация"><div class="footer-main"><div class="footer-about"><a class="footer-brand" href="#start"><span class="footer-mark" aria-hidden="true">M</span><span><strong>Metall</strong><span>Инженерная библиотека</span></span></a><p>Формулы и расчёты: от геометрии детали до времени, трудоёмкости и стоимости.</p></div>
<nav class="footer-nav" aria-label="Основные разделы"><h2>В справочнике</h2><a href="#geometry">Геометрия и масса</a><a href="#feeds">Режимы обработки</a><a href="#time">Время и партия</a><a href="#cost">Смета и трудоёмкость</a></nav>
<nav class="footer-nav" aria-label="Работа с пособием"><h2>Изучение и практика</h2><a href="#practice">Интерактивный пример</a><a href="#prepared">Подготовленные методы</a><a href="#comparison">Исследования и примеры</a><a href="#coverage">Охват и границы</a></nav></div>
<div class="footer-bottom"><p>Учебное пособие Metall</p><a class="footer-top" href="#start">К началу<span aria-hidden="true">{icon("chevron")}</span></a></div></footer>"""
