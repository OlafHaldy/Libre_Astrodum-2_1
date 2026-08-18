"""
Liber Astrodum

core/prompt_builder.py

Prompt Builder v3.1.
Поддерживает разные типы карт (лунар, натал, соляр).

Автор: Olaf Haldi
Архитектура: Liber Astrodum 3.0
Версия: 3.1
"""


def build_prompt(prompt_context, chart_type="lunar") -> str:
    """
    Строит текст промпта из PromptContext.
    Выбирает ветку в зависимости от типа карты.
    """
    ctx = prompt_context
    mt = ctx.main_theme

    main_theme_text = ""
    if mt:
        if isinstance(mt, dict):
            planet = mt.get("planet", "?")
            house = mt.get("house", "?")
            sign = mt.get("sign", "?")
            dispositor = mt.get("dispositor", "?")
        else:
            planet = getattr(mt, "planet", "?")
            house = getattr(mt, "house", "?")
            sign = getattr(mt, "sign", "?")
            dispositor = getattr(mt, "dispositor", "?")

        main_theme_text = (
            f"Главная тема карты:\n"
            f"- Планета: {planet}\n"
            f"- Дом: {house}\n"
            f"- Знак: {sign}\n"
            f"- Диспозитор: {dispositor}\n"
        )

    key_factors_text = ""
    if ctx.key_factors:
        key_factors_text = "Ключевые факторы (по важности):\n"
        for i, f in enumerate(ctx.key_factors[:5], 1):
            obj = f.get('object', '?') if isinstance(f, dict) else getattr(f, 'object', '?')
            importance = f.get('importance', 0) if isinstance(f, dict) else getattr(f, 'importance', 0)
            reasons = f.get('importance_reasons', []) if isinstance(f, dict) else getattr(f, 'importance_reasons', [])
            reasons_str = ', '.join(reasons) if reasons else ''
            key_factors_text += f"{i}. {obj} (важность: {importance}) — {reasons_str}\n"

    strengths_text = ""
    if ctx.strengths:
        strengths_text = "Сильные стороны карты:\n"
        for s in ctx.strengths[:5]:
            obj = s.get('object', '?') if isinstance(s, dict) else getattr(s, 'object', '?')
            reasons = s.get('confidence_reasons', []) if isinstance(s, dict) else getattr(s, 'confidence_reasons', [])
            reasons_str = ', '.join(reasons) if reasons else ''
            strengths_text += f"- {obj}: {reasons_str}\n"

    challenges_text = ""
    if ctx.challenges:
        challenges_text = "Слабые места:\n"
        for c in ctx.challenges[:5]:
            obj = c.get('object', '?') if isinstance(c, dict) else getattr(c, 'object', '?')
            reasons = c.get('confidence_reasons', []) if isinstance(c, dict) else getattr(c, 'confidence_reasons', [])
            reasons_str = ', '.join(reasons) if reasons else ''
            challenges_text += f"- {obj}: {reasons_str}\n"

    contradictions_text = ""
    if ctx.contradictions:
        contradictions_text = "Противоречия:\n"
        for c in ctx.contradictions:
            p1 = c.get('planet1', '?') if isinstance(c, dict) else getattr(c, 'planet1', '?')
            p2 = c.get('planet2', '?') if isinstance(c, dict) else getattr(c, 'planet2', '?')
            contradictions_text += f"- Оппозиция {p1} — {p2}\n"

    dominants_text = ""
    if ctx.dominant_elements or ctx.dominant_modes or ctx.dominant_houses:
        dominants_text = "Доминанты карты:\n"
        if ctx.dominant_elements:
            dominants_text += f"- Стихии: {', '.join(ctx.dominant_elements)}\n"
        if ctx.dominant_modes:
            dominants_text += f"- Кресты: {', '.join(ctx.dominant_modes)}\n"
        if ctx.dominant_houses:
            dominants_text += f"- Дома: {', '.join(str(h) for h in ctx.dominant_houses)}\n"

    # Дополнительные данные (рецепции, акцидентальные достоинства)
    extra_text = ""
    if hasattr(ctx, 'receptions_text') and ctx.receptions_text:
        extra_text += f"\nВзаимные рецепции:\n{ctx.receptions_text}\n"
    
    if hasattr(ctx, 'accidental_dignities_text') and ctx.accidental_dignities_text:
        extra_text += f"\nАкцидентальные достоинства:\n{ctx.accidental_dignities_text}\n"

    full_context = main_theme_text + key_factors_text + strengths_text + challenges_text + contradictions_text + dominants_text + extra_text

    if chart_type == "natal":
        return _build_natal_prompt(full_context)
    elif chart_type == "solar":
        return _build_solar_prompt(full_context)
    else:
        return _build_lunar_prompt(full_context)


