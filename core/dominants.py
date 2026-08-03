"""
Liber Astrodum

core/dominants.py

Dominant Engine v2.2.
Определяет доминирующие планеты, стихии, кресты и дома.

Использует PriorityCollection для взвешивания важности планет.
Хранит все промежуточные scores в DominantReport.

Спецификация: docs/PIPELINE_SPEC.md, Шаг 6

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.2
"""

from dignities.zodiac import SIGN_ELEMENT, SIGN_MODE

# ==========================================================
# КОНСТАНТЫ
# ==========================================================

DOMINANT_THRESHOLD = 0.70      # порог для доминирующих планет
SECONDARY_THRESHOLD = 0.40     # порог для второстепенных планет
ELEMENT_THRESHOLD = 0.90       # порог для стихий/крестов/домов


class DominantPlanet:
    """Планета с её суммарным importance."""

    def __init__(self, name: str, score: int):
        self.name = name
        self.score = score

    def to_dict(self) -> dict:
        return {"planet": self.name, "score": self.score}

    def __repr__(self) -> str:
        return f"<DominantPlanet {self.name}={self.score}>"


class DominantReport:
    """
    Отчёт о доминантах карты.

    Атрибуты:
    - primary: список DominantPlanet (>= 70% максимума)
    - secondary: список DominantPlanet (>= 40% максимума)
    - elements: список доминирующих стихий
    - modes: список доминирующих крестов
    - houses: список доминирующих домов
    - planet_scores: полный словарь {планета: importance}
    - element_scores: полный словарь {стихия: сумма importance}
    - mode_scores: полный словарь {крест: сумма importance}
    - house_scores: полный словарь {дом: сумма importance}
    """

    def __init__(
        self,
        primary,
        secondary,
        elements,
        modes,
        houses,
        planet_scores,
        element_scores,
        mode_scores,
        house_scores,
    ):
        self.primary = primary
        self.secondary = secondary
        self.elements = elements
        self.modes = modes
        self.houses = houses
        self.planet_scores = planet_scores
        self.element_scores = element_scores
        self.mode_scores = mode_scores
        self.house_scores = house_scores

    def to_dict(self) -> dict:
        return {
            "primary": [p.to_dict() for p in self.primary],
            "secondary": [p.to_dict() for p in self.secondary],
            "elements": self.elements,
            "modes": self.modes,
            "houses": self.houses,
            "planet_scores": self.planet_scores,
            "element_scores": self.element_scores,
            "mode_scores": self.mode_scores,
            "house_scores": self.house_scores,
        }

    def __repr__(self) -> str:
        return (f"<DominantReport primary={[p.name for p in self.primary]} "
                f"elements={self.elements} houses={self.houses}>")


# ==========================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ==========================================================

def build_dominant_report(chart, priority_collection) -> DominantReport:
    """
    Строит DominantReport.

    Parameters
    ----------
    chart : Chart
    priority_collection : PriorityCollection

    Returns
    -------
    DominantReport
    """
    planet_importance = _build_planet_importance(chart, priority_collection)
    element_scores = _build_element_scores(chart, planet_importance)
    mode_scores = _build_mode_scores(chart, planet_importance)
    house_scores = _build_house_scores(chart, planet_importance)

    return DominantReport(
        primary=_find_primary_planets(planet_importance),
        secondary=_find_secondary_planets(planet_importance),
        elements=_find_top_by_threshold(element_scores, ELEMENT_THRESHOLD),
        modes=_find_top_by_threshold(mode_scores, ELEMENT_THRESHOLD),
        houses=_find_top_by_threshold(house_scores, ELEMENT_THRESHOLD),
        planet_scores=planet_importance,
        element_scores=element_scores,
        mode_scores=mode_scores,
        house_scores=house_scores,
    )


# ==========================================================
# КАРТА IMPORTANCE ПЛАНЕТ
# ==========================================================

