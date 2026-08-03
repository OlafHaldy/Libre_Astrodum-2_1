"""
Liber Astrodum

fact_engine/fact_builder.py

Сборщик фактов из Chart.
Принимает Chart целиком — не зависит от внутренней структуры.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.1
"""

from .fact_collection import FactCollection


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

    # Планеты
    for planet_name, data in chart.planets.items():
        facts_list.append({
            "id": f"planet_position_{planet_name}",
            "type": "planet_position",
            "producer": "astrology_engine",
            "object": planet_name,
            "data": data,
        })
        if 'sign' in data:
            facts_list.append({
                "id": f"planet_sign_{planet_name}",
                "type": "planet_sign",
                "producer": "astrology_engine",
                "object": planet_name,
                "data": {
                    "planet": planet_name,
                    "sign": data['sign'],
                    "degree": data.get('degree', 0),
                },
            })

    # Дома
    for house_num, data in chart.houses.items():
        if isinstance(house_num, int):
            facts_list.append({
                "id": f"house_position_{house_num}",
                "type": "house_position",
                "producer": "astrology_engine",
                "object": f"House_{house_num}",
                "data": data,
            })

    # Управители домов
    for house_num, ruler_data in chart.house_rulers.items():
        ruler = ruler_data.get('ruler', 'Unknown')
        facts_list.append({
            "id": f"{ruler}_rules_house_{house_num}",
            "type": "house_ruler",
            "producer": "house_rulers",
            "object": ruler,
            "data": ruler_data,
        })

    # Аспекты
    for aspect_data in chart.aspects:
        p1 = aspect_data.get('planet1', '')
        p2 = aspect_data.get('planet2', '')
        asp_type = aspect_data.get('type', '')
        facts_list.append({
            "id": f"aspect_{p1}_{asp_type}_{p2}",
            "type": "aspect",
            "producer": "aspects",
            "object": p1,
            "data": aspect_data,
        })

    return FactCollection(facts_list)