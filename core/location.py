"""
Liber Astrodum

core/location.py

Неизменяемый объект географических координат.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.0
"""


class Location:
    """
    Географические координаты места.

    Неизменяем после создания.
    """

    def __init__(self, lat: float, lon: float):
        self._lat = lat
        self._lon = lon

    @property
    def lat(self) -> float:
        return self._lat

    @property
    def lon(self) -> float:
        return self._lon

    def to_dict(self) -> dict:
        return {"lat": self._lat, "lon": self._lon}

    def __repr__(self) -> str:
        return f"<Location lat={self._lat} lon={self._lon}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Location):
            return False
        return self._lat == other._lat and self._lon == other._lon