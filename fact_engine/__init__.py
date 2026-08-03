"""
Liber Astrodum

fact_engine/__init__.py

Пакет Fact Engine — слой извлечения фактов из Chart.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.0
"""

from .fact_builder import build_facts
from .fact_collection import FactCollection

__all__ = ['build_facts', 'FactCollection']