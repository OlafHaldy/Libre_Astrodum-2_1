"""
Liber Astrodum

core/themes.py

Theme Engine v1.1.

Объединяет астрологические паттерны в структурированные
кандидаты смысловых тем.

Поток:

    Facts
      ↓
    Priorities
      ↓
    Relations
      ↓
    Patterns
      ↓
    Themes

Theme Engine НЕ генерирует текст.
Theme Engine НЕ использует LLM.
Theme Engine НЕ выдаёт окончательную трактовку.

Его задача:
    найти сходящиеся линии карты,
    объединить действительно связанные паттерны,
    определить силу и подтверждённость темы.

Основной принцип:

    Одна тема должна подтверждаться несколькими
    независимыми признаками.

Версия 1.1:
    - исправлено объединение семян;
    - ограничено склеивание по одной планете;
    - Relations прикрепляются строго;
    - сила темы меньше зависит от количества Relations;
    - различаются tension/support диспозиторные темы;
    - исправлен выбор theme_key;
    - исключено чрезмерное объединение всей карты.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum / Astrodum Engine
"""

from dataclasses import dataclass, field
from typing import Any


# ==========================================================
# КОНСТАНТЫ
# ==========================================================

MIN_THEME_STRENGTH = 30.0
MIN_INDEPENDENT_EVIDENCE = 2

PATTERN_WEIGHTS = {
    "planet_focus": 1.00,
    "planet_cluster": 1.15,
    "multiple_rulership": 1.05,
    "dispositor_chain": 1.10,
    "tension": 1.20,
    "support": 1.00,
    "dignity_reinforcement": 0.85,
    "angular_concentration": 1.15,
}


# ==========================================================
# СТРУКТУРНЫЕ ГРУППЫ ДОМОВ
# ==========================================================

HOUSE_GROUPS = {
    "identity": {1},
    "resources": {2},
    "communication": {3},
    "home": {4},
    "creativity": {5},
    "work_health": {6},
    "partnership": {7},
    "shared_resources": {8},
    "meaning": {9},
    "career": {10},
    "community": {11},
    "retreat": {12},
}


# ==========================================================
# THEME CANDIDATE
# ==========================================================

@dataclass
class ThemeCandidate:
    """
    Структурированный кандидат на смысловую тему.
    """

    theme_key: str
    strength: float
    coherence: float
    evidence_count: int

    pattern_types: tuple[str, ...] = ()
    planets: tuple[str, ...] = ()
    houses: tuple[int, ...] = ()

    tensions: tuple[dict, ...] = ()
    supports: tuple[dict, ...] = ()

    evidence: tuple[dict, ...] = ()

    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "theme_key": self.theme_key,
            "strength": self.strength,
            "coherence": self.coherence,
            "evidence_count": self.evidence_count,
            "pattern_types": list(self.pattern_types),
            "planets": list(self.planets),
            "houses": list(self.houses),
            "tensions": list(self.tensions),
            "supports": list(self.supports),
            "evidence": list(self.evidence),
            "data": dict(self.data),
        }

    def __repr__(self) -> str:
        return (
            f"<ThemeCandidate "
            f"{self.theme_key} "
            f"strength={self.strength} "
            f"evidence={self.evidence_count}>"
        )


# ==========================================================
# THEME REPORT
# ==========================================================

