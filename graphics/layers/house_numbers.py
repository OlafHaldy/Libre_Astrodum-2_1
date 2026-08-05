"""
Liber Astrodum

House Numbers Layer

Версия 1.0
"""

import math

from graphics.theme import WHITE


class HouseNumbersLayer:

    def __init__(self, renderer):
        self.r = renderer

    def draw(self):

        radius = self.r.r_houses - 35

        for house in range(1, 13):

            cusp1 = self.r.chart.houses[house]["longitude"]

            if house == 12:
                cusp2 = self.r.chart.houses[1]["longitude"] + 360
            else:
                cusp2 = self.r.chart.houses[house + 1]["longitude"]

            middle = (cusp1 + cusp2) / 2

            angle = math.radians(middle + 180)

            x = self.r.cx + math.sin(angle) * radius
            y = self.r.cy + math.cos(angle) * radius

            self.r._add(
                f'<text '
                f'x="{x:.2f}" '
                f'y="{y:.2f}" '
                f'fill="{WHITE}" '
                f'font-size="15" '
                f'font-weight="bold" '
                f'text-anchor="middle">'
                f'{house}'
                f'</text>'
            )