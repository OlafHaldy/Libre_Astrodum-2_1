"""
Liber Astrodum
graphics/planets.py

Отрисовка планет.

Версия 3.0
"""

from graphics.theme import (
    GOLD,
    WHITE,
    PLANET_RING,
)

from graphics.geometry import polar_to_cartesian

# Unicode-символы планет
PLANET_SYMBOLS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    "Chiron": "⚷",
    "North Node": "☊",
    "South Node": "☋",
    "Lilith": "⚸",
}


class PlanetsLayer:

    def __init__(self, renderer):
        self.r = renderer

    # ===================================================
    # Главная функция
    # ===================================================

    def draw(self):

        self.draw_planets()

    # ===================================================
    # Планеты
    # ===================================================

    def draw_planets(self):

        for planet, data in self.r.chart.planets.items():

            lon = data["longitude"]

            # настоящая позиция планеты
            x0, y0 = polar_to_cartesian(
                self.r.cx,
                self.r.cy,
                PLANET_RING - 18,
                lon,
            )

            # место отображения символа
            x, y = polar_to_cartesian(
                self.r.cx,
                self.r.cy,
                PLANET_RING,
                lon,
            )

            # соединительная линия

            self.r._add(f"""
<line
x1="{x0:.2f}"
y1="{y0:.2f}"
x2="{x:.2f}"
y2="{y:.2f}"
stroke="{GOLD}"
stroke-width="0.8"/>
""")

            # круг

            self.r._add(f"""
<circle
cx="{x:.2f}"
cy="{y:.2f}"
r="12"
fill="#222222"
stroke="{GOLD}"
stroke-width="1.3"/>
""")

            symbol = PLANET_SYMBOLS.get(planet, planet[:2])

            # символ планеты

            self.r._add(f"""
<text
x="{x:.2f}"
y="{y:.2f}"
fill="{WHITE}"
font-size="18"
font-family="DejaVu Sans"
text-anchor="middle"
dominant-baseline="middle">
{symbol}
</text>
""")

            # градус

            degree = round(data["degree"], 1)

            self.r._add(f"""
<text
x="{x:.2f}"
y="{y + 22:.2f}"
fill="{WHITE}"
font-size="9"
font-family="Georgia"
text-anchor="middle">
{degree}°
</text>
""")