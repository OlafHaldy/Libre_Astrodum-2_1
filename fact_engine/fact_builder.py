"""
Liber Astrodum

fact_engine/fact_builder.py

Сборщик фактов из Chart.
Превращает ВСЁ содержимое Chart в факты.
После этого модули анализа не должны обращаться к Chart.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.2
"""

from .fact_collection import FactCollection

# Константы для producer
PRODUCER_ASTROLOGY = "astrology_engine"
PRODUCER_HOUSE_RULERS = "house_rulers"
PRODUCER_ASPECTS = "aspects"
PRODUCER_DIGNITIES = "dignities_engine"
PRODUCER_DISPOSITOR = "dispositor"
PRODUCER_CHART = "chart"


def build_facts(chart) -> FactCollection:
    """
    Собирает факты из Chart.

    Parameters
    ----------
    chart : Chart
        Готовая карта.

    Returns
    -------
    FactCollection
    """
    facts_list = []

    # ----------------------------------------------------------
    # 1. ПЛАНЕТЫ
    # ----------------------------------------------------------
    for planet_name, data in chart.planets.items():
        facts_list.append({
            "id": f"planet_position_{planet_name}",
            "type": "planet_position",
            "producer": PRODUCER_ASTROLOGY,
            "object": planet_name,
            "data": data,
        })

        # Знак планеты
        if 'sign' in data:
            facts_list.append({
                "id": f"planet_sign_{planet_name}",
                "type": "planet_sign",
                "producer": PRODUCER_ASTROLOGY,
                "object": planet_name,
                "data": {
                    "planet": planet_name,
                    "sign": data['sign'],
                    "degree": data.get('degree', 0),
                },
            })

    # ----------------------------------------------------------
    # 2. ДОМА
    # ----------------------------------------------------------
    for house_num, data in chart.houses.items():
        if isinstance(house_num, int):
            facts_list.append({
                "id": f"house_position_{house_num}",
                "type": "house_position",
                "producer": PRODUCER_ASTROLOGY,
                "object": f"House_{house_num}",
                "data": data,
            })

    # ----------------------------------------------------------
    # 3. УПРАВИТЕЛИ ДОМОВ
    # ----------------------------------------------------------
    for house_num, ruler_data in chart.house_rulers.items():
        ruler = ruler_data.get('ruler', 'Unknown')
        facts_list.append({
            "id": f"{ruler}_rules_house_{house_num}",
            "type": "house_ruler",
            "producer": PRODUCER_HOUSE_RULERS,
            "object": ruler,
            "data": ruler_data,
        })

    # ----------------------------------------------------------
    # 4. АСПЕКТЫ (с правильным объектом)
    # ----------------------------------------------------------
    for aspect_data in chart.aspects:
        p1 = aspect_data.get('planet1', '')
        p2 = aspect_data.get('planet2', '')
        asp_type = aspect_data.get('type', '')
        aspect_id = f"{p1}_{asp_type}_{p2}"
        facts_list.append({
            "id": f"aspect_{aspect_id}",
            "type": "aspect",
            "producer": PRODUCER_ASPECTS,
            "object": aspect_id,          # ← теперь объект — весь аспект
            "data": aspect_data,
        })

    # ----------------------------------------------------------
    # 5. ДОСТОИНСТВА (каждой планеты)
    # ----------------------------------------------------------
    for planet_name, dignity_data in chart.essential_dignities.items():
        facts_list.append({
            "id": f"dignity_{planet_name}",
            "type": "ruler_strength",
            "producer": PRODUCER_DIGNITIES,
            "object": planet_name,
            "data": {
                "planet": planet_name,
                "essential_details": dignity_data,
            },
        })

    # ----------------------------------------------------------
    # 6. ДИСПОЗИТОРЫ
    # ----------------------------------------------------------
    for planet_name, dispositor_name in chart.dispositor_graph.items():
        facts_list.append({
            "id": f"dispositor_{planet_name}",
            "type": "dispositor",
            "producer": PRODUCER_DISPOSITOR,
            "object": planet_name,
            "data": {
                "planet": planet_name,
                "dispositor": dispositor_name,
            },
        })

    # ----------------------------------------------------------
    # 7. МЕТАДАННЫЕ КАРТЫ
    # ----------------------------------------------------------
    facts_list.append({
        "id": "chart_type",
        "type": "chart_metadata",
        "producer": PRODUCER_CHART,
        "object": "Chart",
        "data": {
            "type": chart.type,
            "datetime": chart.datetime,
            "lat": chart.lat,
            "lon": chart.lon,
            "house_system": chart.metadata.house_system,
            "zodiac": chart.metadata.zodiac,
            "engine_version": chart.metadata.engine_version,
        },
    })

    return FactCollection(facts_list)