def _build_natal_prompt(context_text):
    """Собирает промпт для натальной карты."""
    return f"""
Ты — Астродо, хранитель Небесного Архива Liber Astrodum. Читай натальную карту как символический язык судьбы. Ты описываешь не период, а личность — её дары, её вызовы, её предназначение.

ТИП КАРТЫ: Натальная карта

{context_text}

=== ОСНОВНОЙ ПРИНЦИП ===
Карта — единое целое. Ищи повторяющиеся мотивы, объединяй их в одну мысль. Противоречия показывай как внутреннюю драму личности. Значение символа определяется его положением, домом, знаком, диспозитором и аспектами.

=== ДВА СЛОЯ ===
ПСИХОЛОГИЧЕСКИЙ: врождённые черты, таланты, внутренние конфликты, способ выстраивать отношения с миром.
ГЕРМЕТИЧЕСКИЙ: предназначение души, центральный урок воплощения, что человек пришёл познать и чем овладеть.

=== СТИЛЬ ===
Спокойный, философский, ясный. Текст — как страница старого трактата о человеческой душе. Никаких «вам нужно», «следует развивать», «будьте осторожны».

=== ФОРМАТ ОТВЕТА ===
Верни ровно 8 разделов с маркерами:
[SECTION:MAIN] — Центральная тема личности
[SECTION:STRENGTHS] — Дары и таланты
[SECTION:WEAKNESSES] — Зоны роста и внутренние конфликты
[SECTION:PSYCHOLOGY] — Как личность переживает себя изнутри
[SECTION:TENSION] — Центральное внутреннее противоречие
[SECTION:HERMETIC] — Предназначение души
[SECTION:TRANSFORMATION] — Направление личностного роста
[SECTION:CONCLUSION] — Что становится видимым о себе

Каждый раздел — отдельный абзац. Между разделами — одна пустая строка. Не добавляй вступление и заключение вне секций.
"""


def _build_lunar_prompt(context_text):
    """Собирает промпт для лунара."""
    return f"""
Ты — Астродо, хранитель Небесного Архива Liber Astrodum. Читай лунарную карту как символический язык времени. Не предсказывай неизбежное — показывай направление, напряжение, возможность и смысл.

ТИП КАРТЫ: Лунар

{context_text}

=== ОСНОВНОЙ ПРИНЦИП ===
Карта — единое целое. Ищи повторяющиеся мотивы, объединяй их в одну мысль. Противоречия показывай как внутреннее напряжение. Значение символа определяется его положением, домом, знаком, диспозитором и аспектами.

=== ДВА СЛОЯ ===
ПСИХОЛОГИЧЕСКИЙ: как процесс переживается изнутри — чувства, сомнения, выбор. Не ставь диагнозов, используй вероятностный язык.
ГЕРМЕТИЧЕСКИЙ: какой глубинный процесс стоит за происходящим. Допустимы мотивы: разрушение старой формы, очищение, соединение противоположностей, созревание, жертва как сознательный обмен.

=== ФОРМАТ ОТВЕТА ===
Верни ровно 8 разделов с маркерами:
[SECTION:MAIN] — Центральный внутренний процесс периода
[SECTION:STRENGTHS] — Что помогает процессу развиваться
[SECTION:WEAKNESSES] — Где процесс встречает сопротивление
[SECTION:PSYCHOLOGY] — Как процесс переживается изнутри
[SECTION:TENSION] — Конфликт сил
[SECTION:HERMETIC] — Глубинный смысл процесса
[SECTION:TRANSFORMATION] — Как меняется внутренняя позиция
[SECTION:CONCLUSION] — Что становится видимым после прохождения

Каждый раздел — отдельный абзац. Между разделами — одна пустая строка.
"""


