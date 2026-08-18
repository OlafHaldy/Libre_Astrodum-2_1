"""
Liber Astrodum
core/accidental_dignities.py

Акцидентальные достоинства планет.

Оценивает силу планеты по:
- Дому (угловой, последующий, падающий)
- Ретроградности
- Сожжению (под лучами Солнца)
- Скорости
- Стационарности

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0
"""

# ==========================================================
# КОЭФФИЦИЕНТЫ ДЛЯ ДОМОВ
# ==========================================================

HOUSE_STRENGTH = {
    "angular": 5,      # 1, 4, 7, 10
    "succeedent": 3,   # 2, 5, 8, 11
    "cadent": 1,       # 3, 6, 9, 12
}

ANGULAR_HOUSES = [1, 4, 7, 10]
SUCCEEDENT_HOUSES = [2, 5, 8, 11]
CADENT_HOUSES = [3, 6, 9, 12]


def get_house_type(house_num):
    """Определяет тип дома: angular, succeedent, cadent."""
    if house_num in ANGULAR_HOUSES:
        return "angular"
    elif house_num in SUCCEEDENT_HOUSES:
        return "succeedent"
    elif house_num in CADENT_HOUSES:
        return "cadent"
    return None


# ==========================================================
# СОЖЖЕНИЕ (под лучами Солнца)
# ==========================================================

COMBUSTION_ORB = 8.5  # градусов от Солнца (по Птолемею)
UNDER_BEAMS_ORB = 17  # градусов (под лучами, но не сожжён)


def is_combust(planet_lon, sun_lon, orb=COMBUSTION_ORB):
    """Проверяет, сожжена ли планета."""
    diff = abs((planet_lon - sun_lon) % 360)
    if diff > 180:
        diff = 360 - diff
    return diff <= orb


def is_under_beams(planet_lon, sun_lon, orb=UNDER_BEAMS_ORB):
    """Проверяет, находится ли планета под лучами Солнца."""
    diff = abs((planet_lon - sun_lon) % 360)
    if diff > 180:
        diff = 360 - diff
    return orb < diff <= orb + 5  # условно


# ==========================================================
# СКОРОСТЬ ПЛАНЕТ (относительная)
# ==========================================================

def get_speed_factor(speed):
    """
    Возвращает коэффициент силы по скорости.
    Быстрая планета сильнее, медленная — слабее.
    """
    if speed > 1.0:
        return 2.0   # очень быстрая
    elif speed > 0.5:
        return 1.5   # быстрая
    elif speed > 0:
        return 1.0   # нормальная
    elif speed > -0.5:
        return 0.5   # медленная
    else:
        return 0.0   # очень медленная или стационарная


# ==========================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==========================================================

def build_accidental_dignities(planets, houses):
    """
    Рассчитывает акцидентальные достоинства для всех планет.

    Возвращает dict:
        {
            "Sun": {
                "house_type": "angular",
                "house_strength": 5,
                "retrograde": False,
                "combust": False,
                "under_beams": False,
                "speed_factor": 1.5,
                "total": 6.5,
                "description": "Угловой дом (+5), быстрая (+1.5)"
            },
            ...
        }
    """
    result = {}

    sun_lon = planets.get("Sun", {}).get("longitude", 0)

    for planet_name, planet_data in planets.items():
        house = planet_data.get("house")
        retrograde = planet_data.get("retrograde", False)
        speed = planet_data.get("speed", 0)
        lon = planet_data.get("longitude", 0)

        # 1. Тип дома
        house_type = get_house_type(house) if house else None
        house_strength = HOUSE_STRENGTH.get(house_type, 0)

        # 2. Ретроградность
        retrograde_penalty = -1 if retrograde else 0

        # 3. Сожжение
        combust = False
        under_beams = False
        if planet_name != "Sun":
            combust = is_combust(lon, sun_lon)
            under_beams = is_under_beams(lon, sun_lon)
        combust_penalty = -3 if combust else 0

        # 4. Скорость
        speed_factor = get_speed_factor(speed)

        # 5. Итог
        total = house_strength + retrograde_penalty + combust_penalty + speed_factor

        # 6. Описание
        desc_parts = []
        if house_type:
            desc_parts.append(f"{house_type} дом (+{house_strength})")
        if retrograde:
            desc_parts.append("ретроград (-1)")
        if combust:
            desc_parts.append("сожжена (-3)")
        if speed_factor > 0:
            desc_parts.append(f"скорость ({speed_factor:.1f})")

        result[planet_name] = {
            "house_type": house_type,
            "house_strength": house_strength,
            "retrograde": retrograde,
            "retrograde_penalty": retrograde_penalty,
            "combust": combust,
            "under_beams": under_beams,
            "combust_penalty": combust_penalty,
            "speed_factor": speed_factor,
            "total": round(total, 2),
            "description": ", ".join(desc_parts) if desc_parts else "нейтральная",
        }

    return result