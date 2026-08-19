"""
Liber Astrodum

core/prompt_builder.py

Prompt Builder Engine v6.0 — "Книга Звёздного Дара".

Строит интерпретацию по 12 домам с афоризмами.

Версия:
    6.0
"""

from typing import Any


# ==========================================================
# КОНСТАНТЫ
# ==========================================================

DEFAULT_CHART_TYPE = "natal"
MIN_PROMPT_CONFIDENCE = 0.35
MAX_EVIDENCE_PER_SECTION = 5


# ==========================================================
# АФОРИЗМЫ ДОМОВ
# ==========================================================

HOUSE_APHORISMS = {
    1: "Я — сосуд, в котором небо отражается землёй.",
    2: "Что ты ценишь, тем и становишься.",
    3: "Слово — мост, по которому душа идёт к другой душе.",
    4: "Корни держат дерево, но не мешают ему тянуться к свету.",
    5: "Творить — значит оставлять след души в материи.",
    6: "Порядок снаружи начинается с порядка внутри.",
    7: "Встреча с другим — всегда встреча с собой.",
    8: "Что умирает, то освобождает место для рождения.",
    9: "Горизонт существует, чтобы к нему идти.",
    10: "Вершина не для того, чтобы стоять, а чтобы видеть дальше.",
    11: "Единомышленники — это души, узнавшие друг друга.",
    12: "В тишине завершается круг и начинается новый.",
}

HOUSE_NAMES_RU = {
    1: "Личность",
    2: "Ценности",
    3: "Общение",
    4: "Корни",
    5: "Творчество",
    6: "Служение",
    7: "Партнёрство",
    8: "Трансформация",
    9: "Путь",
    10: "Призвание",
    11: "Сообщество",
    12: "Таинство",
}


# ==========================================================
# ВСПОМОГАТЕЛЬНЫЕ
# ==========================================================

def _as_list(collection) -> list:
    if collection is None:
        return []
    if hasattr(collection, "all"):
        return collection.all()
    return list(collection)


def _get(item, name: str, default=None):
    if item is None:
        return default
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_chart_type(chart_type: str | None) -> str:
    if not chart_type:
        return DEFAULT_CHART_TYPE
    chart_type = str(chart_type).lower().strip()
    aliases = {
        "solar": "solar", "solyar": "solar",
        "lunar": "lunar", "lunar_return": "lunar", "moon": "lunar",
        "natal": "natal", "birth": "natal",
    }
    return aliases.get(chart_type, DEFAULT_CHART_TYPE)


# ==========================================================
# CHART METADATA
# ==========================================================

def _build_chart_metadata(chart, chart_type: str) -> str:
    if chart is None:
        return f"Карта: {chart_type}"
    
    data = {}
    for field_name in ("type", "datetime", "lat", "lon"):
        value = _get(chart, field_name, None)
        if value is not None:
            data[field_name] = value
    data["type"] = data.get("type", chart_type)
    
    return (
        f"Карта: {data.get('type', '?')} | "
        f"{data.get('datetime', '?')} | "
        f"{data.get('lat', '?')},{data.get('lon', '?')}"
    )


# ==========================================================
# COMPOSITION SUMMARY
# ==========================================================

def _build_composition_summary(composition) -> str:
    core_theme = _get(composition, "core_theme", "")
    process = _get(composition, "dominant_process", "")
    planets = _get(composition, "planets", ()) or ()
    houses = _get(composition, "houses", ()) or ()
    tensions = _get(composition, "tensions", ()) or ()
    supports = _get(composition, "supports", ()) or ()
    resolutions = _get(composition, "resolutions", ()) or ()
    
    lines = [
        f"Тема: {core_theme}",
        f"Процесс: {process}",
        f"КЛЮЧЕВЫЕ ПЛАНЕТЫ: {', '.join(map(str, planets))}",
        f"КЛЮЧЕВЫЕ ДОМА: {', '.join(map(str, houses))}",
    ]
    
    if tensions:
        lines.append(f"Напряжение: {', '.join(map(str, tensions))}")
    if supports:
        lines.append(f"Поддержка: {', '.join(map(str, supports))}")
    if resolutions:
        lines.append(f"Разрешение: {', '.join(map(str, resolutions))}")
    
    return "\n".join(lines)


# ==========================================================
# EVIDENCE — ТЕКСТОВЫЙ ФОРМАТ
# ==========================================================

def _build_evidence_context(evidence_plan) -> str:
    if evidence_plan is None:
        return "Нет доказательств"
    
    sections = _as_list(_get(evidence_plan, "sections", ()))
    
    lines = []
    
    for section in sections:
        section_type = _get(section, "section_type", "")
        evidence = _get(section, "evidence", ()) or ()
        
        items = []
        for item in evidence[:MAX_EVIDENCE_PER_SECTION]:
            natural = _get(item, "natural_language", "")
            if natural:
                items.append(natural)
        
        if items:
            lines.append(f"{section_type}:")
            for item in items:
                lines.append(f"  - {item}")
    
    return "\n".join(lines) if lines else "Нет доказательств"


# ==========================================================
# ПРАВИЛА — СТРОГИЕ
# ==========================================================

