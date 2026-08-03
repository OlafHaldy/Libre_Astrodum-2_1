"""
Liber Astrodum

core/reasoning.py

Reasoning Engine v2.0.
Первый модуль, который строит логические выводы.

Отвечает на вопрос «Что из этого следует?» на основе:
- Chart
- PriorityCollection
- DominantReport

Возвращает ReasoningReport — СТРУКТУРУ, а не текст.
Текст генерирует Prompt Engine.

Спецификация: docs/PIPELINE_SPEC.md, Шаг 7

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.0
"""

# ==========================================================
# КОНСТАНТЫ
# ==========================================================

SUPPORTING_IMPORTANCE_MIN = 30
SUPPORTING_CONFIDENCE_MIN = 50

WEAKENING_IMPORTANCE_MIN = 25
WEAKENING_CONFIDENCE_MAX = 45

PATTERN_HOUSE_MIN = 3

# ==========================================================
# ОБЪЕКТЫ ВЫВОДА
# ==========================================================

class MainTheme:
    """Главная тема карты."""

    def __init__(self, planet, house, sign, dispositor, confidence):
        self.planet = planet
        self.house = house
        self.sign = sign
        self.dispositor = dispositor
        self.confidence = confidence

    def to_dict(self) -> dict:
        return {
            "planet": self.planet,
            "house": self.house,
            "sign": self.sign,
            "dispositor": self.dispositor,
            "confidence": self.confidence,
        }

    def __repr__(self) -> str:
        return (f"<MainTheme planet={self.planet} house={self.house} "
                f"dispositor={self.dispositor}>")


class SupportingFactor:
    """Фактор, усиливающий главную тему."""

    def __init__(self, object_name, reason):
        self.object = object_name
        self.reason = reason

    def to_dict(self) -> dict:
        return {"object": self.object, "reason": self.reason}

    def __repr__(self) -> str:
        return f"<SupportingFactor {self.object}: {self.reason}>"


class WeakeningFactor:
    """Фактор, ослабляющий проявление."""

    def __init__(self, object_name, reason):
        self.object = object_name
        self.reason = reason

    def to_dict(self) -> dict:
        return {"object": self.object, "reason": self.reason}

    def __repr__(self) -> str:
        return f"<WeakeningFactor {self.object}: {self.reason}>"


class Contradiction:
    """Противоречие в карте."""

    def __init__(self, type_name, planet1, planet2):
        self.type = type_name
        self.planet1 = planet1
        self.planet2 = planet2

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "planet1": self.planet1,
            "planet2": self.planet2,
        }

    def __repr__(self) -> str:
        return f"<Contradiction {self.type} {self.planet1}-{self.planet2}>"


class ConfirmedPattern:
    """Паттерн, подтверждённый несколькими независимыми факторами."""

    def __init__(self, pattern_type, **kwargs):
        self.type = pattern_type
        self.data = kwargs

    def to_dict(self) -> dict:
        return {"type": self.type, **self.data}

    def __repr__(self) -> str:
        return f"<ConfirmedPattern {self.type}>"


class ReasoningReport:
    """
    Структурированный логический вывод о карте.
    Не содержит текста — только структуры.
    """

    def __init__(self, main_theme, supporting, weakening, contradictions, confirmed):
        self.main_theme = main_theme
        self.supporting = supporting
        self.weakening = weakening
        self.contradictions = contradictions
        self.confirmed = confirmed

    def to_dict(self) -> dict:
        return {
            "main_theme": self.main_theme.to_dict() if self.main_theme else None,
            "supporting_factors": [s.to_dict() for s in self.supporting],
            "weakening_factors": [w.to_dict() for w in self.weakening],
            "contradictions": [c.to_dict() for c in self.contradictions],
            "confirmed_patterns": [p.to_dict() for p in self.confirmed],
        }

    def __repr__(self) -> str:
        return (f"<ReasoningReport theme={self.main_theme} "
                f"+{len(self.supporting)} -{len(self.weakening)} "
                f"!{len(self.contradictions)} ~{len(self.confirmed)}>")


# ==========================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ==========================================================

def build_reasoning_report(chart, priority, dominants) -> ReasoningReport:
    """
    Строит логический вывод о карте.

    Parameters
    ----------
    chart : Chart
    priority : PriorityCollection
    dominants : DominantReport

    Returns
    -------
    ReasoningReport
    """
    return ReasoningReport(
        main_theme=_determine_main_theme(chart, priority),
        supporting=_find_supporting_factors(priority, chart),
        weakening=_find_weakening_factors(priority, chart),
        contradictions=_find_contradictions(priority),
        confirmed=_find_confirmed_patterns(priority, dominants),
    )


