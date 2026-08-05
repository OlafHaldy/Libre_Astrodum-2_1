"""
Liber Astrodum

graphics/layers/houses.py

Отрисовка куспидов домов.

Версия 1.0
"""

import math

from graphics.theme import GOLD, WHITE


class HousesLayer:

    def __init__(self, renderer):

        self.r = renderer

    # ---------------------------------------------------------

    def draw(self):

        cx = self.r.cx
        cy = self.r.cy

        r_inner = self.r.r_planets
        r_outer = self.r.r_houses

        for house in range(1, 13):

            longitude = self.r.chart.houses[house]["longitude"]

            angle = math.radians(longitude + 180)

            x1 = cx + math.sin(angle) * r_inner
            y1 = cy + math.cos(angle) * r_inner

            x2 = cx + math.sin(angle) * r_outer
            y2 = cy + math.cos(angle) * r_outer

            # ---------------------------------------------
            # Линия куспида
            # ---------------------------------------------

            self.r._add(
                f'''
                <line
                    x1="{x1:.2f}"
                    y1="{y1:.2f}"
                    x2="{x2:.2f}"
                    y2="{y2:.2f}"
                    stroke="{GOLD}"
                    stroke-width="1.3"
                />
                '''
            )

            # ---------------------------------------------
            # Номер дома
            # ---------------------------------------------

            next_house = house + 1 if house < 12 else 1

            lon2 = self.r.chart.houses[next_house]["longitude"]

            span = (lon2 - longitude) % 360

            middle = longitude + span / 2

            angle_mid = math.radians(middle + 180)

            radius = (r_inner + r_outer) / 2

            tx = cx + math.sin(angle_mid) * radius
            ty = cy + math.cos(angle_mid) * radius

            self.r._add(
                f'''
                <text
                    x="{tx:.2f}"
                    y="{ty:.2f}"
                    fill="{WHITE}"
                    font-size="18"
                    text-anchor="middle"
                    dominant-baseline="middle"
                    font-family="Georgia"
                >
                    {house}
                </text>
                '''
            )