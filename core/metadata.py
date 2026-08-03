"""
Liber Astrodum

core/metadata.py

Неизменяемый объект метаданных карты.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.0
"""


class ChartMetadata:
    """
    Метаданные астрологической карты.

    Неизменяем после создания.
    """

    def __init__(
        self,
        engine_version: str,
        house_system: str = "Placidus",
        zodiac: str = "Tropical",
        ephemeris_version: str = "default",
        created_at: str = "",
    ):
        self._engine_version = engine_version
        self._house_system = house_system
        self._zodiac = zodiac
        self._ephemeris_version = ephemeris_version
        self._created_at = created_at

    @property
    def engine_version(self) -> str:
        return self._engine_version

    @property
    def house_system(self) -> str:
        return self._house_system

    @property
    def zodiac(self) -> str:
        return self._zodiac

    @property
    def ephemeris_version(self) -> str:
        return self._ephemeris_version

    @property
    def created_at(self) -> str:
        return self._created_at

    def to_dict(self) -> dict:
        return {
            "engine_version": self._engine_version,
            "house_system": self._house_system,
            "zodiac": self._zodiac,
            "ephemeris_version": self._ephemeris_version,
            "created_at": self._created_at,
        }

    def __repr__(self) -> str:
        return f"<ChartMetadata engine={self._engine_version} houses={self._house_system}>"