"""
Liber Astrodum

builders/lunar_builder.py

Построитель лунарной карты на чистом ядре 2.0.
Не зависит от старых модулей (house_rulers, ruler_strength).
Использует только core/ модули.

Автор: Olaf Haldi
Архитектура: Liber Astrodum 2.0
Версия: 2.1
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


def build_lunar_chart(natal_moon_longitude, year, month, lat, lon):
    """Строит лунарную карту на чистом ядре 2.0."""
    
    # 1. Ищем возврат Луны
    jd_start = swe.julday(year, month, 1, 12)
    for _ in range(200):
        moon_data, _ = swe.calc_ut(jd_start, swe.MOON)
        moon_lon = moon_data[0]
        diff = (natal_moon_longitude - moon_lon + 180) % 360 - 180
        if abs(diff) < 0.001:
            break
        jd_start += diff / 13.176

    # 2. Дата возврата
    y, m, d, h_float = swe.revjul(jd_start)
    h = int(h_float)
    minute = int((h_float - h) * 60)
    datetime_str = f"{int(y):04d}-{int(m):02d}-{int(d):02d}T{h:02d}:{minute:02d}:00"

    # 3. Позиции планет
    positions = {}
    for name, pid in PLANET_IDS.items():
        data, _ = swe.calc_ut(jd_start, pid)
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

    # 4. Дома
    cusps, ascmc = swe.houses(jd_start, lat, lon, b'P')
    houses = {}
    for i in range(12):
        lon_cusp = cusps[i]
        sign_num = int(lon_cusp // 30)
        houses[i+1] = {
            "sign": SIGNS[sign_num],
            "degree": round(lon_cusp % 30, 2),
            "longitude": lon_cusp
        }
    for name, idx in [("Ascendant", 0), ("MC", 1)]:
        lon_pt = ascmc[idx]
        sign_num = int(lon_pt // 30)
        houses[name] = {
            "sign": SIGNS[sign_num],
            "degree": round(lon_pt % 30, 2),
            "longitude": lon_pt
        }

    # 5. Планеты в дома
    positions = assign_planet_houses(positions, houses)

    # 6. Аспекты
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

    # 7. Управители домов (на чистом ядре)
    house_rulers = {}
    for h_num in range(1, 13):
        h_sign = houses[h_num]["sign"]
        ruler = SIGN_RULER.get(h_sign)
        if ruler and ruler in positions:
            rd = positions[ruler]
            house_rulers[h_num] = {
                "house": h_num,
                "sign": h_sign,
                "ruler": ruler,
                "ruler_sign": rd.get("sign"),
                "ruler_house": rd.get("house"),
                "ruler_degree": rd.get("degree"),
                "retrograde": rd.get("retrograde", False),
            }

    # 8. Достоинства и диспозиторы
    essential_dignities = build_essential_dignities(positions)
    dispositor_graph = build_dispositor_graph(positions)

    # 9. Сборка Chart
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
            engine_version="2.1",
            created_at=datetime.now(timezone.utc).isoformat(),
        ),
    )