class ThemeReport:
    """
    Коллекция смысловых кандидатов.
    """

    def __init__(
        self,
        themes: list[ThemeCandidate] | None = None,
    ):
        self._themes = list(themes) if themes else []

        self._themes.sort(
            key=lambda theme: (
                theme.strength,
                theme.coherence,
                theme.evidence_count,
            ),
            reverse=True,
        )

    def all(self) -> list[ThemeCandidate]:
        return list(self._themes)

    def to_list(self) -> list[dict]:
        return [theme.to_dict() for theme in self._themes]

    def __len__(self) -> int:
        return len(self._themes)

    def __iter__(self):
        return iter(self._themes)

    def __getitem__(self, index):
        return self._themes[index]

    def top(self, n: int = 10) -> list[ThemeCandidate]:
        return self._themes[:n]

    def by_key(self, theme_key: str) -> list[ThemeCandidate]:
        return [
            theme
            for theme in self._themes
            if theme.theme_key == theme_key
        ]

    def with_house(self, house: int) -> list[ThemeCandidate]:
        return [
            theme
            for theme in self._themes
            if house in theme.houses
        ]

    def with_planet(self, planet: str) -> list[ThemeCandidate]:
        return [
            theme
            for theme in self._themes
            if planet in theme.planets
        ]

    @property
    def strongest(self) -> ThemeCandidate | None:
        return self._themes[0] if self._themes else None

    def __repr__(self) -> str:
        return f"<ThemeReport themes={len(self._themes)}>"


# ==========================================================
# ВСПОМОГАТЕЛЬНЫЕ
# ==========================================================

def _as_list(collection) -> list:
    if collection is None:
        return []

    if hasattr(collection, "all"):
        return collection.all()

    return list(collection)


def _pattern_type(pattern) -> str:
    return getattr(pattern, "type", "")


def _pattern_strength(pattern) -> float:
    try:
        return float(getattr(pattern, "strength", 0.0))
    except (TypeError, ValueError):
        return 0.0


def _pattern_data(pattern) -> dict:
    data = getattr(pattern, "data", {})
    return dict(data) if isinstance(data, dict) else {}


def _pattern_evidence(pattern) -> list:
    evidence = getattr(pattern, "evidence", ())
    return list(evidence) if evidence else []


def _relation_data(relation) -> dict:
    data = getattr(relation, "data", {})
    return dict(data) if isinstance(data, dict) else {}


def _relation_type(relation) -> str:
    return getattr(relation, "type", "")


def _relation_source(relation) -> str:
    return getattr(relation, "source", "")


def _relation_target(relation) -> str:
    return getattr(relation, "target", "")


def _extract_planets_from_pattern(pattern) -> set[str]:
    data = _pattern_data(pattern)
    result = set()

    for key in (
        "planet",
        "planet1",
        "planet2",
        "final_dispositor",
    ):
        value = data.get(key)

        if isinstance(value, str) and value:
            result.add(value)

    planets = data.get("planets", [])

    if isinstance(planets, (list, tuple, set)):
        for planet in planets:
            if isinstance(planet, str) and planet:
                result.add(planet)

    chain = data.get("chain", [])

    if isinstance(chain, (list, tuple)):
        for planet in chain:
            if isinstance(planet, str) and planet:
                result.add(planet)

    return result


def _extract_houses_from_pattern(pattern) -> set[int]:
    data = _pattern_data(pattern)
    result = set()

    house = data.get("house")

    if isinstance(house, int):
        result.add(house)

    houses = data.get("houses", [])

    if isinstance(houses, (list, tuple, set)):
        for value in houses:
            if isinstance(value, int):
                result.add(value)

    return result


def _extract_planets_from_relation(relation) -> set[str]:
    result = set()

    source = _relation_source(relation)
    target = _relation_target(relation)

    if source:
        result.add(source)

    if target:
        result.add(target)

    data = _relation_data(relation)

    for key in (
        "planet",
        "planet1",
        "planet2",
        "ruler",
        "dispositor",
    ):
        value = data.get(key)

        if isinstance(value, str) and value:
            result.add(value)

    return result


def _extract_houses_from_relation(relation) -> set[int]:
    result = set()

    data = _relation_data(relation)

    house = data.get("house")

    if isinstance(house, int):
        result.add(house)

    target = _relation_target(relation)

    if isinstance(target, str) and target.startswith("House_"):
        try:
            result.add(
                int(target.split("_", 1)[1])
            )
        except (ValueError, IndexError):
            pass

    return result


def _house_group(house: int) -> str | None:
    for group, houses in HOUSE_GROUPS.items():
        if house in houses:
            return group

    return None


