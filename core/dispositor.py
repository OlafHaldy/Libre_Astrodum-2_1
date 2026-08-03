"""
Liber Astrodum

core/dispositor.py

Строит граф диспозиций для карты.

Использует единый источник истины: core/rulerships.py.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.1
"""

from core.rulerships import SIGN_RULER


def build_dispositor_graph(positions: dict) -> dict:
    """
    Строит граф диспозиций.

    Для каждой планеты находит управителя знака,
    в котором она стоит.

    Parameters
    ----------
    positions : dict
        Словарь планет с полем 'sign'.

    Returns
    -------
    dict
        {"Sun": "Saturn", "Moon": "Jupiter", ...}.
    """
    graph = {}
    for planet_name, data in positions.items():
        sign = data.get("sign", "")
        dispositor = SIGN_RULER.get(sign)
        if dispositor:
            graph[planet_name] = dispositor
    return graph