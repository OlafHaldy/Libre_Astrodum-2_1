"""
Liber Astrodum

core/patterns.py

Pattern Engine v1.0.

Преобразует Relations в устойчивые астрологические конструкции.

Поток:

    Facts
      ↓
    Priorities
      ↓
    Relations
      ↓
    Patterns

Pattern Engine НЕ генерирует текст.
Pattern Engine НЕ делает окончательную интерпретацию.

Его задача:
    обнаружить повторяющиеся структуры,
    объединить связанные отношения
    и оценить силу паттерна.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum / Astrodum Engine

Версия:
    1.0
"""

from dataclasses import dataclass, field
from typing import Any


# ==========================================================
# КОНСТАНТЫ
# ==========================================================

IMPORTANT_PLANET_MIN = 30
STRONG_PATTERN_MIN = 45

ANGULAR_HOUSES = {1, 4, 7, 10}

MAJOR_TENSION_ASPECTS = {
    "square",
    "opposition",
}

MAJOR_SUPPORT_ASPECTS = {
    "trine",
    "sextile",
}

MAJOR_ASPECTS = {
    "conjunction",
    "square",
    "opposition",
    "trine",
    "sextile",
}

PATTERN_PRIORITY = {
    "planet_cluster": 70,
    "angular_concentration": 65,
    "tension": 60,
    "support": 50,
    "dispositor_chain": 55,
    "multiple_rulership": 50,
    "planet_focus": 45,
    "house_recurrence": 45,
    "dignity_reinforcement": 40,
}


# ==========================================================
# PATTERN
# ==========================================================

@dataclass(frozen=True)
class Pattern:
    """
    Один распознанный структурный паттерн.

    type:
        Машинный тип паттерна.

    theme_hint:
        Предварительная смысловая подсказка для следующего слоя.
        Это НЕ окончательная интерпретация.

    strength:
        Сила паттерна.

    evidence:
        ID отношений/фактов, на которых он основан.

    data:
        Дополнительные данные.
    """

    type: str
    theme_hint: str
    strength: float
    evidence: tuple[str, ...] = ()
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "theme_hint": self.theme_hint,
            "strength": self.strength,
            "evidence": list(self.evidence),
            "data": dict(self.data),
        }

    def __repr__(self) -> str:
        return (
            f"<Pattern {self.type} "
            f"hint={self.theme_hint!r} "
            f"strength={self.strength}>"
        )


# ==========================================================
# REPORT
# ==========================================================

class PatternReport:
    """
    Коллекция распознанных паттернов.
    """

    def __init__(self, patterns: list[Pattern] | None = None):
        self._patterns = list(patterns) if patterns else []
        self._patterns.sort(
            key=lambda p: p.strength,
            reverse=True,
        )

    def all(self) -> list[Pattern]:
        return list(self._patterns)

    def to_list(self) -> list[dict]:
        return [p.to_dict() for p in self._patterns]

    def __len__(self) -> int:
        return len(self._patterns)

    def __iter__(self):
        return iter(self._patterns)

    def __getitem__(self, index):
        return self._patterns[index]

    def top(self, n: int = 10) -> list[Pattern]:
        return self._patterns[:n]

    def by_type(self, pattern_type: str) -> list[Pattern]:
        return [
            p
            for p in self._patterns
            if p.type == pattern_type
        ]

    def by_theme_hint(self, theme_hint: str) -> list[Pattern]:
        return [
            p
            for p in self._patterns
            if p.theme_hint == theme_hint
        ]

    @property
    def tensions(self) -> list[Pattern]:
        return self.by_type("tension")

    @property
    def supports(self) -> list[Pattern]:
        return self.by_type("support")

    @property
    def house_clusters(self) -> list[Pattern]:
        return self.by_type("planet_cluster")

    @property
    def angular_patterns(self) -> list[Pattern]:
        return self.by_type("angular_concentration")

    @property
    def dispositor_patterns(self) -> list[Pattern]:
        return self.by_type("dispositor_chain")

    def __repr__(self) -> str:
        return f"<PatternReport patterns={len(self._patterns)}>"


