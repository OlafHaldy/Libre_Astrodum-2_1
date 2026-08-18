"""
Liber Astrodum

builders/natal_builder.py

Построитель натальной карты на чистом ядре 2.0.

Автор: Olaf Haldi
Архитектура: Liber Astrodum 2.0
Версия: 2.0
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


def build_natal_chart(year, month, day, hour, minute, lat, lon):
    """Строит натальную карту."""
    
    # 1. JD рождения
    jd_natal = swe.julday(year, month, day, hour + minute / 60.0)
    datetime_str = f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"

    # 2. Позиции планет
    positions = {}

    for name, pid in PLANET_IDS.items():
        data, _ = swe.calc_ut(jd_natal, pid)
        planet_lon = data[0]
        sign_num = int(planet_lon // 30)
        degree = round(planet_lon % 30, 2)

        positions[name] = {
            "sign": SIGNS[sign_num],
            "degree": degree,
            "longitude": planet_lon,
            "speed": data[3],
            "house": None,
            "retrograde": data[3] < 0,
        }

    # 3. Дома
    cusps, ascmc = swe.houses(jd_natal, lat, lon, b'P')
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

    # 4. Планеты в дома
    positions = assign_planet_houses(positions, houses)

    # 5. Аспекты
    aspects = []
    planet_names = list(positions.keys())

    EXACT_ANGLES = {
        "conjunction": 0,
        "sextile": 60,
        "square": 90,
        "trine": 120,
        "opposition": 180,
    }

    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1, p2 = planet_names[i], planet_names[j]

            angle = abs(
                positions[p1]["longitude"] -
                positions[p2]["longitude"]
            )

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
                exact_angle = EXACT_ANGLES[asp_type]
                orb = abs(angle - exact_angle)

                aspects.append({
                    "planet1": p1,
                    "planet2": p2,
                    "type": asp_type,
                    "angle": round(angle, 2),
                    "orb": round(orb, 2),
                })

    # 6. Управители домов
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

    # 7. Достоинства и диспозиторы
    essential_dignities = build_essential_dignities(positions)
    dispositor_graph = build_dispositor_graph(positions)

    # 8. Сборка Chart
    return Chart(
        chart_type="natal",
        datetime_str=datetime_str,
        location=Location(lat=lat, lon=lon),
        planets=positions,
        houses=houses,
        aspects=aspects,
        house_rulers=house_rulers,
        essential_dignities=essential_dignities,
        dispositor_graph=dispositor_graph,
        metadata=ChartMetadata(
            engine_version="2.0",
            created_at=datetime.now(timezone.utc).isoformat(),
        ),
    )