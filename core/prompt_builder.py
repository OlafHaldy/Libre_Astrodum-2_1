"""
Liber Astrodum

core/prompt_builder.py

Prompt Builder v2.0.
Превращает PromptContext в текст промпта для LLM.

Не анализирует карту. Только форматирует данные.
Текст промпта содержит жёсткие правила для LLM.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.0
"""


def build_prompt(prompt_context, chart_type="lunar") -> str:
    """
    Строит текст промпта из PromptContext.

    Parameters
    ----------
    prompt_context : PromptContext
    chart_type : str

    Returns
    -------
    str
    """
    ctx = prompt_context
    mt = ctx.main_theme

    # Главная тема
    main_theme_text = ""
    if mt:
        main_theme_text = (
            f"Главная тема карты:\n"
            f"- Планета: {mt.planet}\n"
            f"- Дом: {mt.house}\n"
            f"- Знак: {mt.sign}\n"
            f"- Диспозитор: {mt.dispositor}\n"
        )

    # Ключевые факторы (топ-5)
    key_factors_text = ""
    if ctx.key_factors:
        key_factors_text = "Ключевые факторы (по важности):\n"
        for i, f in enumerate(ctx.key_factors[:5], 1):
            obj = f.get('object', '?')
            importance = f.get('importance', 0)
            reasons = ', '.join(f.get('importance_reasons', []))
            key_factors_text += f"{i}. {obj} (важность: {importance}) — {reasons}\n"

    # Сильные стороны
    strengths_text = ""
    if ctx.strengths:
        strengths_text = "Сильные стороны карты:\n"
        for s in ctx.strengths[:5]:
            obj = s.get('object', '?')
            reasons = ', '.join(s.get('confidence_reasons', []))
            strengths_text += f"- {obj}: {reasons}\n"

    # Слабые места
    challenges_text = ""
    if ctx.challenges:
        challenges_text = "Слабые места (важно, но проявляется слабо):\n"
        for c in ctx.challenges[:5]:
            obj = c.get('object', '?')
            reasons = ', '.join(c.get('confidence_reasons', []))
            challenges_text += f"- {obj}: {reasons}\n"

    # Противоречия
    contradictions_text = ""
    if ctx.contradictions:
        contradictions_text = "Противоречия в карте:\n"
        for c in ctx.contradictions:
            contradictions_text += (
                f"- Оппозиция {c.planet1} — {c.planet2}\n"
            )

    # Доминанты
    dominants_text = ""
    if ctx.dominant_elements or ctx.dominant_modes or ctx.dominant_houses:
        dominants_text = "Доминанты карты:\n"
        if ctx.dominant_elements:
            dominants_text += f"- Стихии: {', '.join(ctx.dominant_elements)}\n"
        if ctx.dominant_modes:
            dominants_text += f"- Кресты: {', '.join(ctx.dominant_modes)}\n"
        if ctx.dominant_houses:
            dominants_text += f"- Дома: {', '.join(str(h) for h in ctx.dominant_houses)}\n"

    # Карта
    chart_name = "Лунар" if chart_type == "lunar" else "Натальная карта"

    return f"""Ты — астролог классической школы. Интерпретируй {chart_name}.

{main_theme_text}
{key_factors_text}
{strengths_text}
{challenges_text}
{contradictions_text}
{dominants_text}

=== ЖЁСТКИЕ ПРАВИЛА (соблюдай неукоснительно) ===

1. УПРАВИТЕЛИ ЗНАКОВ ТОЛЬКО КЛАССИЧЕСКИЕ:
Овен — Марс, Телец — Венера, Близнецы — Меркурий, Рак — Луна,
Лев — Солнце, Дева — Меркурий, Весы — Венера, Скорпион — Марс,
Стрелец — Юпитер, Козерог — Сатурн, Водолей — САТУРН, Рыбы — Юпитер.
Уран, Нептун, Плутон НЕ управляют знаками.

2. Начни с ГЛАВНОЙ ТЕМЫ. Она уже определена — используй её.

3. Упомяни СИЛЬНЫЕ СТОРОНЫ — то, что помогает главной теме.

4. Укажи СЛАБЫЕ МЕСТА — то, что важно, но проявляется с трудом.

5. Опиши ПРОТИВОРЕЧИЯ, если они есть.

6. НЕ используй шаблонные значения знаков.
   Тема месяца определяется по ДОМУ и ДИСПОЗИТОРУ, а не по знаку.

7. Пиши на русском языке. Дай развёрнутый прогноз (3-4 абзаца).
   Не используй markdown."""


def build_prompt_from_dict(prompt_context_dict: dict, chart_type="lunar") -> str:
    """
    Строит промпт из словаря (для случаев, когда PromptContext сериализован).
    """
    class SimpleObj:
        def __init__(self, d):
            self.__dict__.update(d)

    mt_dict = prompt_context_dict.get("main_theme", {})
    main_theme = SimpleObj(mt_dict) if mt_dict else None

    key_factors = prompt_context_dict.get("key_factors", [])
    strengths = prompt_context_dict.get("strengths", [])
    challenges = prompt_context_dict.get("challenges", [])

    contradictions = []
    for c in prompt_context_dict.get("contradictions", []):
        contradictions.append(SimpleObj(c))

    dominant_elements = prompt_context_dict.get("dominant_elements", [])
    dominant_modes = prompt_context_dict.get("dominant_modes", [])
    dominant_houses = prompt_context_dict.get("dominant_houses", [])

    return build_prompt_text(
        main_theme=main_theme,
        key_factors=key_factors,
        strengths=strengths,
        challenges=challenges,
        contradictions=contradictions,
        dominant_elements=dominant_elements,
        dominant_modes=dominant_modes,
        dominant_houses=dominant_houses,
        chart_type=chart_type,
    )