def _unique_preserve(values) -> tuple:
    result = []

    for value in values:
        if value not in result:
            result.append(value)

    return tuple(result)


def _pattern_weight(pattern_type: str) -> float:
    return PATTERN_WEIGHTS.get(pattern_type, 0.75)


# ==========================================================
# СЕМЕНА ТЕМ
# ==========================================================

def _build_theme_seeds(
    patterns,
    relations=None,
) -> list[dict]:
    """
    Создаёт структурные семена тем.
    """

    seeds = []

    # ------------------------------------------------------
    # 1. КЛАСТЕРЫ ДОМОВ
    # ------------------------------------------------------

    for pattern in patterns:

        if _pattern_type(pattern) != "planet_cluster":
            continue

        data = _pattern_data(pattern)

        house = data.get("house")

        if not isinstance(house, int):
            continue

        seeds.append(
            {
                "key": f"house_{house}",
                "origin": "house_cluster",
                "patterns": [pattern],
                "planets": _extract_planets_from_pattern(pattern),
                "houses": {house},
            }
        )

    # ------------------------------------------------------
    # 2. МНОЖЕСТВЕННОЕ УПРАВЛЕНИЕ
    # ------------------------------------------------------

    for pattern in patterns:

        if _pattern_type(pattern) != "multiple_rulership":
            continue

        data = _pattern_data(pattern)

        planet = data.get("planet")
        houses = data.get("houses", [])

        valid_houses = {
            house
            for house in houses
            if isinstance(house, int)
        }

        if not planet or not valid_houses:
            continue

        seeds.append(
            {
                "key": f"rulership_{planet}",
                "origin": "multiple_rulership",
                "patterns": [pattern],
                "planets": {planet},
                "houses": valid_houses,
            }
        )

    # ------------------------------------------------------
    # 3. ДИСПОЗИТОРНЫЕ ЦЕПОЧКИ
    # ------------------------------------------------------

    for pattern in patterns:

        if _pattern_type(pattern) != "dispositor_chain":
            continue

        data = _pattern_data(pattern)

        chain = data.get("chain", [])
        final_dispositor = data.get("final_dispositor")

        planets = {
            planet
            for planet in chain
            if isinstance(planet, str)
        }

        if isinstance(final_dispositor, str):
            planets.add(final_dispositor)

        if not planets:
            continue

        seeds.append(
            {
                "key": f"dispositor_{final_dispositor}",
                "origin": "dispositor_chain",
                "patterns": [pattern],
                "planets": planets,
                "houses": set(),
            }
        )

    # ------------------------------------------------------
    # 4. НАПРЯЖЕНИЯ
    # ------------------------------------------------------

    for pattern in patterns:

        if _pattern_type(pattern) != "tension":
            continue

        data = _pattern_data(pattern)

        planets = {
            data.get("planet1"),
            data.get("planet2"),
        }

        planets.discard(None)

        if len(planets) < 2:
            continue

        seeds.append(
            {
                "key": (
                    "tension_"
                    + "_".join(sorted(planets))
                ),
                "origin": "tension",
                "patterns": [pattern],
                "planets": planets,
                "houses": set(),
            }
        )

    # ------------------------------------------------------
    # 5. ПОДДЕРЖКА
    # ------------------------------------------------------

    for pattern in patterns:

        if _pattern_type(pattern) != "support":
            continue

        data = _pattern_data(pattern)

        planets = {
            data.get("planet1"),
            data.get("planet2"),
        }

        planets.discard(None)

        if len(planets) < 2:
            continue

        seeds.append(
            {
                "key": (
                    "support_"
                    + "_".join(sorted(planets))
                ),
                "origin": "support",
                "patterns": [pattern],
                "planets": planets,
                "houses": set(),
            }
        )

    # ------------------------------------------------------
    # 6. ФОКУС ПЛАНЕТЫ
    # ------------------------------------------------------

    for pattern in patterns:

        if _pattern_type(pattern) != "planet_focus":
            continue

        data = _pattern_data(pattern)
        planet = data.get("planet")

        if not planet:
            continue

        seeds.append(
            {
                "key": f"planet_{planet}",
                "origin": "planet_focus",
                "patterns": [pattern],
                "planets": {planet},
                "houses": set(),
            }
        )

    # ------------------------------------------------------
    # 7. ДОСТОИНСТВА
    # ------------------------------------------------------

    for pattern in patterns:

        if _pattern_type(pattern) != "dignity_reinforcement":
            continue

        data = _pattern_data(pattern)
        planet = data.get("planet")

        if not planet:
            continue

        seeds.append(
            {
                "key": f"planet_{planet}",
                "origin": "dignity",
                "patterns": [pattern],
                "planets": {planet},
                "houses": set(),
            }
        )

    # ------------------------------------------------------
    # 8. УГЛОВАЯ КОНЦЕНТРАЦИЯ
    # ------------------------------------------------------

    for pattern in patterns:

        if _pattern_type(pattern) != "angular_concentration":
            continue

        data = _pattern_data(pattern)

        planets = {
            planet
            for planet in data.get("planets", [])
            if isinstance(planet, str)
        }

        houses = {
            house
            for house in data.get("houses", [])
            if isinstance(house, int)
        }

        if not planets:
            continue

        seeds.append(
            {
                "key": "angular_emphasis",
                "origin": "angular_concentration",
                "patterns": [pattern],
                "planets": planets,
                "houses": houses,
            }
        )

    return seeds


