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
    2.0
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

# Изгнание: {планета: [знаки]} (оппозит обители)
OPPOSITE_SIGN = {
    "Aries": "Libra", "Taurus": "Scorpio", "Gemini": "Sagittarius",
    "Cancer": "Capricorn", "Leo": "Aquarius", "Virgo": "Pisces",
    "Libra": "Aries", "Scorpio": "Taurus", "Sagittarius": "Gemini",
    "Capricorn": "Cancer", "Aquarius": "Leo", "Pisces": "Virgo",
}

DETRIMENT = {}
for planet, signs in DOMICILE.items():
    DETRIMENT[planet] = [OPPOSITE_SIGN[s] for s in signs]