def build_prompt_text(
    main_theme,
    key_factors,
    strengths,
    challenges,
    contradictions,
    dominant_elements,
    dominant_modes,
    dominant_houses,
    chart_type="lunar",
) -> str:
    """Строит текст промпта из сырых данных."""
    mt = main_theme

    main_theme_text = ""
    if mt:
        main_theme_text = (
            f"Главная тема карты:\n"
            f"- Планета: {getattr(mt, 'planet', mt.get('planet', '?'))}\n"
            f"- Дом: {getattr(mt, 'house', mt.get('house', '?'))}\n"
            f"- Знак: {getattr(mt, 'sign', mt.get('sign', '?'))}\n"
            f"- Диспозитор: {getattr(mt, 'dispositor', mt.get('dispositor', '?'))}\n"
        )

    key_factors_text = ""
    if key_factors:
        key_factors_text = "Ключевые факторы (по важности):\n"
        for i, f in enumerate(key_factors[:5], 1):
            obj = f.get('object', '?') if isinstance(f, dict) else getattr(f, 'object', '?')
            importance = f.get('importance', 0) if isinstance(f, dict) else getattr(f, 'importance', 0)
            reasons = f.get('importance_reasons', []) if isinstance(f, dict) else getattr(f, 'importance_reasons', [])
            reasons_str = ', '.join(reasons) if reasons else ''
            key_factors_text += f"{i}. {obj} (важность: {importance}) — {reasons_str}\n"

    strengths_text = ""
    if strengths:
        strengths_text = "Сильные стороны карты:\n"
        for s in strengths[:5]:
            obj = s.get('object', '?') if isinstance(s, dict) else getattr(s, 'object', '?')
            reasons = s.get('confidence_reasons', []) if isinstance(s, dict) else getattr(s, 'confidence_reasons', [])
            reasons_str = ', '.join(reasons) if reasons else ''
            strengths_text += f"- {obj}: {reasons_str}\n"

    challenges_text = ""
    if challenges:
        challenges_text = "Слабые места:\n"
        for c in challenges[:5]:
            obj = c.get('object', '?') if isinstance(c, dict) else getattr(c, 'object', '?')
            reasons = c.get('confidence_reasons', []) if isinstance(c, dict) else getattr(c, 'confidence_reasons', [])
            reasons_str = ', '.join(reasons) if reasons else ''
            challenges_text += f"- {obj}: {reasons_str}\n"

    contradictions_text = ""
    if contradictions:
        contradictions_text = "Противоречия:\n"
        for c in contradictions:
            p1 = c.get('planet1', '?') if isinstance(c, dict) else getattr(c, 'planet1', '?')
            p2 = c.get('planet2', '?') if isinstance(c, dict) else getattr(c, 'planet2', '?')
            contradictions_text += f"- Оппозиция {p1} — {p2}\n"

    dominants_text = ""
    if dominant_elements or dominant_modes or dominant_houses:
        dominants_text = "Доминанты карты:\n"
        if dominant_elements:
            dominants_text += f"- Стихии: {', '.join(dominant_elements)}\n"
        if dominant_modes:
            dominants_text += f"- Кресты: {', '.join(dominant_modes)}\n"
        if dominant_houses:
            dominants_text += f"- Дома: {', '.join(str(h) for h in dominant_houses)}\n"

    chart_name = "Лунар" if chart_type == "lunar" else "Натальная карта"

    return f"""Ты — астролог классической школы. Интерпретируй {chart_name}.

{main_theme_text}
{key_factors_text}
{strengths_text}
{challenges_text}
{contradictions_text}
{dominants_text}

=== ЖЁСТКИЕ ПРАВИЛА (соблюдай неукоснительно) ===

1. УПРАВИТЕЛИ ЗНАКОВ ТОЛЬКО КЛАССИЧЕСКИЕ:
Овен — Марс, Телец — Венера, Близнецы — Меркурий, Рак — Луна,
Лев — Солнце, Дева — Меркурий, Весы — Венера, Скорпион — Марс,
Стрелец — Юпитер, Козерог — Сатурн, Водолей — САТУРН, Рыбы — Юпитер.
Уран, Нептун, Плутон НЕ управляют знаками.

2. Начни с ГЛАВНОЙ ТЕМЫ. Она уже определена — используй её.

3. Упомяни СИЛЬНЫЕ СТОРОНЫ — то, что помогает главной теме.

4. Укажи СЛАБЫЕ МЕСТА — то, что важно, но проявляется с трудом.

5. Опиши ПРОТИВОРЕЧИЯ, если они есть.

6. НЕ используй шаблонные значения знаков.
   Тема месяца определяется по ДОМУ и ДИСПОЗИТОРУ, а не по знаку.

7. Пиши на русском языке. Дай развёрнутый прогноз (3-4 абзаца).
   Не используй markdown."""