"""
Liber Astrodum

builders/natal_builder.py

Построитель натальной карты.
Не вычисляет ничего — только вызывает специализированные модули
и собирает Chart.

Спецификация: docs/PIPELINE_SPEC.md, Шаг 1

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.1
"""

from datetime import datetime

from astrology_engine import (
    get_planet_positions,
    get_houses,
    calculate_aspects,
)
from house_rulers import build_house_rulers
from core.planet_house_engine import assign_planet_houses
from core.dignities_engine import build_essential_dignities
from core.dispositor import build_dispositor_graph
from core.chart import Chart
from core.location import Location
from core.metadata import ChartMetadata


def build_natal_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    lat: float,
    lon: float,
) -> Chart:
    """
    Строит натальную карту.

    Не вычисляет ничего самостоятельно.
    Каждый шаг — вызов специализированного модуля.
    """
    # 1. Планеты
    positions = get_planet_positions(year, month, day, hour, minute)

    # 2. Дома
    houses = get_houses(year, month, day, hour, minute, lat, lon)

    # 3. Назначение планет в дома
    positions = assign_planet_houses(positions, houses)

    # 4. Аспекты
    aspects = calculate_aspects(positions)

    # 5. Управители домов
    house_rulers = build_house_rulers(houses, positions)

    # 6. Эссенциальные достоинства
    essential_dignities = build_essential_dignities(positions)

    # 7. Граф диспозиторов
    dispositor_graph = build_dispositor_graph(positions)

    # 8. Метаданные и координаты
    metadata = ChartMetadata(
        engine_version="2.0",
        house_system="Placidus",
        zodiac="Tropical",
        ephemeris_version="default",
        created_at=datetime.utcnow().isoformat(),
    )
    location = Location(lat=lat, lon=lon)
    datetime_str = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"

    # 9. Сборка Chart
    return Chart(
        chart_type="natal",
        datetime_str=datetime_str,
        location=location,
        planets=positions,
        houses=houses,
        aspects=aspects,
        house_rulers=house_rulers,
        essential_dignities=essential_dignities,
        dispositor_graph=dispositor_graph,
        metadata=metadata,
    )