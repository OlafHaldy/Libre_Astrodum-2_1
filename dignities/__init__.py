"""
Liber Astrodum — dignities
"""

from .zodiac import (
    ZODIAC, SIGN_ELEMENT, SIGN_MODE, SIGN_POLARITY, OPPOSITE_SIGN
)
from .planets import SEPTENER, ALL_PLANETS
from .egyptian_terms import EGYPTIAN_TERMS
from .faces import FACES
from .triplicity import TRIPLICITY_RULERS
from .scores import calculate_essential_score
from .labels import DIGNITY_LABELS
from core.rulerships import DOMICILE, DETRIMENT

EXALTATION = {
    'Sun': 'Aries', 'Moon': 'Taurus', 'Mercury': 'Virgo',
    'Venus': 'Pisces', 'Mars': 'Capricorn', 'Jupiter': 'Cancer',
    'Saturn': 'Libra'
}

FALL = {}
for planet, sign in EXALTATION.items():
    FALL[planet] = OPPOSITE_SIGN[sign]

def get_term_ruler(sign, degree):
    for start, end, ruler in EGYPTIAN_TERMS.get(sign, []):
        if start <= degree <= end:
            return ruler
    return None

def get_face_ruler(sign, degree):
    for start, end, ruler in FACES.get(sign, []):
        if start <= degree <= end:
            return ruler
    return None

def get_triplicity_rulers(sign, is_day):
    element = SIGN_ELEMENT[sign]
    day_ruler, night_ruler = TRIPLICITY_RULERS[element]
    if is_day:
        return (day_ruler, night_ruler)
    return (night_ruler, day_ruler)

def get_all_essential_dignities(planet, sign, degree, is_day=True):
    dignities = {
        'domicile': sign in DOMICILE.get(planet, []),
        'exaltation': sign == EXALTATION.get(planet, ''),
        'detriment': sign in DETRIMENT.get(planet, []),
        'fall': sign == FALL.get(planet, ''),
        'triplicity_ruler': None,
        'triplicity_secondary': None,
        'term_ruler': None,
        'face_ruler': None
    }
    tri = get_triplicity_rulers(sign, is_day)
    dignities['triplicity_ruler'] = tri[0]
    dignities['triplicity_secondary'] = tri[1]
    dignities['term_ruler'] = get_term_ruler(sign, degree)
    dignities['face_ruler'] = get_face_ruler(sign, degree)
    dignities['essential_score'] = calculate_essential_score(dignities)
    return dignities