# ==========================================================
# ОБЪЕДИНЕНИЕ СЕМЯН
# ==========================================================

def _merge_seeds(seeds: list[dict]) -> list[dict]:
    """
    Объединяет семена только при сильном структурном
    пересечении.

    Одной общей планеты недостаточно.
    """

    groups = []

    for seed in seeds:

        best_group = None
        best_score = 0.0

        for group in groups:

            shared_planets = (
                set(seed["planets"])
                .intersection(group["planets"])
            )

            shared_houses = (
                set(seed["houses"])
                .intersection(group["houses"])
            )

            score = 0.0

            # Общая планета + общий дом.
            if shared_planets and shared_houses:
                score += 5.0

            # Только общий дом.
            elif shared_houses:
                score += 3.5

            # Две или более общих планеты.
            elif len(shared_planets) >= 2:
                score += 2.5

            # Особое усиление для двух диспозиторных цепей,
            # если они действительно пересекаются.
            if seed["origin"] == "dispositor_chain":

                if shared_planets:

                    for existing_seed in group["seeds"]:

                        if existing_seed["origin"] == "dispositor_chain":
                            score += 1.0
                            break

            # Поддержка / напряжение должны иметь
            # реальное планетарное пересечение.
            if seed["origin"] in {
                "tension",
                "support",
            }:

                if shared_planets:
                    score += 1.5

            if score > best_score:
                best_score = score
                best_group = group

        # --------------------------------------------------
        # ОБЪЕДИНЕНИЕ
        # --------------------------------------------------

        if (
            best_group is not None
            and best_score >= 3.0
        ):

            best_group["seeds"].append(seed)

            best_group["patterns"].extend(
                seed["patterns"]
            )

            best_group["planets"].update(
                seed["planets"]
            )

            best_group["houses"].update(
                seed["houses"]
            )

            best_group["origins"].add(
                seed["origin"]
            )

        else:

            groups.append(
                {
                    "seeds": [seed],
                    "patterns": list(seed["patterns"]),
                    "planets": set(seed["planets"]),
                    "houses": set(seed["houses"]),
                    "origins": {seed["origin"]},
                }
            )

    return groups


# ==========================================================
# СВЯЗЫВАНИЕ С RELATIONS
# ==========================================================

