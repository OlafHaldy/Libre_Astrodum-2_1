"""
Liber Astrodum
graphics/houses.py

Отрисовка системы домов.

Версия 3.0
"""

from graphics.theme import (
    GOLD,
    WHITE,
    HOUSE_RING,
    SIGN_RING_OUTER,
    FONT_NORMAL,
)

from graphics.geometry import (
    polar_to_cartesian,
    midpoint,
)


class HousesLayer:

    def __init__(self, renderer):
        self.r = renderer

    # ======================================================
    # Главная функция
    # ======================================================

    def draw(self):

        self.draw_house_lines()

        self.draw_house_numbers()

        self.draw_angles()

    # ======================================================
    # Линии домов
    # ======================================================

    def draw_house_lines(self):

        for house in range(1, 13):

            cusp = self.r.chart.houses[house]["longitude"]

            x1, y1 = polar_to_cartesian(
                self.r.cx,
                self.r.cy,
                HOUSE_RING,
                cusp,
            )

            x2, y2 = polar_to_cartesian(
                self.r.cx,
                self.r.cy,
                SIGN_RING_OUTER,
                cusp,
            )

            self.r._add(f"""
<line
x1="{x1:.2f}"
y1="{y1:.2f}"
x2="{x2:.2f}"
y2="{y2:.2f}"
stroke="{GOLD}"
stroke-width="1"/>
""")

    # ======================================================
    # Номера домов
    # ======================================================

    def draw_house_numbers(self):

        for house in range(1, 13):

            current = self.r.chart.houses[house]["longitude"]

            if house == 12:
                nxt = self.r.chart.houses[1]["longitude"] + 360
            else:
                nxt = self.r.chart.houses[house + 1]["longitude"]

            middle = midpoint(current, nxt)

            x, y = polar_to_cartesian(
                self.r.cx,
                self.r.cy,
                HOUSE_RING - 28,
                middle,
            )

            self.r._add(f"""
<text
x="{x:.2f}"
y="{y:.2f}"
fill="{WHITE}"
font-size="{FONT_NORMAL}"
font-family="Georgia"
text-anchor="middle"
dominant-baseline="middle">
{house}
</text>
""")

    # ======================================================
    # ASC / DSC / MC / IC
    # ======================================================

    def draw_angles(self):

        points = {
            "ASC": self.r.chart.houses["Ascendant"]["longitude"],
            "MC": self.r.chart.houses["MC"]["longitude"],
            "DSC": (self.r.chart.houses["Ascendant"]["longitude"] + 180) % 360,
            "IC": (self.r.chart.houses["MC"]["longitude"] + 180) % 360,
        }

        for label, lon in points.items():

            x, y = polar_to_cartesian(
                self.r.cx,
                self.r.cy,
                SIGN_RING_OUTER + 18,
                lon,
            )

            self.r._add(f"""
<text
x="{x:.2f}"
y="{y:.2f}"
fill="{WHITE}"
font-size="18"
font-family="Georgia"
font-weight="bold"
text-anchor="middle"
dominant-baseline="middle">
{label}
</text>
""")