# ==========================================================
# ВСПОМОГАТЕЛЬНЫЕ
# ==========================================================

def _as_list(collection) -> list:
    if collection is None:
        return []

    if hasattr(collection, "all"):
        return collection.all()

    return list(collection)


def _relation_evidence(relation) -> str:
    evidence = getattr(relation, "evidence", ())
    if evidence:
        return ",".join(evidence)

    return (
        f"{getattr(relation, 'type', '')}:"
        f"{getattr(relation, 'source', '')}:"
        f"{getattr(relation, 'target', '')}"
    )


def _relation_data(relation) -> dict:
    data = getattr(relation, "data", {})
    return dict(data) if isinstance(data, dict) else {}


def _relation_strength(relation) -> float:
    return float(getattr(relation, "importance", 0))


def _unique_evidence(relations) -> tuple[str, ...]:
    result = []

    for relation in relations:
        evidence = getattr(relation, "evidence", ())
        for item in evidence:
            if item and item not in result:
                result.append(item)

    return tuple(result)


def _safe_strength(values: list[float], bonus: float = 0.0) -> float:
    """
    Сводит несколько весов в одно значение.

    Берём максимальный вес и добавляем умеренный бонус
    за дополнительные подтверждения.
    """
    if not values:
        return 0.0

    maximum = max(values)

    additional = max(0, len(values) - 1)

    result = maximum + min(20.0, additional * 5.0) + bonus

    return round(min(100.0, result), 2)


def _get_planet_house(relations):
    result = {}

    for relation in relations:
        if getattr(relation, "type", None) != "planet_house":
            continue

        planet = getattr(relation, "source", "")
        target = getattr(relation, "target", "")

        data = _relation_data(relation)

        house = data.get("house")

        if house is None and target.startswith("House_"):
            try:
                house = int(target.split("_", 1)[1])
            except (ValueError, IndexError):
                house = None

        if planet and house is not None:
            result[planet] = house

    return result


# ==========================================================
# ОСНОВНОЙ BUILDER
# ==========================================================

def build_patterns(
    relations,
    priorities=None,
) -> PatternReport:
    """
    Строит PatternReport из RelationReport.

    Parameters
    ----------
    relations:
        RelationReport или список Relation.

    priorities:
        Необязательный PriorityCollection.
        Используется для оценки важности объектов.

    Returns
    -------
    PatternReport
    """

    relation_list = _as_list(relations)
    priority_list = _as_list(priorities)

    patterns = []

    priority_by_object = {}

    for fact in priority_list:
        obj = fact.get("object", "")

        if not obj:
            continue

        current = priority_by_object.get(obj, 0)
        importance = float(fact.get("importance", 0))

        if importance > current:
            priority_by_object[obj] = importance

    patterns.extend(
        _find_planet_clusters(
            relation_list,
            priority_by_object,
        )
    )

    patterns.extend(
        _find_angular_concentration(
            relation_list,
            priority_by_object,
        )
    )

    patterns.extend(
        _find_tensions(
            relation_list,
            priority_by_object,
        )
    )

    patterns.extend(
        _find_supports(
            relation_list,
            priority_by_object,
        )
    )

    patterns.extend(
        _find_dispositor_chains(
            relation_list,
            priority_by_object,
        )
    )

    patterns.extend(
        _find_multiple_rulerships(
            relation_list,
        )
    )

    patterns.extend(
        _find_planet_focus(
            relation_list,
            priority_by_object,
        )
    )

    patterns.extend(
        _find_dignity_reinforcement(
            relation_list,
            priority_by_object,
        )
    )

    # Удаляем дубликаты.
    unique = {}

    for pattern in patterns:
        key = (
            pattern.type,
            pattern.theme_hint,
            tuple(sorted(pattern.evidence)),
            repr(sorted(pattern.data.items(), key=str)),
        )

        existing = unique.get(key)

        if existing is None or pattern.strength > existing.strength:
            unique[key] = pattern

    patterns = list(unique.values())

    patterns.sort(
        key=lambda p: p.strength,
        reverse=True,
    )

    return PatternReport(patterns)