def _build_global_rules() -> str:
    return """СТРОГИЕ ПРАВИЛА:
1. Используй ТОЛЬКО: Солнце, Луна, Меркурий, Венера, Марс, Юпитер, Сатурн.
2. НЕ упоминай: Уран, Нептун, Плутон, Хирон, Лилит.
3. Знаки должны соответствовать данным карты.
4. Аспекты: только соединение, секстиль, квадрат, тригон, оппозиция.
5. НЕ выдумывай аспекты, которых нет в опорных фактах.
6. НЕ используй markdown: без **, *, #.
7. НЕ используй абстракции без имени планеты.
8. Пиши конкретно: "Сатурн в Водолее", а не "строгая планета"."""


def _build_style_rules() -> str:
    return """СТИЛЬ:
- Язык: русский, философский, герметический.
- Без markdown.
- Каждый дом — отдельная глава.
- Начинай каждую главу с афоризма.
- Пиши как древний трактат, но современным языком.
- Не используй: "вам следует", "вы должны".
- Используй: "это может проявляться", "здесь открывается"."""


def _build_chart_rules(chart_type: str) -> str:
    if chart_type == "natal":
        return "Режим: натальная карта. Книга Звёздного Дара."
    if chart_type == "solar":
        return "Режим: соляр. Тематика года."
    return "Режим: лунар. Внутренний процесс периода."


# ==========================================================
# OUTPUT — КНИГА ЗВЁЗДНОГО ДАРА
# ==========================================================

def _build_output_rules(composition) -> str:
    houses = _get(composition, "houses", ()) or ()
    
    lines = [
        "ФОРМАТ ОТВЕТА — КНИГА ЗВЁЗДНОГО ДАРА:",
        "",
        "[SECTION:PROLOGUE]",
        "Одно вступительное предложение о судьбе человека.",
        "",
    ]
    
    # Только ключевые дома
    for house in houses:
        if house in HOUSE_NAMES_RU:
            name = HOUSE_NAMES_RU[house]
            aphorism = HOUSE_APHORISMS[house]
            lines.append(f"[SECTION:{house}_HOUSE] {name}")
            lines.append(f'Афоризм: "{aphorism}"')
            lines.append("Затем 2-3 предложения интерпретации.")
            lines.append("")
    
    lines.extend([
        "[SECTION:EPILOGUE]",
        "Итоговое послание — 1-2 предложения.",
    ])
    
    return "\n".join(lines)


# ==========================================================
# MAIN PROMPT
# ==========================================================

def build_pipeline_prompt(
    composition,
    evidence_plan=None,
    chart=None,
    chart_type: str = DEFAULT_CHART_TYPE,
) -> str:
    chart_type = _normalize_chart_type(chart_type)
    
    parts = [
        "Ты — Астродо, хранитель Небесного Архива Liber Astrodum.",
        "",
        "Напиши «Книгу Звёздного Дара» — астрологическую интерпретацию по домам.",
        "Каждая глава — отдельная сфера жизни.",
        "Начинай каждую главу с афоризма-ключа.",
        "Пиши философски, но конкретно.",
        "",
        _build_chart_metadata(chart, chart_type),
        "",
        _build_composition_summary(composition),
        "",
        "ОПОРНЫЕ ФАКТЫ:",
        _build_evidence_context(evidence_plan),
        "",
        _build_chart_rules(chart_type),
        "",
        _build_global_rules(),
        "",
        _build_style_rules(),
        "",
        _build_output_rules(composition),
    ]
    
    return "\n".join(part for part in parts if part).strip()


# ==========================================================
# REPORT API
# ==========================================================

def build_prompts(
    compositions,
    evidence_report=None,
    chart=None,
    chart_type: str = DEFAULT_CHART_TYPE,
) -> dict[str, str]:
    composition_list = _as_list(compositions)
    
    if not composition_list:
        return {}
    
    evidence_plans = {}
    
    if evidence_report is not None:
        for evidence_plan in _as_list(evidence_report):
            theme_key = _get(evidence_plan, "theme_key", "")
            if theme_key:
                evidence_plans[theme_key] = evidence_plan
    
    result = {}
    
    for composition in composition_list:
        theme_key = _get(composition, "theme_key", "")
        evidence_plan = evidence_plans.get(theme_key)
        
        result[theme_key] = build_pipeline_prompt(
            composition=composition,
            evidence_plan=evidence_plan,
            chart=chart,
            chart_type=chart_type,
        )
    
    return result


def build_prompt(
    prompt_context=None,
    chart_type: str = DEFAULT_CHART_TYPE,
    composition=None,
    evidence_plan=None,
    chart=None,
) -> str:
    if composition is not None:
        return build_pipeline_prompt(
            composition=composition,
            evidence_plan=evidence_plan,
            chart=chart,
            chart_type=chart_type,
        )
    
    if prompt_context is None:
        return ""
    
    chart_type = _normalize_chart_type(chart_type)
    context_text = str(prompt_context)
    
    return (
        f"Ты — Астродо, хранитель Небесного Архива Liber Astrodum.\n\n"
        f"ТИП КАРТЫ: {chart_type}\n\n"
        f"{context_text}\n\n"
        f"{_build_global_rules()}\n\n"
        f"{_build_style_rules()}"
    )