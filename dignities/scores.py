"""
Liber Astrodum — scores.py
Баллы эссенциальных достоинств.
"""

SCORE_DOMICILE = 5
SCORE_EXALTATION = 4
SCORE_TRIPLICITY = 3
SCORE_TERM = 2
SCORE_FACE = 1
SCORE_DETRIMENT = -5
SCORE_FALL = -4

def calculate_essential_score(d):
    s = 0
    if d.get('domicile'): s += SCORE_DOMICILE
    if d.get('exaltation'): s += SCORE_EXALTATION
    if d.get('detriment'): s += SCORE_DETRIMENT
    if d.get('fall'): s += SCORE_FALL
    if d.get('triplicity_ruler'): s += SCORE_TRIPLICITY
    if d.get('term_ruler'): s += SCORE_TERM
    if d.get('face_ruler'): s += SCORE_FACE
    return s