# ==========================================================
# 1. КЛАСТЕР ПЛАНЕТ В ОДНОМ ДОМЕ
# ==========================================================

def _find_planet_clusters(
    relations,
    priority_by_object,
) -> list[Pattern]:

    house_to_planets = {}

    house_relations = {}

    for relation in relations:
        if getattr(relation, "type", None) != "planet_house":
            continue

        data = _relation_data(relation)

        planet = data.get(
            "planet",
            getattr(relation, "source", ""),
        )

        house = data.get("house")

        if house is None:
            continue

        house_to_planets.setdefault(house, []).append(planet)
        house_relations.setdefault(house, []).append(relation)

    patterns = []

    for house, planets in house_to_planets.items():

        unique_planets = list(dict.fromkeys(planets))

        if len(unique_planets) < 2:
            continue

        related = house_relations[house]

        strengths = [
            _relation_strength(r)
            for r in related
        ]

        importance_bonus = sum(
            priority_by_object.get(planet, 0)
            for planet in unique_planets
        ) / max(1, len(unique_planets))

        strength = _safe_strength(
            strengths,
            bonus=min(20.0, importance_bonus * 0.15),
        )

        patterns.append(
            Pattern(
                type="planet_cluster",
                theme_hint="house_concentration",
                strength=strength,
                evidence=_unique_evidence(related),
                data={
                    "house": house,
                    "planets": unique_planets,
                    "count": len(unique_planets),
                },
            )
        )

    return patterns


# ==========================================================
# 2. СКОНЦЕНТРИРОВАННОСТЬ В УГЛОВЫХ ДОМАХ
# ==========================================================

def _find_angular_concentration(
    relations,
    priority_by_object,
) -> list[Pattern]:

    planet_houses = _get_planet_house(relations)

    angular_planets = {
        planet: house
        for planet, house in planet_houses.items()
        if house in ANGULAR_HOUSES
    }

    if not angular_planets:
        return []

    angular_relations = []

    for relation in relations:

        if getattr(relation, "type", None) != "planet_house":
            continue

        planet = getattr(relation, "source", "")

        if planet in angular_planets:
            angular_relations.append(relation)

    if not angular_relations:
        return []

    importance_values = [
        _relation_strength(r)
        for r in angular_relations
    ]

    mean_priority = (
        sum(
            priority_by_object.get(planet, 0)
            for planet in angular_planets
        )
        / len(angular_planets)
    )

    strength = _safe_strength(
        importance_values,
        bonus=min(20.0, mean_priority * 0.20),
    )

    return [
        Pattern(
            type="angular_concentration",
            theme_hint="public_or_structural_emphasis",
            strength=strength,
            evidence=_unique_evidence(angular_relations),
            data={
                "planets": list(angular_planets.keys()),
                "houses": list(angular_planets.values()),
                "count": len(angular_planets),
            },
        )
    ]


# ==========================================================
# 3. НАПРЯЖЁННЫЕ АСПЕКТЫ
# ==========================================================

def _find_tensions(
    relations,
    priority_by_object,
) -> list[Pattern]:

    patterns = []

    for relation in relations:

        if getattr(relation, "type", None) != "planet_aspect":
            continue

        data = _relation_data(relation)

        aspect = data.get(
            "aspect",
            data.get("type", ""),
        )

        if aspect not in MAJOR_TENSION_ASPECTS:
            continue

        p1 = getattr(relation, "source", "")
        p2 = getattr(relation, "target", "")

        p1_priority = priority_by_object.get(p1, 0)
        p2_priority = priority_by_object.get(p2, 0)

        structural_strength = _relation_strength(relation)

        if p1_priority >= IMPORTANT_PLANET_MIN:
            structural_strength += 5

        if p2_priority >= IMPORTANT_PLANET_MIN:
            structural_strength += 5

        strength = min(
            100.0,
            round(structural_strength, 2),
        )

        patterns.append(
            Pattern(
                type="tension",
                theme_hint="planetary_conflict",
                strength=strength,
                evidence=_unique_evidence([relation]),
                data={
                    "planet1": p1,
                    "planet2": p2,
                    "aspect": aspect,
                    "priority1": p1_priority,
                    "priority2": p2_priority,
                    "orb": data.get("orb"),
                },
            )
        )

    return patterns


