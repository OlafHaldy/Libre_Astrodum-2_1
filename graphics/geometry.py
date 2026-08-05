"""
Liber Astrodum
graphics/geometry.py

Вся геометрия колеса.

Версия 3.0

Никакой SVG.
Никаких цветов.
Только математика.
"""

import math

# ==========================================================
# ДОЛГОТА → УГОЛ
# ==========================================================

def longitude_to_angle(longitude: float) -> float:
    """
    Преобразует астрологическую долготу
    в угол SVG.

    0° Овна находится сверху.

    Возвращает угол в градусах.
    """

    return (longitude - 90) % 360


# ==========================================================
# УГОЛ → РАДИАНЫ
# ==========================================================

def angle_to_radians(angle: float) -> float:
    return math.radians(angle)


# ==========================================================
# КООРДИНАТЫ НА ОКРУЖНОСТИ
# ==========================================================

def polar_to_cartesian(cx, cy, radius, longitude):
    """
    Переводит долготу в координаты SVG.

    Parameters
    ----------

    cx
        Центр X

    cy
        Центр Y

    radius
        Радиус

    longitude
        Эклиптическая долгота
    """

    angle = longitude_to_angle(longitude)

    rad = angle_to_radians(angle)

    x = cx + radius * math.cos(rad)

    y = cy + radius * math.sin(rad)

    return x, y


# ==========================================================
# ПРОТИВОПОЛОЖНАЯ ТОЧКА
# ==========================================================

def opposite_longitude(longitude):
    return (longitude + 180) % 360


# ==========================================================
# СЕРЕДИНА ДВУХ ДОЛГОТ
# ==========================================================

def midpoint(lon1, lon2):
    diff = (lon2 - lon1 + 360) % 360

    return (lon1 + diff / 2) % 360


# ==========================================================
# РАССТОЯНИЕ МЕЖДУ ДВУМЯ ДОЛГОТАМИ
# ==========================================================

def angular_distance(lon1, lon2):

    diff = abs(lon1 - lon2)

    if diff > 180:
        diff = 360 - diff

    return diff


# ==========================================================
# SVG ARC
# ==========================================================

def describe_arc(cx, cy, radius, start_lon, end_lon):
    """
    Возвращает SVG Path для дуги.
    """

    start = polar_to_cartesian(cx, cy, radius, start_lon)

    end = polar_to_cartesian(cx, cy, radius, end_lon)

    diff = (end_lon - start_lon) % 360

    large_arc = 1 if diff > 180 else 0

    return (
        f"M {start[0]:.2f} {start[1]:.2f} "
        f"A {radius:.2f} {radius:.2f} "
        f"0 {large_arc} 1 "
        f"{end[0]:.2f} {end[1]:.2f}"
    )


# ==========================================================
# ВРАЩЕНИЕ ТЕКСТА
# ==========================================================

def text_rotation(longitude):
    """
    Возвращает угол поворота текста.

    Чтобы подписи не были вверх ногами.
    """

    angle = longitude_to_angle(longitude)

    if 90 < angle < 270:
        angle += 180

    return angle


# ==========================================================
# КОЛЛИЗИЯ ПЛАНЕТ
# ==========================================================

def spread_radius(index, total, base_radius, step=12):
    """
    Смещает планеты,
    если они стоят слишком близко.
    """

    if total <= 1:
        return base_radius

    center = (total - 1) / 2

    return base_radius + (index - center) * step