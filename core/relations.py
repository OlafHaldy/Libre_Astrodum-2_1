"""
Liber Astrodum

core/relations.py

Relations Engine v1.0.

Строит структурированный граф связей между астрологическими фактами.

Поток:
    FactCollection
        +
    PriorityCollection
        ↓
    RelationReport

Модуль НЕ генерирует текст и НЕ определяет смысловые темы.
Его задача — обнаружить и структурировать отношения:

- планета → дом;
- планета → знак;
- планета ↔ планета через аспект;
- планета → управляемый дом;
- планета → диспозитор;
- планета → эссенциальное достоинство;
- диспозитор → планета;
- связи с главными/приоритетными объектами.

Архитектурный принцип:
    После Fact Engine модуль не должен обращаться к Chart.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0 / Astrodum Engine

Версия:
    1.0
"""

from dataclasses import dataclass, field
from typing import Any


# ==========================================================
# КОНСТАНТЫ
# ==========================================================

PLANETS = {
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "True Node",
    "Chiron",
}

ASPECT_TYPES = {
    "conjunction",
    "sextile",
    "square",
    "trine",
    "opposition",
    "quincunx",
}

# Чем сильнее аспект как структурная связь,
# тем выше его базовый relation weight.
ASPECT_WEIGHTS = {
    "conjunction": 12,
    "opposition": 11,
    "square": 10,
    "trine": 8,
    "sextile": 6,
    "quincunx": 5,
}

# Минимальный importance, при котором факт участвует
# в построении усиленных связей.
IMPORTANT_FACT_MIN = 30

# Максимальное количество причин/связей,
# чтобы report не разрастался бесконтрольно.
DEFAULT_MAX_RELATIONS = 200


# ==========================================================
# ОБЪЕКТ RELATION
# ==========================================================

@dataclass(frozen=True)
class Relation:
    """
    Одна структурированная связь между элементами карты.

    type:
        Тип связи.

    source:
        Основной объект связи.

    target:
        Второй объект связи.

    data:
        Дополнительные структурированные данные.

    importance:
        Вес связи, полученный из приоритетов фактов.

    evidence:
        ID исходного факта/фактов, на основании которых
        связь была создана.
    """

    type: str
    source: str
    target: str
    data: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.0
    evidence: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "source": self.source,
            "target": self.target,
            "data": dict(self.data),
            "importance": self.importance,
            "evidence": list(self.evidence),
        }

    def __repr__(self) -> str:
        return (
            f"<Relation {self.type}: "
            f"{self.source} -> {self.target} "
            f"importance={self.importance}>"
        )


# ==========================================================
# REPORT
# ==========================================================

class RelationReport:
    """
    Отчёт Relations Engine.

    Хранит все обнаруженные отношения и предоставляет
    удобную выборку по типам и объектам.
    """

    def __init__(self, relations: list[Relation] | None = None):
        self._relations = list(relations) if relations else []
        self._sort()

    def _sort(self):
        self._relations.sort(
            key=lambda r: r.importance,
            reverse=True,
        )

    def all(self) -> list[Relation]:
        return list(self._relations)

    def to_list(self) -> list[dict]:
        return [relation.to_dict() for relation in self._relations]

    def __len__(self) -> int:
        return len(self._relations)

    def __iter__(self):
        return iter(self._relations)

    def __getitem__(self, index):
        return self._relations[index]

    def top(self, n: int = 20) -> list[Relation]:
        return self._relations[:n]

    def by_type(self, relation_type: str) -> list[Relation]:
        return [
            r for r in self._relations
            if r.type == relation_type
        ]

    def for_object(self, object_name: str) -> list[Relation]:
        return [
            r
            for r in self._relations
            if r.source == object_name or r.target == object_name
        ]

    def between(self, source: str, target: str) -> list[Relation]:
        return [
            r
            for r in self._relations
            if (
                (r.source == source and r.target == target)
                or
                (r.source == target and r.target == source)
            )
        ]

    @property
    def aspects(self) -> list[Relation]:
        return self.by_type("planet_aspect")

    @property
    def planet_houses(self) -> list[Relation]:
        return self.by_type("planet_house")

    @property
    def rulerships(self) -> list[Relation]:
        return self.by_type("house_rulership")

    @property
    def dispositors(self) -> list[Relation]:
        return self.by_type("dispositor")

    @property
    def dignities(self) -> list[Relation]:
        return self.by_type("planet_dignity")

    def __repr__(self) -> str:
        return f"<RelationReport relations={len(self._relations)}>"


