"""
Liber Astrodum

core/prompt_builder.py

Prompt Builder Engine v5.1 — COMPACT + CONCRETE.

Версия:
    5.1
"""

from typing import Any
import json


# ==========================================================
# КОНСТАНТЫ
# ==========================================================

DEFAULT_CHART_TYPE = "natal"
MIN_PROMPT_CONFIDENCE = 0.35
MAX_EVIDENCE_PER_SECTION = 5


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


# ==========================================================
# CHART TYPE
# ==========================================================

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
# COMPOSITION SUMMARY — С КОНКРЕТИКОЙ
# ==========================================================

def _build_composition_summary(composition) -> str:
    theme_key = _get(composition, "theme_key", "")
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
        f"КЛЮЧЕВЫЕ ПЛАНЕТЫ (в порядке важности): {', '.join(map(str, planets))}",
        f"Дома: {', '.join(map(str, houses))}",
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
    """
    Доказательства в текстовом формате для LLM.
    Без весов — только суть для литературного осмысления.
    """
    
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
# GLOBAL RULES — КОНКРЕТНЫЕ
# ==========================================================

def _build_global_rules() -> str:
    return """Правила:
1. Называй планеты КОНКРЕТНО: Сатурн, Меркурий, Луна, Водолей.
2. НЕ используй абстракции: "сущность", "центр", "сила" без имени планеты.
3. Ключевые планеты из списка важнее второстепенных.
4. Описывай реальные аспекты (оппозиция, тригон, соединение).
5. Не выдумывай факты, события, даты.
6. Не заканчивай каждый абзац одинаково.
7. Избегай: "указывая на", "проявляется как", "может проявляться".
8. Не используй: "гарантированно", "неизбежно", "точно произойдёт"."""


def _build_style_rules() -> str:
    return """Стиль:
- Язык: русский.
- Тон: спокойный, философский, конкретный.
- Без мистификации и категоричных предсказаний.
- Каждый раздел — один цельный абзац.
- Используй формат: [SECTION:НАЗВАНИЕ] перед каждым абзацем."""


# ==========================================================
# CHART RULES
# ==========================================================

def _build_chart_rules(chart_type: str) -> str:
    if chart_type == "natal":
        return "Режим: натальная карта. Фокус: структура личности, психология, долгосрочная динамика."
    if chart_type == "solar":
        return "Режим: соляр. Фокус: тематика года. Не выдавай вероятности за гарантии."
    return "Режим: лунар. Фокус: внутренний процесс периода. Без категоричных событий."


# ==========================================================
# OUTPUT RULES
# ==========================================================

def _build_output_rules(composition) -> str:
    sections = _as_list(_get(composition, "sections", ()))
    
    markers = []
    for section in sections:
        section_type = _get(section, "section_type", "")
        marker = str(section_type).upper()
        markers.append(f"[SECTION:{marker}]")
    
    return (
        "Формат ответа:\n"
        + "\n".join(markers)
        + "\n\nКаждый раздел — один абзац. "
        "Между разделами — пустая строка. "
        "Ничего вне секций."
    )


# ==========================================================
# MAIN PIPELINE PROMPT
# ==========================================================

def build_pipeline_prompt(
    composition,
    evidence_plan=None,
    chart=None,
    chart_type: str = DEFAULT_CHART_TYPE,
) -> str:
    """
    Компактный промпт для LLM с конкретикой.
    """
    
    chart_type = _normalize_chart_type(chart_type)
    
    parts = [
        "Ты — Астродо, хранитель Небесного Архива Liber Astrodum.",
        "",
        "Напиши глубокую литературную астрологическую интерпретацию.",
        "Называй планеты и знаки КОНКРЕТНО.",
        "Выделяй ключевые планеты из списка.",
        "Описывай реальные аспекты между планетами.",
        "Пиши как современный герметический трактат.",
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
    """
    Строит компактные промпты для каждого CompositionPlan.
    """
    
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


# ==========================================================
# ЕДИНАЯ ТОЧКА ВХОДА
# ==========================================================

def build_prompt(
    prompt_context=None,
    chart_type: str = DEFAULT_CHART_TYPE,
    composition=None,
    evidence_plan=None,
    chart=None,
) -> str:
    """
    Единая точка входа.
    """
    
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