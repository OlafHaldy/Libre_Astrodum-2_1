"""
Liber Astrodum

priority_engine/__init__.py

Пакет Priority Engine — слой взвешивания фактов.
Определяет, какие факты карты наиболее важны.
Ничего не вычисляет — только добавляет priority и weight.

Автор:
    Olaf Haldi

Архитектура:
    Astrodo Stage III — Priority Engine v1.0

Версия:
    1.0
"""

from .priority_builder import build_priorities

__all__ = ['build_priorities']