# ==========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================================

def _as_list(collection) -> list[dict]:
    """
    Приводит FactCollection / PriorityCollection / list
    к обычному списку словарей.
    """
    if collection is None:
        return []

    if hasattr(collection, "all"):
        return collection.all()

    return list(collection)


def _fact_importance(
    fact_id: str,
    priority_facts: dict[str, dict],
) -> float:
    """Возвращает importance исходного факта."""
    fact = priority_facts.get(fact_id)
    if not fact:
        return 0.0

    return float(fact.get("importance", 0))


def _fact_confidence(
    fact_id: str,
    priority_facts: dict[str, dict],
) -> float:
    """Возвращает confidence исходного факта."""
    fact = priority_facts.get(fact_id)
    if not fact:
        return 0.0

    return float(fact.get("confidence", 0))


def _combined_importance(
    fact_ids: list[str],
    priority_facts: dict[str, dict],
) -> float:
    """
    Рассчитывает importance связи.

    Берём максимум importance среди подтверждающих фактов
    и небольшой бонус за наличие нескольких независимых
    подтверждений.

    Это пока намеренно консервативный алгоритм:
    Relations Engine не должен искусственно раздувать веса.
    """
    if not fact_ids:
        return 0.0

    values = [
        _fact_importance(fid, priority_facts)
        for fid in fact_ids
    ]

    values = [value for value in values if value > 0]

    if not values:
        return 0.0

    maximum = max(values)

    # Небольшой бонус за дополнительные свидетельства.
    bonus = min(10.0, max(0, len(values) - 1) * 2.0)

    return maximum + bonus


def _is_planet(name: str) -> bool:
    return name in PLANETS


def _aspect_relation_weight(aspect_type: str) -> float:
    return ASPECT_WEIGHTS.get(aspect_type, 4.0)


# ==========================================================
# ОСНОВНОЙ BUILDER
# ==========================================================