def _attach_relations(
    groups,
    relations,
) -> None:
    """
    Добавляет только те Relations, которые действительно
    относятся к структурному ядру темы.

    Простого совпадения одной планеты недостаточно.

    Исключение:
        planet_dignity может быть прикреплён к теме,
        если сама планета входит в её ядро.
    """

    relation_list = _as_list(relations)

    for group in groups:

        group["relations"] = []

        theme_planets = set(group["planets"])
        theme_houses = set(group["houses"])

        for relation in relation_list:

            relation_type = _relation_type(relation)

            relation_planets = (
                _extract_planets_from_relation(
                    relation
                )
            )

            relation_houses = (
                _extract_houses_from_relation(
                    relation
                )
            )

            shared_planets = (
                theme_planets
                .intersection(relation_planets)
            )

            shared_houses = (
                theme_houses
                .intersection(relation_houses)
            )

            # ------------------------------------------------
            # АСПЕКТЫ
            # ------------------------------------------------

            if relation_type == "planet_aspect":

                if len(shared_planets) >= 2:
                    group["relations"].append(relation)

                continue

            # ------------------------------------------------
            # ДИСПОЗИТОРЫ
            # ------------------------------------------------

            if relation_type == "dispositor":

                if len(shared_planets) >= 2:
                    group["relations"].append(relation)

                continue

            # ------------------------------------------------
            # УПРАВЛЕНИЕ ДОМАМИ
            # ------------------------------------------------

            if relation_type == "house_rulership":

                if (
                    shared_planets
                    and shared_houses
                ):
                    group["relations"].append(relation)

                continue

            # ------------------------------------------------
            # ДОСТОИНСТВА
            # ------------------------------------------------

            if relation_type == "planet_dignity":

                if shared_planets:
                    group["relations"].append(relation)

                continue

            # ------------------------------------------------
            # ПРОЧИЕ ОТНОШЕНИЯ
            # ------------------------------------------------

            if (
                shared_planets
                and shared_houses
            ):
                group["relations"].append(relation)


# ==========================================================
# РАСЧЁТ СИЛЫ ТЕМЫ
# ==========================================================

def _calculate_strength(group) -> float:
    """
    Рассчитывает силу темы.

    Основной вес дают паттерны.
    Relations дают только небольшой бонус.
    """

    patterns = group["patterns"]

    if not patterns:
        return 0.0

    weighted_strength = 0.0
    total_weight = 0.0

    for pattern in patterns:

        pattern_type = _pattern_type(pattern)
        strength = _pattern_strength(pattern)

        weight = _pattern_weight(pattern_type)

        weighted_strength += (
            strength * weight
        )

        total_weight += weight

    if total_weight == 0:
        return 0.0

    base = (
        weighted_strength
        / total_weight
    )

    # Разнообразие независимых структур.
    type_count = len(group["origins"])

    diversity_bonus = min(
        12.0,
        max(0, type_count - 1) * 3.0,
    )

    # Relations не должны доминировать над паттернами.
    relation_count = len(
        group.get("relations", [])
    )

    relation_bonus = min(
        5.0,
        relation_count * 0.5,
    )

    # Небольшой бонус за размер планетарного ядра.
    planet_bonus = min(
        6.0,
        max(
            0,
            len(group["planets"]) - 1
        ) * 1.5,
    )

    strength = (
        base
        + diversity_bonus
        + relation_bonus
        + planet_bonus
    )

    return round(
        min(100.0, strength),
        2,
    )


# ==========================================================
# COHERENCE
# ==========================================================

def _calculate_coherence(group) -> float:
    """
    Оценивает внутреннюю связность темы.
    """

    origin_count = len(
        group["origins"]
    )

    relation_count = len(
        group.get("relations", [])
    )

    planet_count = len(
        group["planets"]
    )

    score = 20.0

    score += min(
        35.0,
        origin_count * 10.0,
    )

    score += min(
        25.0,
        relation_count * 2.5,
    )

    score += min(
        20.0,
        max(
            0,
            planet_count - 1
        ) * 5.0,
    )

    return round(
        min(100.0, score),
        2,
    )


# ==========================================================
# ДОКАЗАТЕЛЬСТВА
# ==========================================================

