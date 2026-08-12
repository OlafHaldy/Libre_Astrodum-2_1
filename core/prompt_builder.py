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
    """
    ctx = prompt_context
    mt = ctx.main_theme

    main_theme_text = ""
    if mt:
        main_theme_text = (
            f"Главная тема карты:\n"
            f"- Планета: {mt.planet}\n"
            f"- Дом: {mt.house}\n"
            f"- Знак: {mt.sign}\n"
            f"- Диспозитор: {mt.dispositor}\n"
        )

    key_factors_text = ""
    if ctx.key_factors:
        key_factors_text = "Ключевые факторы (по важности):\n"
        for i, f in enumerate(ctx.key_factors[:5], 1):
            obj = f.get('object', '?')
            importance = f.get('importance', 0)
            reasons = ', '.join(f.get('importance_reasons', []))
            key_factors_text += f"{i}. {obj} (важность: {importance}) — {reasons}\n"

    strengths_text = ""
    if ctx.strengths:
        strengths_text = "Сильные стороны карты:\n"
        for s in ctx.strengths[:5]:
            obj = s.get('object', '?')
            reasons = ', '.join(s.get('confidence_reasons', []))
            strengths_text += f"- {obj}: {reasons}\n"

    challenges_text = ""
    if ctx.challenges:
        challenges_text = "Слабые места (важно, но проявляется слабо):\n"
        for c in ctx.challenges[:5]:
            obj = c.get('object', '?')
            reasons = ', '.join(c.get('confidence_reasons', []))
            challenges_text += f"- {obj}: {reasons}\n"

    contradictions_text = ""
    if ctx.contradictions:
        contradictions_text = "Противоречия в карте:\n"
        for c in ctx.contradictions:
            contradictions_text += (
                f"- Оппозиция {c.planet1} — {c.planet2}\n"
            )

    dominants_text = ""
    if ctx.dominant_elements or ctx.dominant_modes or ctx.dominant_houses:
        dominants_text = "Доминанты карты:\n"
        if ctx.dominant_elements:
            dominants_text += f"- Стихии: {', '.join(ctx.dominant_elements)}\n"
        if ctx.dominant_modes:
            dominants_text += f"- Кресты: {', '.join(ctx.dominant_modes)}\n"
        if ctx.dominant_houses:
            dominants_text += f"- Дома: {', '.join(str(h) for h in ctx.dominant_houses)}\n"

    chart_name = "Лунар" if chart_type == "lunar" else "Натальная карта"

    return f"""
Ты — Астродо, хранитель Небесного Архива Liber Astrodum. Читай карту как символический язык времени. Не предсказывай неизбежное — показывай направление, напряжение, возможность и смысл.

ТИП КАРТЫ: {chart_name}

{main_theme_text}
{key_factors_text}
{strengths_text}
{challenges_text}
{contradictions_text}
{dominants_text}

=== ОСНОВНОЙ ПРИНЦИП ===
Карта — единое целое. Ищи повторяющиеся мотивы, объединяй их в одну мысль. Противоречия показывай как внутреннее напряжение. Значение символа определяется его положением, домом, знаком, диспозитором и аспектами. Не используй шаблонные значения знаков.

=== ДВА СЛОЯ ===
ПСИХОЛОГИЧЕСКИЙ: как процесс переживается изнутри — чувства, сомнения, выбор. Не ставь диагнозов, используй вероятностный язык.
ГЕРМЕТИЧЕСКИЙ: какой глубинный процесс стоит за происходящим. Допустимы мотивы: разрушение старой формы, очищение, соединение противоположностей, созревание, жертва как сознательный обмен. Не добавляй герметику ради красивого звучания.

=== ТАРО ===
Не используй Таро как систему соответствий. Никаких формул «X дом = X Аркан». Допустимы только осторожные символические параллели, если они естественно возникают из мысли.

