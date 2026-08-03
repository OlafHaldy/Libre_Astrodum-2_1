"""
Liber Astrodum

core/planet_house_engine.py

Назначает планетам номера домов на основе их долготы.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.0
"""


def assign_planet_houses(positions: dict, houses: dict) -> dict:
    """
    Назначает каждой планете номер дома.

    Parameters
    ----------
    positions : dict
        Словарь планет с полем 'longitude'.
    houses : dict
        Словарь домов с полем 'longitude'.

    Returns
    -------
    dict
        Тот же positions с заполненным полем 'house'.
    """
    for planet_name, data in positions.items():
        planet_lon = data["longitude"]
        data["house"] = None

        for house_num in range(1, 13):
            cusp_lon = houses[house_num]["longitude"]
            next_house = house_num + 1 if house_num < 12 else 1
            next_cusp_lon = houses[next_house]["longitude"]

            if next_cusp_lon <= cusp_lon:
                next_cusp_lon += 360

            planet_check = planet_lon
            if planet_check < cusp_lon:
                planet_check += 360

            if cusp_lon <= planet_check < next_cusp_lon:
                data["house"] = house_num
                break

    return positions