# ==========================================================
# 4. ПОДДЕРЖИВАЮЩИЕ АСПЕКТЫ
# ==========================================================

def _find_supports(
    relations,
    priority_by_object,
) -> list[Pattern]:

    patterns = []

    for relation in relations:

        if getattr(relation, "type", None) != "planet_aspect":
            continue

        data = _relation_data(relation)

        aspect = data.get(
            "aspect",
            data.get("type", ""),
        )

        if aspect not in MAJOR_SUPPORT_ASPECTS:
            continue

        p1 = getattr(relation, "source", "")
        p2 = getattr(relation, "target", "")

        p1_priority = priority_by_object.get(p1, 0)
        p2_priority = priority_by_object.get(p2, 0)

        strength = _relation_strength(relation)

        if p1_priority >= IMPORTANT_PLANET_MIN:
            strength += 5

        if p2_priority >= IMPORTANT_PLANET_MIN:
            strength += 5

        strength = min(100.0, round(strength, 2))

        patterns.append(
            Pattern(
                type="support",
                theme_hint="planetary_cooperation",
                strength=strength,
                evidence=_unique_evidence([relation]),
                data={
                    "planet1": p1,
                    "planet2": p2,
                    "aspect": aspect,
                    "priority1": p1_priority,
                    "priority2": p2_priority,
                    "orb": data.get("orb"),
                },
            )
        )

    return patterns


# ==========================================================
# 5. ЦЕПОЧКИ ДИСПОЗИТОРОВ
# ==========================================================

def _find_dispositor_chains(
    relations,
    priority_by_object,
) -> list[Pattern]:

    graph = {}

    relation_by_pair = {}

    for relation in relations:

        if getattr(relation, "type", None) != "dispositor":
            continue

        source = getattr(relation, "source", "")
        target = getattr(relation, "target", "")

        if not source or not target:
            continue

        graph[source] = target

        relation_by_pair[(source, target)] = relation

    patterns = []

    if not graph:
        return patterns

    for start in graph:

        visited = []
        current = start

        while current in graph:

            if current in visited:
                # Обнаружена петля диспозиций.
                break

            visited.append(current)
            current = graph[current]

        if len(visited) < 2:
            continue

        final_dispositor = current

        chain_relations = []

        for index in range(len(visited) - 1):

            pair = (
                visited[index],
                visited[index + 1],
            )

            relation = relation_by_pair.get(pair)

            if relation:
                chain_relations.append(relation)

        if not chain_relations:
            continue

        priorities = [
            priority_by_object.get(planet, 0)
            for planet in visited
        ]

        base_strength = max(
            [_relation_strength(r) for r in chain_relations],
            default=0,
        )

        priority_bonus = min(
            20.0,
            max(priorities) * 0.20 if priorities else 0,
        )

        chain_bonus = min(
            15.0,
            max(0, len(visited) - 2) * 5.0,
        )

        strength = min(
            100.0,
            round(
                base_strength
                + priority_bonus
                + chain_bonus,
                2,
            ),
        )

        patterns.append(
            Pattern(
                type="dispositor_chain",
                theme_hint="dispositor_focus",
                strength=strength,
                evidence=_unique_evidence(chain_relations),
                data={
                    "chain": visited,
                    "final_dispositor": final_dispositor,
                    "length": len(visited),
                },
            )
        )

    return patterns