def _build_planet_importance(chart, priority) -> dict:
    """Суммирует importance всех фактов для каждой планеты."""
    scores = {planet: 0 for planet in chart.planets}

    for fact in priority:
        obj = fact.get('object', '')
        if obj in scores:
            scores[obj] += fact.get('importance', 0)

    return scores


# ==========================================================
# ДОМИНИРУЮЩИЕ ПЛАНЕТЫ (primary / secondary)
# ==========================================================

def _find_primary_planets(planet_importance: dict) -> list[DominantPlanet]:
    """Планеты >= 70% от максимума."""
    return _find_planets_by_threshold(planet_importance, DOMINANT_THRESHOLD)


def _find_secondary_planets(planet_importance: dict) -> list[DominantPlanet]:
    """Планеты >= 40% от максимума, но не primary."""
    primary_names = {p.name for p in _find_primary_planets(planet_importance)}
    candidates = _find_planets_by_threshold(planet_importance, SECONDARY_THRESHOLD)
    return [p for p in candidates if p.name not in primary_names]


def _find_planets_by_threshold(planet_importance: dict, threshold: float) -> list[DominantPlanet]:
    """Планеты с суммой >= threshold * max_score."""
    if not planet_importance:
        return []

    max_score = max(planet_importance.values())
    if max_score == 0:
        return []

    cutoff = max_score * threshold

    result = [
        DominantPlanet(planet, score)
        for planet, score in planet_importance.items()
        if score >= cutoff
    ]
    result.sort(key=lambda p: p.score, reverse=True)
    return result


# ==========================================================
# СТИХИИ
# ==========================================================

def _build_element_scores(chart, planet_importance: dict) -> dict:
    """Суммирует importance планет в каждой стихии."""
    scores = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}

    for planet, data in chart.planets.items():
        sign = data.get("sign", "")
        element = SIGN_ELEMENT.get(sign)
        if element:
            scores[element] += planet_importance.get(planet, 0)

    return scores


# ==========================================================
# КРЕСТЫ (МОДАЛЬНОСТИ)
# ==========================================================

def _build_mode_scores(chart, planet_importance: dict) -> dict:
    """Суммирует importance планет в каждом кресте."""
    scores = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}

    for planet, data in chart.planets.items():
        sign = data.get("sign", "")
        mode = SIGN_MODE.get(sign)
        if mode:
            scores[mode] += planet_importance.get(planet, 0)

    return scores


# ==========================================================
# ДОМА
# ==========================================================

def _build_house_scores(chart, planet_importance: dict) -> dict:
    """Суммирует importance планет в каждом доме."""
    scores = {h: 0 for h in range(1, 13)}

    for planet, data in chart.planets.items():
        house = data.get("house")
        if house and house in scores:
            scores[house] += planet_importance.get(planet, 0)

    return scores


# ==========================================================
# ПОРОГОВЫЙ ФИЛЬТР
# ==========================================================

def _find_top_by_threshold(scores: dict, threshold: float) -> list:
    """
    Возвращает ключи с максимальным значением,
    а также те, что >= threshold * max_score.
    """
    if not scores:
        return []

    max_score = max(scores.values())
    if max_score == 0:
        return []

    cutoff = max_score * threshold
    result = [k for k, v in scores.items() if v >= cutoff]

    # Сортируем: сначала числовые ключи (дома), потом строковые
    try:
        result.sort()
    except TypeError:
        result.sort(key=str)

    return result
    # ==========================================================
# TODO(v2.3) — осознанно отложенные улучшения
# ==========================================================
#
# □ Перенести пороги (DOMINANT_THRESHOLD, SECONDARY_THRESHOLD,
#   ELEMENT_THRESHOLD) в config.py
# □ DominantCategory с primary/secondary для элементов/модов/домов
# □ Учёт графа диспозиторов при подсчёте importance
# □ Учёт цепочек диспозиций (конечный диспозитор получает бонус)
# □ Вес главной планеты (лунар=Moon, соляр=Sun) через настройки
# □ Статистическая калибровка порогов на эталонных картах
#
# ==========================================================