def build_relations(
    facts,
    priorities,
    max_relations: int = DEFAULT_MAX_RELATIONS,
) -> RelationReport:
    """
    Строит RelationReport из фактов и приоритетов.

    Parameters
    ----------
    facts:
        FactCollection или list[dict].

    priorities:
        PriorityCollection или list[dict].

    max_relations:
        Защитный предел количества создаваемых связей.

    Returns
    -------
    RelationReport

    ВАЖНО:
        Chart сюда НЕ передаётся.
    """

    fact_list = _as_list(facts)
    priority_list = _as_list(priorities)

    # Индекс приоритетных фактов по ID.
    priority_by_id = {
        fact.get("id", ""): fact
        for fact in priority_list
        if fact.get("id")
    }

    relations: list[Relation] = []

    # ------------------------------------------------------
    # 1. ПЛАНЕТА → ДОМ
    # ------------------------------------------------------

    for fact in fact_list:
        if fact.get("type") != "planet_position":
            continue

        planet = fact.get("object", "")
        data = fact.get("data", {})

        if not _is_planet(planet):
            continue

        house = data.get("house")
        if house is None:
            continue

        importance = _fact_importance(
            fact.get("id", ""),
            priority_by_id,
        )

        relations.append(
            Relation(
                type="planet_house",
                source=planet,
                target=f"House_{house}",
                data={
                    "planet": planet,
                    "house": house,
                },
                importance=importance,
                evidence=(fact.get("id", ""),),
            )
        )

    # ------------------------------------------------------
    # 2. ПЛАНЕТА → ЗНАК
    # ------------------------------------------------------

    for fact in fact_list:
        if fact.get("type") != "planet_sign":
            continue

        planet = fact.get("object", "")
        data = fact.get("data", {})
        sign = data.get("sign")

        if not _is_planet(planet) or not sign:
            continue

        importance = _fact_importance(
            fact.get("id", ""),
            priority_by_id,
        )

        relations.append(
            Relation(
                type="planet_sign",
                source=planet,
                target=sign,
                data={
                    "planet": planet,
                    "sign": sign,
                    "degree": data.get("degree", 0),
                },
                importance=importance,
                evidence=(fact.get("id", ""),),
            )
        )

    # ------------------------------------------------------
    # 3. ПЛАНЕТА ↔ ПЛАНЕТА ЧЕРЕЗ АСПЕКТ
    # ------------------------------------------------------

    for fact in fact_list:
        if fact.get("type") != "aspect":
            continue

        data = fact.get("data", {})

        p1 = data.get("planet1", "")
        p2 = data.get("planet2", "")
        aspect_type = data.get("type", "")
        orb = data.get("orb")

        if not _is_planet(p1) or not _is_planet(p2):
            continue

        if not aspect_type:
            continue

        fact_id = fact.get("id", "")

        base_importance = _fact_importance(
            fact_id,
            priority_by_id,
        )

        # Если Priority Engine не дал weight,
        # всё равно сохраняем минимальный структурный вес.
        if base_importance <= 0:
            base_importance = _aspect_relation_weight(aspect_type)

        # Орб аспекта.
        orb = data.get("orb")

        if orb is not None:
            try:
                orb = float(orb)

                # Чем точнее аспект, тем сильнее связь.
                # 0° = максимальный бонус.
                # На границе допустимого орба бонус исчезает.
                orb_bonus = max(0.0, 8.0 - orb)

                base_importance += orb_bonus

            except (TypeError, ValueError):
                orb = None

        relation_data = {
            "planet1": p1,
            "planet2": p2,
            "aspect": aspect_type,
        }

        if orb is not None:
            relation_data["orb"] = orb

        relations.append(
            Relation(
                type="planet_aspect",
                source=p1,
                target=p2,
                data=relation_data,
                importance=base_importance,
                evidence=(fact_id,),
            )
        )

    # ------------------------------------------------------
    # 4. ПЛАНЕТА → УПРАВЛЯЕМЫЙ ДОМ
    # ------------------------------------------------------

    for fact in fact_list:
        if fact.get("type") != "house_ruler":
            continue

        data = fact.get("data", {})
        planet = fact.get("object", "")
        house = data.get("house")

        if not _is_planet(planet) or house is None:
            continue

        fact_id = fact.get("id", "")
        importance = _fact_importance(
            fact_id,
            priority_by_id,
        )

        relations.append(
            Relation(
                type="house_rulership",
                source=planet,
                target=f"House_{house}",
                data={
                    "planet": planet,
                    "house": house,
                    "ruler": data.get("ruler", planet),
                },
                importance=importance,
                evidence=(fact_id,),
            )
        )

    # ------------------------------------------------------
    # 5. ПЛАНЕТА → ДИСПОЗИТОР
    # ------------------------------------------------------

    for fact in fact_list:
        if fact.get("type") != "dispositor":
            continue

        planet = fact.get("object", "")
        data = fact.get("data", {})
        dispositor = data.get("dispositor", "")

        if not _is_planet(planet) or not _is_planet(dispositor):
            continue

        fact_id = fact.get("id", "")
        importance = _fact_importance(
            fact_id,
            priority_by_id,
        )

        relations.append(
            Relation(
                type="dispositor",
                source=planet,
                target=dispositor,
                data={
                    "planet": planet,
                    "dispositor": dispositor,
                },
                importance=importance,
                evidence=(fact_id,),
            )
        )

    # ------------------------------------------------------
    # 6. ПЛАНЕТА → ДОСТОИНСТВО
    # ------------------------------------------------------

    for fact in fact_list:
        if fact.get("type") != "ruler_strength":
            continue

        planet = fact.get("object", "")
        data = fact.get("data", {})
        essential = data.get("essential_details", {})

        if not _is_planet(planet):
            continue

        fact_id = fact.get("id", "")
        importance = _fact_importance(
            fact_id,
            priority_by_id,
        )

        # Достоинство не всегда имеет один boolean-флаг.
        # Сохраняем весь объект как evidence/data.
        relations.append(
            Relation(
                type="planet_dignity",
                source=planet,
                target="essential_dignity",
                data={
                    "planet": planet,
                    "details": essential,
                },
                importance=importance,
                evidence=(fact_id,),
            )
        )

    # ------------------------------------------------------
    # 7. СВЯЗИ С ВАЖНЫМИ ОБЪЕКТАМИ
    # ------------------------------------------------------
    #
    # Пока только помечаем факт как "important_object".
    # Это не создаёт искусственной новой астрологической связи,
    # а сохраняет информацию для будущего Pattern Engine.

    important_objects = {
        fact.get("object")
        for fact in priority_list
        if (
            fact.get("object")
            and fact.get("importance", 0) >= IMPORTANT_FACT_MIN
            and (
                _is_planet(fact.get("object"))
                or fact.get("type") in {
                    "house_ruler",
                    "dispositor",
                }
            )
        )
    }

    for fact in priority_list:
        obj = fact.get("object", "")

        if not obj or obj not in important_objects:
            continue

        fact_id = fact.get("id", "")

        # Не создаём дубликатов для фактов,
        # которые уже представлены специализированными relations.
        if fact.get("type") in {
            "planet_position",
            "planet_sign",
            "aspect",
            "house_ruler",
            "dispositor",
            "ruler_strength",
        }:
            continue

        relations.append(
            Relation(
                type="important_object",
                source=obj,
                target="priority",
                data={
                    "object": obj,
                    "fact_type": fact.get("type"),
                },
                importance=float(fact.get("importance", 0)),
                evidence=(fact_id,),
            )
        )

    # ------------------------------------------------------
    # 8. УДАЛЕНИЕ ДУБЛИКАТОВ
    # ------------------------------------------------------

    unique: dict[tuple, Relation] = {}

    for relation in relations:
        key = (
            relation.type,
            relation.source,
            relation.target,
            repr(sorted(relation.data.items(), key=str)),
        )

        existing = unique.get(key)

        if existing is None:
            unique[key] = relation
            continue

        # Если одно и то же отношение встретилось повторно,
        # сохраняем более сильное.
        if relation.importance > existing.importance:
            unique[key] = relation

    relations = list(unique.values())

    # ------------------------------------------------------
    # 9. СОРТИРОВКА И ОГРАНИЧЕНИЕ
    # ------------------------------------------------------

    relations.sort(
        key=lambda relation: relation.importance,
        reverse=True,
    )

    if max_relations > 0:
        relations = relations[:max_relations]

    return RelationReport(relations)


# ==========================================================
# УДОБНЫЕ ФИЛЬТРЫ
# ==========================================================

def find_relations_for_planet(
    report: RelationReport,
    planet: str,
) -> list[Relation]:
    """
    Возвращает все отношения конкретной планеты.
    """
    return report.for_object(planet)


def find_aspect(
    report: RelationReport,
    planet1: str,
    planet2: str,
) -> Relation | None:
    """
    Возвращает отношение аспекта между двумя планетами.
    """
    for relation in report.aspects:
        if (
            {relation.source, relation.target}
            == {planet1, planet2}
        ):
            return relation

    return None


def strongest_relations(
    report: RelationReport,
    n: int = 10,
) -> list[Relation]:
    """
    Возвращает наиболее весомые связи.
    """
    return report.top(n)