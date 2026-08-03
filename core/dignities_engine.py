"""
Liber Astrodum

core/dignities_engine.py

Вычисляет эссенциальные достоинства для всех планет карты.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.0
"""

from dignities import get_all_essential_dignities


def build_essential_dignities(positions: dict, is_day: bool = True) -> dict:
    """
    Вычисляет эссенциальные достоинства для всех планет.

    Parameters
    ----------
    positions : dict
        Словарь планет с полями 'sign' и 'degree'.
    is_day : bool
        Дневная карта?

    Returns
    -------
    dict
        Словарь: {"Sun": DignityData, "Moon": DignityData, ...}.
    """
    dignities = {}
    for planet_name, data in positions.items():
        sign = data.get("sign", "")
        degree = data.get("degree", 0)
        dignities[planet_name] = get_all_essential_dignities(
            planet_name, sign, degree, is_day
        )
    return dignities