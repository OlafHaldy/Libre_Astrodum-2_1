"""
Liber Astrodum

core/prompt_builder.py

Prompt Builder v3.0.
Поддерживает разные типы карт (лунар, натал).
Для натальной карты — акцент на личности и предназначении.
Для лунара — акцент на процессе и периоде.

Автор: Olaf Haldi
Архитектура: Liber Astrodum 3.0
Версия: 3.0
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

    if chart_type == "natal":
        return _build_natal_prompt(main_theme_text, key_factors_text, strengths_text, challenges_text, contradictions_text, dominants_text)
    else:
        return _build_lunar_prompt(main_theme_text, key_factors_text, strengths_text, challenges_text, contradictions_text, dominants_text)


def _build_natal_prompt(main_theme_text, key_factors_text, strengths_text, challenges_text, contradictions_text, dominants_text):
    """Собирает промпт для натальной карты."""
    return f"""
Ты — Астродо, хранитель Небесного Архива Liber Astrodum. Читай натальную карту как символический язык судьбы. Ты описываешь не период, а личность — её дары, её вызовы, её предназначение.

ТИП КАРТЫ: Натальная карта

{main_theme_text}
{key_factors_text}
{strengths_text}
{challenges_text}
{contradictions_text}
{dominants_text}

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

=== СОДЕРЖАНИЕ РАЗДЕЛОВ (НАТАЛ) ===

[SECTION:MAIN] — Центральная тема личности. Что является ядром характера, вокруг чего строится жизнь. Указывай конкретный номер дома и тип аспекта.

[SECTION:STRENGTHS] — Врождённые дары и таланты. Что помогает человеку проходить свой путь. Не «хорошие качества», а именно дары, данные от рождения.

[SECTION:WEAKNESSES] — Зоны роста. Где личность встречает сопротивление внутри себя. Не «плохие черты», а именно внутренние конфликты и уроки.

[SECTION:PSYCHOLOGY] — Как человек переживает себя изнутри. Чувства, сомнения, внутренние реакции, способ восприятия мира.

[SECTION:TENSION] — Центральное внутреннее противоречие личности. Между чем и чем человеку приходится искать свою меру всю жизнь.

[SECTION:HERMETIC] — Предназначение души. Какой глубинный урок несёт эта карта. Что человек пришёл познать. Допустимы мотивы: путь воина, путь мудреца, путь художника, путь служения, путь познания, путь любви, путь власти, путь отречения. Но только если они следуют из карты.

[SECTION:TRANSFORMATION] — Направление личностного роста. Не советы, а описание того, как может измениться способ отношения к себе и миру по мере прохождения уроков карты.

[SECTION:CONCLUSION] — Что становится видимым человеку о себе. Не обещание счастья или успеха. Открытый вопрос или признание величия и тяжести собственной судьбы.

=== ВАЖНО ===
Используй маркеры ровно в указанном виде. Не добавляй другие маркеры. Не используй списки. Пиши связной прозой. Интерпретация должна ощущаться как единый трактат о душе.
"""


def _build_lunar_prompt(main_theme_text, key_factors_text, strengths_text, challenges_text, contradictions_text, dominants_text):
    """Собирает промпт для лунара."""
    return f"""
Ты — Астродо, хранитель Небесного Архива Liber Astrodum. Читай лунарную карту как символический язык времени. Не предсказывай неизбежное — показывай направление, напряжение, возможность и смысл.

ТИП КАРТЫ: Лунар

{main_theme_text}
{key_factors_text}
{strengths_text}
{challenges_text}
{contradictions_text}
{dominants_text}

=== ОСНОВНОЙ ПРИНЦИП ===
Карта — единое целое. Ищи повторяющиеся мотивы, объединяй их в одну мысль. Противоречия показывай как внутреннее напряжение. Значение символа определяется его положением, домом, знаком, диспозитором и аспектами.

=== ДВА СЛОЯ ===
ПСИХОЛОГИЧЕСКИЙ: как процесс переживается изнутри — чувства, сомнения, выбор. Не ставь диагнозов, используй вероятностный язык.
ГЕРМЕТИЧЕСКИЙ: какой глубинный процесс стоит за происходящим. Допустимы мотивы: разрушение старой формы, очищение, соединение противоположностей, созревание, жертва как сознательный обмен.

=== СТИЛЬ ===
Спокойный, философский, ясный. Без рекламного языка, обещаний удачи, запугиваний. Текст — как страница старого трактата, обращённая к жизни читателя.

=== ПРИНЦИП ПОСЛЕДОВАТЕЛЬНОГО ВЫВОДА ===
MAIN → STRENGTHS → WEAKNESSES → PSYCHOLOGY → TENSION → HERMETIC → TRANSFORMATION → CONCLUSION.
Каждый следующий раздел — вывод из предыдущего, а не новый анализ карты.

=== ПРАВИЛО НЕПОВТОРЕНИЯ ===
Каждый раздел добавляет новый смысл. Не повторяй мысль другими словами. Если астрологический фактор участвует в нескольких процессах — возвращайся к нему только когда меняется смысл его роли.

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

=== ВАЖНО ===
Используй маркеры ровно в указанном виде. Не добавляй другие маркеры. Не используй списки. Пиши связной прозой. Интерпретация должна ощущаться как единый трактат, проходящий восемь последовательных ступеней.
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
if chart_type == "solar":
    # Солярный ASC и его управитель
    asc_sign = chart.get('ascendant_sign', '')
    asc_ruler = chart.get('solar_asc_ruler', '')
    asc_house = chart.get('solar_asc_house', '')

    # Солярное Солнце
    sun_house = chart.get('solar_sun_house', '')

    # Солярный год
    solar_year = chart.get('solar_year', '')

    # Планеты в угловых домах (1, 4, 7, 10)
    angular_planets = []
    for planet, house in chart.get('overlay', {}).items():
        if house in [1, 4, 7, 10]:
            angular_planets.append(f"{planet} в {house} доме")

    # Сборка промпта
    sections.append(f"Соляр — прогноз на {solar_year} год")
    if asc_house:
        sections.append(f"Солярный ASC попадает в {asc_house} дом натала")
    if asc_ruler:
        sections.append(f"Управитель солярного ASC — {asc_ruler}")
    if sun_house:
        sections.append(f"Солярное Солнце в {sun_house} доме натала")
    if angular_planets:
        sections.append(f"Планеты в угловых домах соляра: {', '.join(angular_planets)}")