def _build_evidence(group) -> list[dict]:
    """
    Формирует список независимых структурных доказательств.
    """

    result = []
    seen = set()

    for pattern in group["patterns"]:

        pattern_type = _pattern_type(pattern)
        data = _pattern_data(pattern)

        key = (
            pattern_type,
            repr(
                sorted(
                    data.items(),
                    key=str,
                )
            ),
        )

        if key in seen:
            continue

        seen.add(key)

        result.append(
            {
                "kind": "pattern",
                "type": pattern_type,
                "strength": _pattern_strength(pattern),
                "data": data,
                "evidence": _pattern_evidence(pattern),
            }
        )

    return result


# ==========================================================
# THEME KEY
# ==========================================================

def _derive_theme_key(group) -> str:
    """
    Определяет структурный ключ темы.

    Это НЕ литературная интерпретация.
    """

    origins = group["origins"]
    houses = group["houses"]
    planets = group["planets"]

    # ------------------------------------------------------
    # 1. ДОМИНИРУЮЩИЙ ДОМ
    # ------------------------------------------------------

    if houses:

        house_counts = {}

        for seed in group["seeds"]:

            for house in seed["houses"]:

                house_counts[house] = (
                    house_counts.get(house, 0) + 1
                )

        if house_counts:

            ordered = sorted(
                house_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )

            main_house, main_count = ordered[0]

            second_count = (
                ordered[1][1]
                if len(ordered) > 1
                else 0
            )

            # Дом должен явно выделяться.
            if main_count >= second_count + 2:
                return f"house_{main_house}_focus"

    # ------------------------------------------------------
    # 2. ДИСПОЗИТОРНЫЙ ЦЕНТР
    # ------------------------------------------------------

    if "dispositor_chain" in origins:

        final_dispositors = []

        for seed in group["seeds"]:

            for pattern in seed["patterns"]:

                data = _pattern_data(pattern)

                final = data.get(
                    "final_dispositor"
                )

                if final:
                    final_dispositors.append(
                        final
                    )

        if final_dispositors:

            final = max(
                set(final_dispositors),
                key=final_dispositors.count,
            )

            if "tension" in origins:
                return (
                    f"dispositor_{final}_tension"
                )

            if "support" in origins:
                return (
                    f"dispositor_{final}_support"
                )

            return (
                f"dispositor_{final}_focus"
            )

    # ------------------------------------------------------
    # 3. НАПРЯЖЕНИЕ
    # ------------------------------------------------------

    if "tension" in origins:
        return "conflict_cluster"

    # ------------------------------------------------------
    # 4. ПОДДЕРЖКА
    # ------------------------------------------------------

    if "support" in origins:
        return "support_cluster"

    # ------------------------------------------------------
    # 5. УГЛОВАЯ КОНЦЕНТРАЦИЯ
    # ------------------------------------------------------

    if "angular_concentration" in origins:
        return "angular_focus"

    # ------------------------------------------------------
    # 6. ПЛАНЕТАРНЫЙ КЛАСТЕР
    # ------------------------------------------------------

    if planets:
        return "planetary_cluster"

    return "unclassified_theme"


# ==========================================================
# СБОРКА CANDIDATE
# ==========================================================

def _build_theme_candidate(
    group,
) -> ThemeCandidate:

    strength = _calculate_strength(group)

    coherence = _calculate_coherence(group)

    evidence = _build_evidence(group)

    theme_key = _derive_theme_key(group)

    pattern_types = _unique_preserve(
        _pattern_type(pattern)
        for pattern in group["patterns"]
    )

    planets = tuple(
        sorted(group["planets"])
    )

    houses = tuple(
        sorted(group["houses"])
    )

    tensions = []
    supports = []

    for pattern in group["patterns"]:

        pattern_type = _pattern_type(pattern)
        data = _pattern_data(pattern)

        if pattern_type == "tension":
            tensions.append(data)

        elif pattern_type == "support":
            supports.append(data)

    return ThemeCandidate(
        theme_key=theme_key,
        strength=strength,
        coherence=coherence,
        evidence_count=len(evidence),
        pattern_types=tuple(pattern_types),
        planets=planets,
        houses=houses,
        tensions=tuple(tensions),
        supports=tuple(supports),
        evidence=tuple(evidence),
        data={
            "origins": sorted(group["origins"]),
            "relation_count": len(
                group.get("relations", [])
            ),
            "planet_count": len(planets),
            "house_count": len(houses),
        },
    )
