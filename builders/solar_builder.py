# builders/solar_builder.py

import swisseph as swe
from datetime import datetime, timedelta
from builders.natal_builder import build_natal_chart


def find_solar_return(natal_chart, target_year):
    """
    Находит точный момент возвращения Солнца в натальный градус.
    Возвращает (year, month, day, hour, minute) или None.
    """
    natal_sun_lon = natal_chart.planets['Sun']['longitude']

    # Грубый поиск с шагом 1 день
    start_date = datetime(target_year, 1, 1, 0, 0)
    end_date = datetime(target_year + 1, 1, 1, 0, 0)

    best_diff = float('inf')
    best_jd = None

    current = start_date
    while current < end_date:
        jd = swe.julday(current.year, current.month, current.day, current.hour + current.minute / 60.0)
        sun_pos, _ = swe.calc_ut(jd, swe.SUN)
        sun_lon = sun_pos[0]

        diff = abs((sun_lon - natal_sun_lon) % 360)
        if diff > 180:
            diff = 360 - diff

        if diff < best_diff:
            best_diff = diff
            best_jd = jd

        current += timedelta(days=1)

    if best_jd is None or best_diff > 0.5:
        raise ValueError(f"Solar return not found for year {target_year}")

    # Точный поиск с шагом 1 час
    jd = best_jd - 0.5
    best_diff = float('inf')
    best_jd_final = None

    for _ in range(48):
        sun_pos, _ = swe.calc_ut(jd, swe.SUN)
        sun_lon = sun_pos[0]
        diff = abs((sun_lon - natal_sun_lon) % 360)
        if diff > 180:
            diff = 360 - diff

        if diff < best_diff:
            best_diff = diff
            best_jd_final = jd

        jd += 1.0 / 24.0

    if best_jd_final is None:
        raise ValueError(f"Solar return not found for year {target_year}")

    year, month, day, hour, minute = swe.revjul(best_jd_final)
    return int(year), int(month), int(day), int(hour), int(minute)


def build_solar_chart(natal_data, target_year, lat, lon):
    """
    Строит солярную карту с полной накладкой на натал.

    Возвращает словарь:
        - solar_chart: карта соляра (объект Chart)
        - solar_return_date: дата солярного возвращения
        - solar_asc_ruler: управитель солярного ASC
        - solar_asc_house: дом натала, в который попадает солярный ASC
        - solar_sun_house: дом натала, в который попадает солярное Солнце
        - overlay: накладка солярных планет на натальные дома
    """
    # 1. Строим натал
    natal_chart = build_natal_chart(
        natal_data['year'],
        natal_data['month'],
        natal_data['day'],
        natal_data['hour'],
        natal_data['minute'],
        natal_data['lat'],
        natal_data['lon']
    )

    # 2. Находим момент солярного возвращения
    solar_date = find_solar_return(natal_chart, target_year)

    # 3. Строим солярную карту
    solar_chart = build_natal_chart(
        solar_date[0], solar_date[1], solar_date[2],
        solar_date[3], solar_date[4],
        lat, lon
    )

    # 4. Накладка соляра на натал
    #    Смотрим, в какие натальные дома попадают солярные планеты
    overlay = {}
    for planet_name, planet_data in solar_chart.planets.items():
        planet_lon = planet_data['longitude']
        # Находим натальный дом этой долготы
        for house_num, house_data in natal_chart.houses.items():
            if house_num in [1,2,3,4,5,6,7,8,9,10,11,12]:
                cusp = house_data['longitude']
                next_cusp = natal_chart.houses.get(house_num + 1, {}).get('longitude', cusp + 30)
                if cusp <= planet_lon < next_cusp:
                    overlay[planet_name] = house_num
                    break

    # 5. Управитель солярного ASC
    solar_asc = solar_chart.houses.get(1, {}).get('sign', None)
    solar_asc_ruler = get_ruler_by_sign(solar_asc) if solar_asc else None

    # 6. Дом натала, куда попадает солярный ASC
    solar_asc_house = None
    if solar_asc:
        asc_lon = solar_chart.houses.get(1, {}).get('longitude', 0)
        for house_num, house_data in natal_chart.houses.items():
            if house_num in [1,2,3,4,5,6,7,8,9,10,11,12]:
                cusp = house_data['longitude']
                next_cusp = natal_chart.houses.get(house_num + 1, {}).get('longitude', cusp + 30)
                if cusp <= asc_lon < next_cusp:
                    solar_asc_house = house_num
                    break

    # 7. Дом натала, куда попадает солярное Солнце
    solar_sun_house = None
    sun_lon = solar_chart.planets['Sun']['longitude']
    for house_num, house_data in natal_chart.houses.items():
        if house_num in [1,2,3,4,5,6,7,8,9,10,11,12]:
            cusp = house_data['longitude']
            next_cusp = natal_chart.houses.get(house_num + 1, {}).get('longitude', cusp + 30)
            if cusp <= sun_lon < next_cusp:
                solar_sun_house = house_num
                break

    # 8. Мета-информация
    solar_chart.chart_type = "solar"
    solar_chart.solar_year = target_year
    solar_chart.solar_return_date = f"{solar_date[2]:02d}.{solar_date[1]:02d}.{solar_date[0]} {solar_date[3]:02d}:{solar_date[4]:02d}"
    solar_chart.solar_asc_ruler = solar_asc_ruler
    solar_chart.solar_asc_house = solar_asc_house
    solar_chart.solar_sun_house = solar_sun_house
    solar_chart.overlay = overlay
    solar_chart.natal_chart = natal_chart

    return solar_chart


def get_ruler_by_sign(sign):
    """Возвращает управителя знака (классическая астрология)."""
    rulers = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury',
        'Cancer': 'Moon', 'Leo': 'Sun', 'Virgo': 'Mercury',
        'Libra': 'Venus', 'Scorpio': 'Mars', 'Sagittarius': 'Jupiter',
        'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter'
    }
    return rulers.get(sign)