"""
Liber Astrodum

sinastriya.py

Обзорная синастрия по датам рождения.
Без времени рождения: только Солнце, Венера, Марс, Меркурий.
"""

from datetime import datetime
import swisseph as swe


SIGNS = [
    'Овен', 'Телец', 'Близнецы', 'Рак',
    'Лев', 'Дева', 'Весы', 'Скорпион',
    'Стрелец', 'Козерог', 'Водолей', 'Рыбы'
]

ASPECTS = {
    'соединение': (0, 8),
    'секстиль': (60, 4),
    'квадрат': (90, 6),
    'трин': (120, 6),
    'оппозиция': (180, 8),
}


def _planet_positions(year, month, day, hour=12.0):
    """Считает позиции планет на полдень указанной даты."""
    jd = swe.julday(year, month, day, hour)

    result = {}
    for name, pid in {
        'Солнце': swe.SUN,
        'Венера': swe.VENUS,
        'Марс': swe.MARS,
        'Меркурий': swe.MERCURY,
    }.items():
        lon = swe.calc_ut(jd, pid)[0][0]
        sign_num = int(lon // 30)
        degree = round(lon % 30, 2)
        result[name] = {
            'longitude': lon,
            'sign': SIGNS[sign_num],
            'degree': degree,
        }

    return result


def _angle_diff(lon1, lon2):
    """Разница между долготами в градусах (0..180)."""
    diff = abs(lon1 - lon2) % 360
    if diff > 180:
        diff = 360 - diff
    return diff


def _find_aspects(pos1, pos2):
    """Находит аспекты между двумя наборами планет."""
    found = []
    for p1, data1 in pos1.items():
        for p2, data2 in pos2.items():
            diff = _angle_diff(data1['longitude'], data2['longitude'])
            for asp_name, (target, orb) in ASPECTS.items():
                if abs(diff - target) <= orb:
                    found.append({
                        'p1': p1,
                        'p2': p2,
                        'type': asp_name,
                        'orb': round(abs(diff - target), 2),
                    })
                    break
    return found


def build_sinastriya(
    name1, date1,
    name2, date2,
):
    """
    Строит обзорную синастрию.

    date1, date2 — строки формата 'YYYY-MM-DD' или datetime.
    """
    if isinstance(date1, str):
        date1 = datetime.strptime(date1, '%Y-%m-%d')
    if isinstance(date2, str):
        date2 = datetime.strptime(date2, '%Y-%m-%d')

    pos1 = _planet_positions(date1.year, date1.month, date1.day)
    pos2 = _planet_positions(date2.year, date2.month, date2.day)

    aspects = _find_aspects(pos1, pos2)

    return {
        'name1': name1,
        'name2': name2,
        'pos1': pos1,
        'pos2': pos2,
        'aspects': aspects,
    }


def format_for_prompt(data):
    """Готовит текст для LLM."""
    lines = []

    for key, label in (
        ('Солнце', 'Солнце'),
        ('Венера', 'Венера'),
        ('Марс', 'Марс'),
        ('Меркурий', 'Меркурий'),
    ):
        p1 = data['pos1'][key]
        p2 = data['pos2'][key]
        lines.append(
            f"{label}1: {p1['sign']} {p1['degree']}° | "
            f"{label}2: {p2['sign']} {p2['degree']}°"
        )

    lines.append('')
    lines.append('Аспекты между ними:')
    if data['aspects']:
        for a in data['aspects']:
            lines.append(
                f"- {a['p1']}1 — {a['p2']}2: {a['type']} (орб {a['orb']}°)"
            )
    else:
        lines.append('- нет точных аспектов')

    return '\n'.join(lines)