def _attach_chart_houses(
    groups,
    chart,
) -> None:
    """
    Добавляет в группы тем реальные дома планет
    из Chart.

    Theme Engine не интерпретирует дома.
    Он только переносит объективные данные Chart.
    """

    if chart is None:
        return

    try:
        chart_planets = chart.planets
    except AttributeError:
        return

    for group in groups:

        for planet in group["planets"]:

            data = chart_planets.get(
                planet,
                {},
            )

            house = data.get("house")

            if isinstance(house, int):
                group["houses"].add(house)


# ==========================================================
# BUILD THEMES
# ==========================================================

def build_themes(
    patterns,
    relations=None,
    priorities=None,
    chart=None,
) -> ThemeReport:
    """
    Строит ThemeReport.
    """

    pattern_list = _as_list(patterns)
    relation_list = _as_list(relations)

    if not pattern_list:
        return ThemeReport()

    # ------------------------------------------------------
    # 1. СЕМЕНА
    # ------------------------------------------------------

    seeds = _build_theme_seeds(
        pattern_list,
        relation_list,
    )

    if not seeds:
        return ThemeReport()

    # ------------------------------------------------------
    # 2. ОБЪЕДИНЕНИЕ
    # ------------------------------------------------------

    groups = _merge_seeds(
         seeds
    )

    _attach_chart_houses(
         groups,
         chart,
    )

    _attach_relations(
        groups,
        relation_list,
    )
    # ------------------------------------------------------
    # 4. КАНДИДАТЫ
    # ------------------------------------------------------

    themes = []

    for group in groups:

        candidate = _build_theme_candidate(group)

        if (
            candidate.strength < MIN_THEME_STRENGTH
            or candidate.evidence_count
            < MIN_INDEPENDENT_EVIDENCE
        ):
            continue

        themes.append(candidate)

    # ------------------------------------------------------
    # 5. СОРТИРОВКА
    # ------------------------------------------------------

    themes.sort(
        key=lambda theme: (
            theme.strength,
            theme.coherence,
            theme.evidence_count,
        ),
        reverse=True,
    )

    # ------------------------------------------------------
    # 6. УДАЛЕНИЕ ДУБЛИКАТОВ
    # ------------------------------------------------------

    selected = []
    covered_signatures = []

    for theme in themes:

        signature = (
            frozenset(theme.planets),
            frozenset(theme.houses),
        )

        duplicate = False

        for existing_signature in covered_signatures:

            shared_planets = len(
                signature[0].intersection(
                    existing_signature[0]
                )
            )

            shared_houses = len(
                signature[1].intersection(
                    existing_signature[1]
                )
            )

            current_planets = max(
                1,
                len(signature[0]),
            )

            current_houses = max(
                1,
                len(signature[1]),
            )

            overlap = max(
                shared_planets / current_planets,
                shared_houses / current_houses,
            )

            if overlap >= 0.85:
                duplicate = True
                break

        if duplicate:
            continue

        selected.append(theme)
        covered_signatures.append(signature)

    return ThemeReport(selected)


# ==========================================================
# УДОБНЫЕ ФУНКЦИИ
# ==========================================================

def strongest_themes(
    report: ThemeReport,
    n: int = 5,
) -> list[ThemeCandidate]:
    return report.top(n)


def themes_for_planet(
    report: ThemeReport,
    planet: str,
) -> list[ThemeCandidate]:
    return report.with_planet(planet)


def themes_for_house(
    report: ThemeReport,
    house: int,
) -> list[ThemeCandidate]:
    return report.with_house(house)