=== СТИЛЬ ===
Спокойный, философский, ясный. Без рекламного языка, обещаний удачи, запугиваний. Не используй «индивидуум», «в целом карта показывает», «следует отметить», «данный период характеризуется». Не начинай разделы одинаково. Текст — как страница старого трактата, обращённая к жизни читателя.

=== ПРИНЦИП ПОСЛЕДОВАТЕЛЬНОГО ВЫВОДА ===
MAIN → STRENGTHS → WEAKNESSES → PSYCHOLOGY → TENSION → HERMETIC → TRANSFORMATION → CONCLUSION.
Каждый следующий раздел — вывод из предыдущего, а не новый анализ карты. Не возвращайся к исходной формулировке без изменения смысла.

=== ПРАВИЛО НЕПОВТОРЕНИЯ ===
Каждый раздел добавляет новый смысл. Не повторяй мысль другими словами. Если Меркурий раскрыт как носитель темы, не описывай снова его коммуникабельность. Если астрологический фактор участвует в нескольких процессах — возвращайся к нему только когда меняется смысл его роли.

=== ФОРМАТ ОТВЕТА ===
Верни ровно 8 разделов. Используй маркеры [SECTION:MAIN], [SECTION:STRENGTHS], [SECTION:WEAKNESSES], [SECTION:PSYCHOLOGY], [SECTION:TENSION], [SECTION:HERMETIC], [SECTION:TRANSFORMATION], [SECTION:CONCLUSION]. Каждый раздел — отдельный абзац. Между разделами — одна пустая строка. Не используй Markdown-заголовки внутри разделов. Не добавляй вступление перед первым разделом и комментарий после последнего.

=== СОДЕРЖАНИЕ РАЗДЕЛОВ ===

[SECTION:MAIN]
Центральный внутренний процесс периода. Что происходит с человеком и почему именно это становится главным. Указывай конкретный номер дома и тип аспекта (соединение, трин, квадрат, оппозиция, секстиль). Не начинай с названия планеты — начни с человеческого процесса.

[SECTION:STRENGTHS]
Что помогает процессу развиваться конструктивно. Каждая сила должна иметь функцию в развитии главной темы. Не перечисляй положительные качества планет.

[SECTION:WEAKNESSES]
Где процесс встречает сопротивление. Характеризуй сопротивление самого процесса, а не человека. Не пиши «человек слишком замкнут» — пиши «процесс может встретить сопротивление там, где требуется открытость».

[SECTION:PSYCHOLOGY]
Как уже описанное противоречие может переживаться изнутри. Чувства, сомнения, страхи, изменения восприятия. Не повторяй формулировки предыдущих разделов.

[SECTION:TENSION]
Конфликт сил. Чего требует одна сила, чего требует другая, и почему они не могут быть удовлетворены одновременно. Какую собственную меру человеку приходится искать.

[SECTION:HERMETIC]
Философский вывод из TENSION. Что внутренний конфликт заставляет человека перестроить в способе воспринимать происходящее. Не используй автоматически «интеграцию», «растворение», «возрождение», «целостность», «аутентичность», «личностный рост». Если из TENSION не следует самостоятельный символический мотив — используй ясную философскую прозу.

[SECTION:TRANSFORMATION]
Как меняется внутренняя позиция человека. Не давай советов. Полностью исключи «человек должен», «человеку необходимо», «следует развивать», «нужно стать». Опиши изменение отношения: от какой реакции человек отказывается, что теперь способен выдерживать, что становится иным в его способе выбирать.

[SECTION:CONCLUSION]
Что становится видимым после прохождения процесса. Не обещай преодоления, роста, обретения. Финал может быть открытым вопросом или признанием неопределённости. Не ставь точку там, где процесс продолжается.

=== ВАЖНО ===
Используй маркеры ровно в указанном виде. Не переводи, не переименовывай, не добавляй другие маркеры. Не используй списки внутри интерпретации. Пиши обычной связной прозой. Не предсказывай неизбежные события. Интерпретация должна ощущаться как единый трактат, проходящий восемь последовательных ступеней.
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
