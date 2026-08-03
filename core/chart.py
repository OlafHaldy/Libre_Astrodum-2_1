"""
Liber Astrodum

core/chart.py

Единый объект астрологической карты (Chart).
Неизменяемая модель данных.

Содержит только объективные (астрономические) данные.
Не содержит результатов анализа (фактов, приоритетов, выводов).

Использует:
- Location (координаты)
- ChartMetadata (метаданные)

Спецификация: docs/CORE_OBJECTS.md
Конвейер: docs/PIPELINE_SPEC.md

TODO: заменить внутренние dict на dataclass-модели (Planet, House, Aspect, Ruler)
      для полной иммутабельности.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.1
"""

from core.location import Location
from core.metadata import ChartMetadata


class Chart:
    """
    Неизменяемая модель астрологической карты.

    Содержит:
    - тип карты
    - дату и время
    - координаты (Location)
    - планеты
    - дома и углы
    - аспекты
    - управителей домов
    - эссенциальные достоинства
    - граф диспозиторов
    - метаданные (ChartMetadata)

    После создания не модифицируется.
    Builder обязан заполнить ВСЕ поля, включая
    essential_dignities и dispositor_graph.
    """

    def __init__(
        self,
        chart_type: str,
        datetime_str: str,
        location: Location,
        planets: dict,
        houses: dict,
        aspects: list,
        house_rulers: dict,
        essential_dignities: dict,
        dispositor_graph: dict,
        metadata: ChartMetadata,
    ):
        """
        Parameters
        ----------
        chart_type : str
            Тип карты: "natal", "solar", "lunar", "progression", "synastry", "election".
        datetime_str : str
            ISO-формат даты и времени: "2026-08-07T16:38:00".
        location : Location
            Координаты места.
        planets : dict
            Словарь планет: {"Sun": {...}, ...}.
        houses : dict
            Словарь домов: {1: {...}, ..., 12: {...}, "Ascendant": {...}, "MC": {...}}.
        aspects : list
            Список аспектов: [{...}, ...].
        house_rulers : dict
            Словарь управителей домов: {1: {...}, ...}.
        essential_dignities : dict
            Словарь достоинств: {"Sun": {...}, ...}.
            Заполняется Builder'ом (через Dignities Engine).
        dispositor_graph : dict
            Граф диспозиций: {"Sun": "Saturn", ...}.
            Заполняется Builder'ом (через Dispositor Engine).
        metadata : ChartMetadata
            Метаданные карты.
        """
        self._type = chart_type
        self._datetime = datetime_str
        self._location = location
        self._planets = planets
        self._houses = houses
        self._aspects = aspects
        self._house_rulers = house_rulers
        self._essential_dignities = essential_dignities
        self._dispositor_graph = dispositor_graph
        self._metadata = metadata

    # ==========================================================
    # СВОЙСТВА (read-only)
    # ==========================================================

    @property
    def type(self) -> str:
        return self._type

    @property
    def datetime(self) -> str:
        return self._datetime

    @property
    def location(self) -> Location:
        return self._location

    @property
    def lat(self) -> float:
        return self._location.lat

    @property
    def lon(self) -> float:
        return self._location.lon

    @property
    def planets(self) -> dict:
        return dict(self._planets)

    @property
    def houses(self) -> dict:
        return dict(self._houses)

    @property
    def aspects(self) -> list:
        return list(self._aspects)

    @property
    def house_rulers(self) -> dict:
        return dict(self._house_rulers)

    @property
    def essential_dignities(self) -> dict:
        return dict(self._essential_dignities)

    @property
    def dispositor_graph(self) -> dict:
        return dict(self._dispositor_graph)

    @property
    def metadata(self) -> ChartMetadata:
        return self._metadata

    # ==========================================================
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    # ==========================================================

    def get_planet(self, name: str) -> dict | None:
        return self._planets.get(name)

    def get_house(self, number: int) -> dict | None:
        return self._houses.get(number)

    def get_ascendant(self) -> dict | None:
        return self._houses.get("Ascendant")

    def get_mc(self) -> dict | None:
        return self._houses.get("MC")

    def get_house_ruler(self, house_number: int) -> dict | None:
        return self._house_rulers.get(house_number)

    def get_dispositor(self, planet_name: str) -> str | None:
        return self._dispositor_graph.get(planet_name)

    def get_dignity(self, planet_name: str) -> dict | None:
        return self._essential_dignities.get(planet_name)

    # ==========================================================
    # СЕРИАЛИЗАЦИЯ
    # ==========================================================

    def to_dict(self) -> dict:
        return {
            "type": self._type,
            "datetime": self._datetime,
            "location": self._location.to_dict(),
            "planets": dict(self._planets),
            "houses": dict(self._houses),
            "aspects": list(self._aspects),
            "house_rulers": dict(self._house_rulers),
            "essential_dignities": dict(self._essential_dignities),
            "dispositor_graph": dict(self._dispositor_graph),
            "metadata": self._metadata.to_dict(),
        }

    def __repr__(self) -> str:
        return f"<Chart type='{self._type}' datetime='{self._datetime}'>"