"""
Liber Astrodum

core/rulerships.py

Единый источник истины: классические управители знаков.

Используется:
- dignities/ (для определения обители, изгнания)
- core/dispositor.py (для построения графа диспозиторов)
- house_rulers.py (для определения управителей домов)

Только септенер. Уран, Нептун, Плутон не управляют знаками.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.1
"""

# ==========================================================
# КЛАССИЧЕСКИЕ УПРАВИТЕЛИ ЗНАКОВ (септенер)
# ==========================================================

SIGN_RULER = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

# ==========================================================
# ПРОИЗВОДНЫЕ СЛОВАРИ
# ==========================================================

# Обители: {планета: [знаки]}
DOMICILE = {}
for sign, ruler in SIGN_RULER.items():
    if ruler not in DOMICILE:
        DOMICILE[ruler] = []
    DOMICILE[ruler].append(sign)

# Противоположные знаки
OPPOSITE_SIGN = {
    "Aries": "Libra", "Taurus": "Scorpio", "Gemini": "Sagittarius",
    "Cancer": "Capricorn", "Leo": "Aquarius", "Virgo": "Pisces",
    "Libra": "Aries", "Scorpio": "Taurus", "Sagittarius": "Gemini",
    "Capricorn": "Cancer", "Aquarius": "Leo", "Pisces": "Virgo",
}

# Изгнание: {планета: [знаки]} (оппозит обители)
DETRIMENT = {}
for planet, signs in DOMICILE.items():
    DETRIMENT[planet] = [OPPOSITE_SIGN[s] for s in signs]

# ==========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================================

def get_ruler_by_sign(sign: str) -> str:
    """
    Возвращает классического управителя знака.

    Пример:
        get_ruler_by_sign("Aries") -> "Mars"
        get_ruler_by_sign("Aquarius") -> "Saturn"
    """
    return SIGN_RULER.get(sign)


def get_domicile(planet: str) -> list:
    """
    Возвращает список знаков, которыми управляет планета (обитель).

    Пример:
        get_domicile("Mercury") -> ["Gemini", "Virgo"]
    """
    return DOMICILE.get(planet, [])


def get_detriment(planet: str) -> list:
    """
    Возвращает список знаков, в которых планета в изгнании.

    Пример:
        get_detriment("Mercury") -> ["Sagittarius", "Pisces"]
    """
    return DETRIMENT.get(planet, [])


def is_domicile(planet: str, sign: str) -> bool:
    """Проверяет, находится ли планета в обители."""
    return sign in DOMICILE.get(planet, [])


def is_detriment(planet: str, sign: str) -> bool:
    """Проверяет, находится ли планета в изгнании."""
    return sign in DETRIMENT.get(planet, [])