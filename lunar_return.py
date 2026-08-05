"""
Liber Astrodum

Модуль Лунара (Lunar Return).

Вычисляет точный момент возвращения Луны
в своё натальное положение и строит карту на месяц.
"""

import swisseph as swe


def find_lunar_return(natal_moon_longitude, year, month, day, hour=12, max_iterations=200):
    """
    Находит точный момент (JD) возвращения Луны.
    Использует swe.mooncross_ut для высокой точности.
    """
    # Начинаем поиск с 1-го числа указанного месяца в 12:00 UT
    jd_start = swe.julday(year, month, day, hour)
        print(f"DEBUG mooncross_ut: jd_lunar = {jd_lunar}")
    # swe.mooncross_ut ищет ближайшее пересечение Луной заданной долготы
    # Возвращает JD этого пересечения
    serr = ''
    jd_lunar = swe.mooncross_ut(natal_moon_longitude, jd_start, 0, serr)
    
    # Если пересечение не найдено, возвращаемся к итеративному методу
    if jd_lunar == 0 or jd_lunar < jd_start - 30:
        # Итеративный поиск как запасной вариант
        DEGREES_PER_DAY = 13.176
        for _ in range(max_iterations):
            moon_data, _ = swe.calc_ut(jd_start, swe.MOON)
            moon_lon = moon_data[0]
            diff = (natal_moon_longitude - moon_lon + 180) % 360 - 180
            if abs(diff) < 0.001:
                return jd_start
            jd_start += diff / DEGREES_PER_DAY
        return jd_start
    
    return jd_lunar


def calculate_lunar_return(natal_moon_longitude, year, month, day, hour=12, lat=50.45, lon=30.52):
    """
    Вычисляет полную карту Лунара на ближайший месяц.

    Возвращает объект с положениями планет, домами, аспектами и темами месяца.
    """
    # Находим точный JD возвращения
    jd_lunar = find_lunar_return(natal_moon_longitude, year, month, day, hour)

    # Конвертируем JD в календарную дату
    year_lunar, month_lunar, day_lunar, hour_float = swe.revjul(jd_lunar)
    hour_lunar = int(hour_float)
    minute_lunar = int((hour_float - hour_lunar) * 60)

    # Строим карту на момент Лунара
    planets = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
        'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN, 'Uranus': swe.URANUS, 'Neptune': swe.NEPTUNE,
        'Pluto': swe.PLUTO, 'True Node': swe.TRUE_NODE, 'Chiron': swe.CHIRON,
    }
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

    positions = {}
    for name, pid in planets.items():
        data, _ = swe.calc_ut(jd_lunar, pid)
        lon = data[0]
        sign_num = int(lon // 30)
        degree = round(lon % 30, 2)
        positions[name] = {
            "sign": signs[sign_num],
            "degree": degree,
            "longitude": lon
        }

    # Дома на момент Лунара
    cusps, ascmc = swe.houses(jd_lunar, lat, lon, b'P')
    houses = {}
    for i in range(12):
        lon_cusp = cusps[i]
        sign_num = int(lon_cusp // 30)
        degree = round(lon_cusp % 30, 2)
        houses[i+1] = {
            "sign": signs[sign_num],
            "degree": degree,
            "longitude": lon_cusp
        }
    for name, index in [("Ascendant", 0), ("MC", 1)]:
        lon_point = ascmc[index]
        sign_num = int(lon_point // 30)
        degree = round(lon_point % 30, 2)
        houses[name] = {
            "sign": signs[sign_num],
            "degree": degree,
            "longitude": lon_point
        }

    # Аспекты
    aspects = []
    planet_names = list(positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            lon1, lon2 = positions[p1]["longitude"], positions[p2]["longitude"]
            angle = abs(lon1 - lon2)
            if angle > 180:
                angle = 360 - angle

            asp_type = None
            if angle <= 8:
                asp_type = "conjunction"
            elif abs(angle - 60) <= 6:
                asp_type = "sextile"
            elif abs(angle - 90) <= 7:
                asp_type = "square"
            elif abs(angle - 120) <= 7:
                asp_type = "trine"
            elif abs(angle - 180) <= 7:
                asp_type = "opposition"

            if asp_type:
                aspects.append({
                    "planet1": p1,
                    "planet2": p2,
                    "type": asp_type,
                    "angle": round(angle, 2)
                })

    # Хранители домов
    from house_rulers import build_house_rulers
    house_rulers = build_house_rulers(houses, positions)

    return {
        "date": f"{int(year_lunar):04d}-{int(month_lunar):02d}-{int(day_lunar):02d}",
        "time": f"{hour_lunar:02d}:{minute_lunar:02d}",
        "jd": jd_lunar,
        "positions": positions,
        "houses": houses,
        "aspects": aspects,
        "house_rulers": house_rulers,
    }