# ==========================================================
# 6. ПЛАНЕТА УПРАВЛЯЕТ НЕСКОЛЬКИМИ ДОМАМИ
# ==========================================================

def _find_multiple_rulerships(relations) -> list[Pattern]:

    planet_houses = {}

    related = {}

    for relation in relations:

        if getattr(relation, "type", None) != "house_rulership":
            continue

        planet = getattr(relation, "source", "")
        house = _relation_data(relation).get("house")

        if not planet or house is None:
            continue

        planet_houses.setdefault(planet, []).append(house)
        related.setdefault(planet, []).append(relation)

    patterns = []

    for planet, houses in planet_houses.items():

        unique_houses = list(dict.fromkeys(houses))

        if len(unique_houses) < 2:
            continue

        rels = related[planet]

        strength = _safe_strength(
            [_relation_strength(r) for r in rels],
            bonus=min(15.0, len(unique_houses) * 3.0),
        )

        patterns.append(
            Pattern(
                type="multiple_rulership",
                theme_hint="multi_house_connection",
                strength=strength,
                evidence=_unique_evidence(rels),
                data={
                    "planet": planet,
                    "houses": unique_houses,
                    "count": len(unique_houses),
                },
            )
        )

    return patterns


# ==========================================================
# 7. ФОКУС ПЛАНЕТЫ
# ==========================================================

def _find_planet_focus(
    relations,
    priority_by_object,
) -> list[Pattern]:

    counts = {}

    related = {}

    for relation in relations:

        source = getattr(relation, "source", "")
        target = getattr(relation, "target", "")

        for planet in (source, target):

            if not planet:
                continue

            if planet not in priority_by_object:
                continue

            counts[planet] = counts.get(planet, 0) + 1
            related.setdefault(planet, []).append(relation)

    patterns = []

    for planet, count in counts.items():

        priority = priority_by_object.get(planet, 0)

        if priority < IMPORTANT_PLANET_MIN:
            continue

        if count < 3:
            continue

        rels = related[planet]

        strength = min(
            100.0,
            round(
                priority
                + min(20.0, count * 4.0),
                2,
            ),
        )

        patterns.append(
            Pattern(
                type="planet_focus",
                theme_hint="planetary_centrality",
                strength=strength,
                evidence=_unique_evidence(rels),
                data={
                    "planet": planet,
                    "relation_count": count,
                    "priority": priority,
                },
            )
        )

    return patterns


# ==========================================================
# 8. ДОСТОИНСТВО + ВЫСОКИЙ ПРИОРИТЕТ
# ==========================================================

def _find_dignity_reinforcement(
    relations,
    priority_by_object,
) -> list[Pattern]:

    patterns = []

    for relation in relations:

        if getattr(relation, "type", None) != "planet_dignity":
            continue

        planet = getattr(relation, "source", "")
        priority = priority_by_object.get(planet, 0)

        if priority < IMPORTANT_PLANET_MIN:
            continue

        strength = _safe_strength(
            [_relation_strength(relation)],
            bonus=min(20.0, priority * 0.15),
        )

        data = _relation_data(relation)

        patterns.append(
            Pattern(
                type="dignity_reinforcement",
                theme_hint="planetary_strength",
                strength=strength,
                evidence=_unique_evidence([relation]),
                data={
                    "planet": planet,
                    "priority": priority,
                    "dignity": data.get("details", {}),
                },
            )
        )

    return patterns


# ==========================================================
# ВЫБОР СИЛЬНЕЙШИХ ПАТТЕРНОВ
# ==========================================================

def strongest_patterns(
    report: PatternReport,
    n: int = 10,
) -> list[Pattern]:
    """
    Возвращает наиболее сильные паттерны.
    """
    return report.top(n)


def patterns_for_theme(
    report: PatternReport,
    theme_hint: str,
) -> list[Pattern]:
    """
    Возвращает паттерны по theme_hint.
    """
    return report.by_theme_hint(theme_hint)