# ==========================================================
# 1. ГЛАВНАЯ ТЕМА
# ==========================================================

def _determine_main_theme(chart, priority) -> MainTheme | None:
    """
    Определяет главную тему по факту с наивысшим importance.
    Возвращает структуру MainTheme, а не текст.
    """
    main_fact = priority.main
    if not main_fact:
        return None

    planet = main_fact.get('object', '')
    planet_data = chart.get_planet(planet)
    if not planet_data:
        return None

    return MainTheme(
        planet=planet,
        house=planet_data.get('house'),
        sign=planet_data.get('sign'),
        dispositor=chart.get_dispositor(planet),
        confidence=main_fact.get('confidence', 50),
    )


# ==========================================================
# 2. УСИЛИВАЮЩИЕ ФАКТОРЫ
# ==========================================================

def _find_supporting_factors(priority, chart) -> list[SupportingFactor]:
    """
    Факты с высокой importance и confidence,
    связанные с главной планетой или её диспозитором.
    """
    main_fact = priority.main
    if not main_fact:
        return []

    main_planet = main_fact.get('object', '')
    dispositor = chart.get_dispositor(main_planet)

    supporting = []
    seen = set()

    for fact in priority:
        if fact.get('importance', 0) < SUPPORTING_IMPORTANCE_MIN:
            continue
        if fact.get('confidence', 50) < SUPPORTING_CONFIDENCE_MIN:
            continue

        obj = fact.get('object', '')
        if obj != main_planet and obj != dispositor:
            continue

        for reason in fact.get('importance_reasons', []):
            key = (obj, reason)
            if key not in seen:
                seen.add(key)
                supporting.append(SupportingFactor(obj, reason))

    return supporting


# ==========================================================
# 3. ОСЛАБЛЯЮЩИЕ ФАКТОРЫ
# ==========================================================

def _find_weakening_factors(priority, chart) -> list[WeakeningFactor]:
    """
    Факты с высокой importance, но низкой confidence.
    Важные, но слабые места карты.
    """
    main_fact = priority.main
    main_planet = main_fact.get('object', '') if main_fact else ''

    weakening = []
    seen = set()

    for fact in priority:
        importance = fact.get('importance', 0)
        confidence = fact.get('confidence', 50)

        if importance < WEAKENING_IMPORTANCE_MIN:
            continue
        if confidence >= WEAKENING_CONFIDENCE_MAX:
            continue

        obj = fact.get('object', '')
        if obj != main_planet and importance < 35:
            continue

        for reason in fact.get('confidence_reasons', []):
            key = (obj, reason)
            if key not in seen:
                seen.add(key)
                weakening.append(WeakeningFactor(obj, reason))

    return weakening


# ==========================================================
# 4. ПРОТИВОРЕЧИЯ
# ==========================================================

def _find_contradictions(priority) -> list[Contradiction]:
    """
    Ищет оппозиции между важными планетами.
    """
    top_planets = set(
        f.get('object', '') for f in priority.top(5)
    )

    contradictions = []

    for fact in priority.aspects():
        data = fact.get('data', {})
        p1 = data.get('planet1', '')
        p2 = data.get('planet2', '')
        asp_type = data.get('type', '')

        if asp_type == 'opposition' and p1 in top_planets and p2 in top_planets:
            contradictions.append(Contradiction("opposition", p1, p2))

    return contradictions


# ==========================================================
# 5. ПОДТВЕРЖДЁННЫЕ ПАТТЕРНЫ
# ==========================================================

def _find_confirmed_patterns(priority, dominants) -> list[ConfirmedPattern]:
    """
    Темы, подтверждённые несколькими независимыми факторами.
    """
    confirmed = []

    # Дома с 3+ факторами
    house_counts = {}
    for f in priority.by_type('house_ruler'):
        h = f.get('data', {}).get('house')
        if h:
            house_counts[h] = house_counts.get(h, 0) + 1

    for house, count in house_counts.items():
        if count >= PATTERN_HOUSE_MIN:
            confirmed.append(ConfirmedPattern(
                "house_cluster", house=house, count=count
            ))

    # Доминирующие стихии
    if dominants.elements:
        confirmed.append(ConfirmedPattern(
            "dominant_elements", elements=dominants.elements
        ))

    # Доминирующие планеты
    if dominants.primary:
        confirmed.append(ConfirmedPattern(
            "dominant_planets",
            planets=[p.name for p in dominants.primary]
        ))

    return confirmed