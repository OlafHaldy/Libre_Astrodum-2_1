"""
Liber Astrodum

fact_engine/fact_collection.py

Коллекция астрологических фактов.
Неизменяемая. Предоставляет семантические методы доступа.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0 — Fact Engine v2.2

Версия:
    2.2
"""


class FactCollection:
    """
    Коллекция астрологических фактов.
    Неизменяемая — все методы возвращают копии.
    """

    def __init__(self, facts: list[dict] | None = None):
        self._facts = list(facts) if facts is not None else []
        self._by_object = {}
        self._by_type = {}
        self._build_index()

    def _build_index(self):
        for f in self._facts:
            obj = f.get('object', '')
            typ = f.get('type', '')
            if obj not in self._by_object:
                self._by_object[obj] = []
            self._by_object[obj].append(f)
            if typ not in self._by_type:
                self._by_type[typ] = []
            self._by_type[typ].append(f)

    # ==========================================================
    # БАЗОВЫЕ МЕТОДЫ
    # ==========================================================

    def all(self) -> list[dict]:
        return list(self._facts)

    def __len__(self) -> int:
        return len(self._facts)

    def __iter__(self):
        return iter(self._facts)

    def __getitem__(self, index):
        return self._facts[index]

    # ==========================================================
    # ФИЛЬТРАЦИЯ
    # ==========================================================

    def by_type(self, type_name: str) -> list[dict]:
        return list(self._by_type.get(type_name, []))

    def by_producer(self, producer_name: str) -> list[dict]:
        return [f for f in self._facts if f.get('producer') == producer_name]

    def for_planet(self, planet_name: str) -> list[dict]:
        return list(self._by_object.get(planet_name, []))

    def planets(self) -> list[str]:
        result = []
        for obj in self._by_object:
            if obj in ('Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn',
                        'Uranus', 'Neptune', 'Pluto', 'True Node', 'Chiron'):
                result.append(obj)
        return result

    def exists(self, type_name: str = None, object_name: str = None) -> bool:
        if type_name and type_name not in self._by_type:
            return False
        if object_name and object_name not in self._by_object:
            return False
        if type_name and object_name:
            return any(f.get('object') == object_name for f in self._by_type[type_name])
        return True

    def count(self, type_name: str = None, object_name: str = None) -> int:
        if type_name and object_name:
            return sum(1 for f in self._by_type.get(type_name, [])
                       if f.get('object') == object_name)
        if type_name:
            return len(self._by_type.get(type_name, []))
        if object_name:
            return len(self._by_object.get(object_name, []))
        return len(self._facts)

    def filter(self, type_name: str = None, object_name: str = None) -> list[dict]:
        result = []
        for f in self._facts:
            if type_name and f.get('type') != type_name:
                continue
            if object_name and f.get('object') != object_name:
                continue
            result.append(f)
        return result

    # ==========================================================
    # СЕМАНТИЧЕСКИЕ МЕТОДЫ
    # ==========================================================

    def planet_positions(self) -> list[dict]:
        return self.by_type('planet_position')

    def house_rulers(self) -> list[dict]:
        return self.by_type('house_ruler')

    def aspects(self) -> list[dict]:
        return self.by_type('aspect')

    def strengths(self) -> list[dict]:
        return self.by_type('ruler_strength')

    def to_list(self) -> list[dict]:
        return list(self._facts)