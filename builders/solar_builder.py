import swisseph as swe
from datetime import datetime, timedelta
from builders.natal_builder import build_natal_chart
from core.rulerships import get_ruler_by_sign


def find_solar_return(natal_chart, target_year):
    """
    Находит точный момент возвращения Солнца в натальный градус.
    Возвращает (year, month, day, hour, minute) или None.
    """
    natal_sun_lon = natal_chart.planets['Sun']['longitude']

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

    # Исправлено: revjul возвращает 4 значения, а не 5
    year, month, day, hour = swe.revjul(best_jd_final)
    return int(year), int(month), int(day), int(hour), 0


def build_solar_chart(natal_data, target_year, lat, lon):
    """
    Строит солярную карту с полной накладкой на натал.
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
    overlay = {}
    for planet_name, planet_data in solar_chart.planets.items():
        planet_lon = planet_data['longitude']
        for house_num, house_data in natal_chart.houses.items():
            if isinstance(house_num, int) and 1 <= house_num <= 12:
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
            if isinstance(house_num, int) and 1 <= house_num <= 12:
                cusp = house_data['longitude']
                next_cusp = natal_chart.houses.get(house_num + 1, {}).get('longitude', cusp + 30)
                if cusp <= asc_lon < next_cusp:
                    solar_asc_house = house_num
                    break

    # 7. Дом натала, куда попадает солярное Солнце
    solar_sun_house = None
    sun_lon = solar_chart.planets['Sun']['longitude']
    for house_num, house_data in natal_chart.houses.items():
        if isinstance(house_num, int) and 1 <= house_num <= 12:
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