def _build_solar_prompt(context_text):
    """Собирает промпт для соляра."""
    return f"""
Ты — Астродо, хранитель Небесного Архива Liber Astrodum. Читай солярную карту как символический язык года. Это карта возвращения Солнца — показывает ключевые темы и вызовы предстоящего года.

ТИП КАРТЫ: Соляр

{context_text}

=== ОСНОВНОЙ ПРИНЦИП ===
Соляр — это карта года. Главная тема определяется солярным ASC, его управителем и солярным Солнцем в натальном доме. Планеты в угловых домах соляра (1, 4, 7, 10) — самые важные.

=== ФОРМАТ ОТВЕТА ===
Верни ровно 8 разделов с маркерами:
[SECTION:MAIN] — Главная тема года
[SECTION:STRENGTHS] — Что будет поддерживать в этом году
[SECTION:WEAKNESSES] — Где будут вызовы
[SECTION:PSYCHOLOGY] — Как будет переживаться этот год
[SECTION:TENSION] — Основное напряжение года
[SECTION:HERMETIC] — Глубинный смысл этого года
[SECTION:TRANSFORMATION] — Как изменится внутренняя позиция
[SECTION:CONCLUSION] — Что станет видимым к концу года

Каждый раздел — отдельный абзац. Между разделами — одна пустая строк.
"""


def build_prompt_from_dict(prompt_context_dict: dict, chart_type="lunar") -> str:
    """
    Строит промпт из словаря.
    Конвертирует dict в объект PromptContext и вызывает build_prompt.
    """
    class PromptContextObj:
        pass

    class SimpleObj:
        def __init__(self, d):
            self.__dict__.update(d)

    ctx = PromptContextObj()

    mt_dict = prompt_context_dict.get("main_theme", {})
    ctx.main_theme = SimpleObj(mt_dict) if mt_dict else None

    ctx.key_factors = prompt_context_dict.get("key_factors", [])
    ctx.strengths = prompt_context_dict.get("strengths", [])
    ctx.challenges = prompt_context_dict.get("challenges", [])

    ctx.contradictions = []
    for c in prompt_context_dict.get("contradictions", []):
        ctx.contradictions.append(SimpleObj(c))

    ctx.dominant_elements = prompt_context_dict.get("dominant_elements", [])
    ctx.dominant_modes = prompt_context_dict.get("dominant_modes", [])
    ctx.dominant_houses = prompt_context_dict.get("dominant_houses", [])

    # Добавляем рецепции и акцидентальные достоинства
    ctx.receptions_text = prompt_context_dict.get("receptions", "")
    ctx.accidental_dignities_text = prompt_context_dict.get("accidental_dignities", "")

    return build_prompt(ctx, chart_type=chart_type)


def build_prompt_text(
    main_theme, key_factors, strengths, challenges, contradictions,
    dominant_elements, dominant_modes, dominant_houses, chart_type="lunar",
) -> str:
    """Строит текст промпта из сырых данных (для обратной совместимости)."""
    class SimpleObj:
        def __init__(self, d):
            self.__dict__.update(d)

    class PromptContextObj:
        pass

    ctx = PromptContextObj()
    ctx.main_theme = SimpleObj(main_theme) if isinstance(main_theme, dict) else main_theme
    ctx.key_factors = key_factors
    ctx.strengths = strengths
    ctx.challenges = challenges
    ctx.contradictions = [SimpleObj(c) if isinstance(c, dict) else c for c in contradictions]
    ctx.dominant_elements = dominant_elements
    ctx.dominant_modes = dominant_modes
    ctx.dominant_houses = dominant_houses

    return build_prompt(ctx, chart_type=chart_type)