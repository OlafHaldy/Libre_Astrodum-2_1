"""
Liber Astrodum — Professional Lunar Builder
Строит лунарную карту шаг за шагом, с полной диагностикой.
Версия: 5.1 (Professional)
"""

from datetime import datetime, timezone
import swisseph as swe

from core.chart import Chart
from core.location import Location
from core.metadata import ChartMetadata
from core.rulerships import SIGN_RULER
from core.dignities_engine import build_essential_dignities
from core.dispositor import build_dispositor_graph
from core.planet_house_engine import assign_planet_houses

SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
         'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

PLANET_IDS = {
    'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
    'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
    'Saturn': swe.SATURN
}


def build_lunar_chart(natal_moon_longitude, year, month, lat, lon, natal_month=2, natal_day=14):
    """
    Профессиональный построитель лунарной карты.
    Шаг за шагом, с полной диагностикой.
    """
    print("=== [PROFESSIONAL LUNAR BUILDER] ===")
    print(f"[1] Input natal Moon longitude: {natal_moon_longitude:.4f}°")
    print(f"[2] Target month: {year}-{month:02d}")
    print(f"[3] Location (meeting place): lat={lat:.4f}, lon={lon:.4f}")

    # ============================================================
    # Шаг 1: Поиск точного момента возврата Луны
    # Теперь ищем в расширенном интервале: 30 дней до и после
    # запрашиваемого месяца.
    # ============================================================
    import datetime as dt
    target_date = dt.date(year, month, 1)
    start_date = target_date - dt.timedelta(days=30)
    jd_start = swe.julday(start_date.year, start_date.month, start_date.day, 12.0)
    print(f"[4] Starting search from JD {jd_start:.4f} ({start_date} 12:00 UT)")

    DEGREES_PER_DAY = 13.176
    max_iterations = 600  # Увеличим на всякий случай

    for i in range(max_iterations):
        moon_data, _ = swe.calc_ut(jd_start, swe.MOON)
        moon_lon = moon_data[0]
        diff = (natal_moon_longitude - moon_lon + 180) % 360 - 180

        if abs(diff) < 0.0001:
            jd_lunar = jd_start
            print(f"[5] Converged at iteration {i}: JD={jd_lunar:.4f}, diff={diff:.6f}°")
            break

        step_days = diff / DEGREES_PER_DAY
        if abs(step_days) > 5:
            step_days = 5 if step_days > 0 else -5
        jd_start += step_days
    else:
        jd_lunar = jd_start
        print(f"[5] Max iterations reached. Using JD={jd_lunar:.4f}")

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
    print("=== [END PROFESSIONAL BUILD] ===")

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
            if angle <= 8: asp_type = "conjunction"
            elif abs(angle - 60) <= 6: asp_type = "sextile"
            elif abs(angle - 90) <= 7: asp_type = "square"
            elif abs(angle - 120) <= 7: asp_type = "trine"
            elif abs(angle - 180) <= 7: asp_type = "opposition"
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

    return Chart(
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
            engine_version="5.1",
            created_at=datetime.now(timezone.utc).isoformat(),
        ),
    )