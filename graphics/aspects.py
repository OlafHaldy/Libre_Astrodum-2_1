"""
Liber Astrodum
Слой аспектов
Версия 1.0
"""

import math

from graphics.theme import (
    ASPECT_COLORS,
    ASPECT_LINE_WIDTH,
)


class AspectsLayer:
    """
    Рисует аспекты между планетами.
    """

    def __init__(self, renderer):
        self.r = renderer

    def draw(self):
        """
        Отрисовка аспектов.
        """

        if not self.r.chart.aspects:
            return

        # координаты всех планет
        coords = {}

        for planet_name, pdata in self.r.chart.planets.items():

            angle = math.radians(pdata["longitude"] + 180)

            radius = self.r.r_planets

            x = self.r.cx + math.sin(angle) * radius
            y = self.r.cy + math.cos(angle) * radius

            coords[planet_name] = (x, y)

        # сами аспекты
        for aspect in self.r.chart.aspects:

            p1 = aspect["planet1"]
            p2 = aspect["planet2"]

            if p1 not in coords or p2 not in coords:
                continue

            x1, y1 = coords[p1]
            x2, y2 = coords[p2]

            aspect_type = aspect["type"]

            color = ASPECT_COLORS.get(
                aspect_type,
                "#777777"
            )

            self.r._add(
                f"""
<line
x1="{x1:.2f}"
y1="{y1:.2f}"
x2="{x2:.2f}"
y2="{y2:.2f}"
stroke="{color}"
stroke-width="{ASPECT_LINE_WIDTH}"
opacity="0.85"
/>
"""
            )