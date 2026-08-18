"""
Liber Astrodum — Professional Lunar Builder
Строит лунарную карту шаг за шагом, с полной диагностикой.
Версия: 7.0 (с накладкой на натал)
"""

from datetime import datetime, timezone
import swisseph as swe

from core.chart import Chart
from core.location import Location
from core.metadata import ChartMetadata
from core.rulerships import SIGN_RULER, get_ruler_by_sign
from core.dignities_engine import build_essential_dignities
from core.dispositor import build_dispositor_graph
from core.planet_house_engine import assign_planet_houses
from builders.natal_builder import build_natal_chart

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN
}

DEGREES_PER_DAY = 13.176
MAX_ITERATIONS = 200


def _find_return(jd_start, natal_moon_longitude):
    """Ищет ближайший возврат Луны от заданного JD."""
    jd = jd_start
    for _ in range(MAX_ITERATIONS):
        moon_data, _ = swe.calc_ut(jd, swe.MOON)
        moon_lon = moon_data[0]
        diff = (natal_moon_longitude - moon_lon + 180) % 360 - 180
        if abs(diff) < 0.0001:
            return jd
        step = diff / DEGREES_PER_DAY
        if abs(step) > 5:
            step = 5 if step > 0 else -5
        jd += step
    return jd


def build_lunar_chart(
    natal_moon_longitude,
    year, month,
    lat, lon,
    natal_month=2,
    natal_day=14,
    natal_year=None,
    natal_hour=12,
    natal_minute=0,
    birth_lat=50.45,
    birth_lon=30.52
):
    """
    Профессиональный построитель лунарной карты.
    Универсальный алгоритм поиска возврата Луны + накладка на натал.
    """
    print("=== [PROFESSIONAL LUNAR BUILDER v7.0] ===")
    print(f"[1] Input natal Moon longitude: {natal_moon_longitude:.4f}°")
    print(f"[2] Target month: {year}-{month:02d}")
    print(f"[3] Location (meeting place): lat={lat:.4f}, lon={lon:.4f}")

    # ============================================================
    # Шаг 1: Поиск возврата Луны, покрывающего указанный месяц
    # ============================================================
    import datetime as dt

    jd_start = swe.julday(year, month, 1, 12.0)
    print(f"[4] Starting search from JD {jd_start:.4f} ({year}-{month:02d}-01 12:00 UT)")

    jd_candidate = _find_return(jd_start, natal_moon_longitude)
    y_ret, m_ret, d_ret, _ = swe.revjul(jd_candidate)
    print(f"[5] First candidate: {int(y_ret)}-{int(m_ret):02d}-{int(d_ret):02d}")

    if m_ret == month and d_ret <= 15:
        jd_lunar = jd_candidate
        print(f"[5] Return covers target month (day <= 15). Using JD={jd_lunar:.4f}")
    elif m_ret < month or (m_ret == month and d_ret <= 15):
        jd_lunar = jd_candidate
        print(f"[5] Return before target month. Using JD={jd_lunar:.4f}")
    else:
        jd_prev = jd_candidate - 27.3
        print(f"[5] Return too late (after 15th). Searching previous from JD={jd_prev:.4f}")
        jd_lunar = _find_return(jd_prev, natal_moon_longitude)

    y_final, m_final, d_final, _ = swe.revjul(jd_lunar)
    print(f"[5] Final return: {int(y_final)}-{int(m_final):02d}-{int(d_final):02d}")

    # ============================================================
    # Шаг 2: Конвертация JD в календарную дату
    # ============================================================
    y, m, d, h_float = swe.revjul(jd_lunar)
    h = int(h_float)
    minute = int((h_float - h) * 60)
    datetime_str = f"{int(y):04d}-{int(m):02d}-{int(d):02d}T{h:02d}:{minute:02d}:00"
    print(f"[6] Lunar Return UT: {datetime_str}")
    print(f"[7] JD: {jd_lunar:.4f}")

    moon_check, _ = swe.calc_ut(jd_lunar, swe.MOON)
    final_diff = (natal_moon_longitude - moon_check[0] + 180) % 360 - 180
    print(f"[8] Final Moon longitude: {moon_check[0]:.4f}°, error: {final_diff:.6f}°")

    # ============================================================
    # Шаг 3: Позиции планет
    # ============================================================
    positions = {}
    print("\n[9] Planet positions:")
    for name, pid in PLANET_IDS.items():
        data, _ = swe.calc_ut(jd_lunar, pid)
        lon = data[0]
        sign_num = int(lon // 30)
        degree = round(lon % 30, 2)
        positions[name] = {
            "sign": SIGNS[sign_num],
            "degree": degree,
            "longitude": lon,
            "speed": 0,
            "house": None,
            "retrograde": False,
        }
        print(f"   {name}: {degree:.2f}° {SIGNS[sign_num]} ({lon:.4f}°)")

    # ============================================================
    # Шаг 4: Дома (Плацидус)
    # ============================================================
    cusps, ascmc = swe.houses(jd_lunar, lat, lon, b'P')
    houses = {}
    print("\n[10] House cusps (Placidus):")
    for i in range(12):
        lon_cusp = cusps[i]
        sign_num = int(lon_cusp // 30)
        houses[i+1] = {
            "sign": SIGNS[sign_num],
            "degree": round(lon_cusp % 30, 2),
            "longitude": lon_cusp
        }
        print(f"    House {i+1}: {round(lon_cusp % 30, 2):.2f}° {SIGNS[sign_num]} ({lon_cusp:.4f}°)")
    for name, idx in [("Ascendant", 0), ("MC", 1)]:
        lon_pt = ascmc[idx]
        sign_num = int(lon_pt // 30)
        houses[name] = {
            "sign": SIGNS[sign_num],
            "degree": round(lon_pt % 30, 2),
            "longitude": lon_pt
        }
        print(f"    {name}: {round(lon_pt % 30, 2):.2f}° {SIGNS[sign_num]} ({lon_pt:.4f}°)")

    # ============================================================
    # Шаг 5: Планеты в дома
    # ============================================================
    positions = assign_planet_houses(positions, houses)
    print("\n[11] Planets in houses:")
    for p in ["Moon", "Saturn", "Sun"]:
        print(f"    {p}: {positions[p]['sign']} → House {positions[p]['house']}")

    # ============================================================
    # Шаг 6: Аспекты, управители, достоинства
    # ============================================================
    aspects = []
    planet_names = list(positions.keys())
    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]
            angle = abs(positions[p1]["longitude"] - positions[p2]["longitude"])
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
                    "planet1": p1, "planet2": p2,
                    "type": asp_type, "angle": round(angle, 2)
                })

    house_rulers = {}
    for h_num in range(1, 13):
        h_sign = houses[h_num]["sign"]
        ruler = SIGN_RULER.get(h_sign)
        if ruler and ruler in positions:
            rd = positions[ruler]
            house_rulers[h_num] = {
                "house": h_num, "sign": h_sign, "ruler": ruler,
                "ruler_sign": rd.get("sign"), "ruler_house": rd.get("house"),
                "ruler_degree": rd.get("degree"), "retrograde": rd.get("retrograde", False),
            }

    essential_dignities = build_essential_dignities(positions)
    dispositor_graph = build_dispositor_graph(positions)

    # ============================================================
    # Шаг 7: Накладка на натал (НОВОЕ)
    # ============================================================
    overlay = {}
    lunar_asc_ruler = None
    lunar_asc_house = None
    lunar_moon_house = None
    angular_planets = []

    if natal_year and natal_month and natal_day:
        natal_chart = build_natal_chart(
            natal_year, natal_month, natal_day,
            natal_hour, natal_minute,
            birth_lat, birth_lon
        )

        # Накладка лунарных планет на натальные дома
        for planet_name, planet_data in positions.items():
            planet_lon = planet_data['longitude']
            for house_num, house_data in natal_chart.houses.items():
                if isinstance(house_num, int) and 1 <= house_num <= 12:
                    cusp = house_data['longitude']
                    next_cusp = natal_chart.houses.get(house_num + 1, {}).get('longitude', cusp + 30)
                    if cusp <= planet_lon < next_cusp:
                        overlay[planet_name] = house_num
                        break

        # Управитель лунарного ASC
        lunar_asc_sign = houses.get('Ascendant', {}).get('sign', None)
        lunar_asc_ruler = get_ruler_by_sign(lunar_asc_sign) if lunar_asc_sign else None

        # Дом натала для лунарного ASC
        asc_lon = houses.get('Ascendant', {}).get('longitude', 0)
        for house_num, house_data in natal_chart.houses.items():
            if isinstance(house_num, int) and 1 <= house_num <= 12:
                cusp = house_data['longitude']
                next_cusp = natal_chart.houses.get(house_num + 1, {}).get('longitude', cusp + 30)
                if cusp <= asc_lon < next_cusp:
                    lunar_asc_house = house_num
                    break

        # Дом натала для лунарной Луны
        moon_lon = positions.get('Moon', {}).get('longitude', 0)
        for house_num, house_data in natal_chart.houses.items():
            if isinstance(house_num, int) and 1 <= house_num <= 12:
                cusp = house_data['longitude']
                next_cusp = natal_chart.houses.get(house_num + 1, {}).get('longitude', cusp + 30)
                if cusp <= moon_lon < next_cusp:
                    lunar_moon_house = house_num
                    break

        # Планеты в угловых домах натала
        for planet, house in overlay.items():
            if house in [1, 4, 7, 10]:
                angular_planets.append(f"{planet} в {house} доме")

        print("\n[12] Lunar overlay on natal:")
        print(f"    Lunar ASC ruler: {lunar_asc_ruler}")
        print(f"    Lunar ASC in natal house: {lunar_asc_house}")
        print(f"    Lunar Moon in natal house: {lunar_moon_house}")
        print(f"    Angular planets: {', '.join(angular_planets) if angular_planets else 'none'}")
        print("=== [END PROFESSIONAL BUILD] ===")

    # ============================================================
    # Шаг 8: Создание Chart
    # ============================================================
    chart = Chart(
        chart_type="lunar",
        datetime_str=datetime_str,
        location=Location(lat=lat, lon=lon),
        planets=positions,
        houses=houses,
        aspects=aspects,
        house_rulers=house_rulers,
        essential_dignities=essential_dignities,
        dispositor_graph=dispositor_graph,
        metadata=ChartMetadata(
            engine_version="7.0",
            created_at=datetime.now(timezone.utc).isoformat(),
        ),
    )

    # Добавляем данные накладки в Chart
    chart.lunar_asc_ruler = lunar_asc_ruler
    chart.lunar_asc_house = lunar_asc_house
    chart.lunar_moon_house = lunar_moon_house
    chart.overlay = overlay
    chart.angular_planets = angular_planets

    return chart