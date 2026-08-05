"""
Liber Astrodum
Слой аспектов

Версия 1.0
"""

import math

# Цвета аспектов
ASPECT_COLORS = {
    "conjunction": "#ffffff",
    "sextile": "#3cb371",
    "square": "#ff4040",
    "trine": "#4a90e2",
    "opposition": "#ff8c00",
}

# Толщина линий
ASPECT_WIDTH = {
    "conjunction": 2.2,
    "sextile": 1.3,
    "square": 1.5,
    "trine": 1.5,
    "opposition": 1.8,
}


class AspectsLayer:

    def __init__(self, renderer):
        self.r = renderer

    def draw(self):

        radius = self.r.r_planets

        for aspect in self.r.chart.aspects:

            p1 = self.r.chart.planets[aspect["planet1"]]
            p2 = self.r.chart.planets[aspect["planet2"]]

            lon1 = p1["longitude"]
            lon2 = p2["longitude"]

            a1 = math.radians(lon1 + 180)
            a2 = math.radians(lon2 + 180)

            x1 = self.r.cx + math.sin(a1) * radius
            y1 = self.r.cy + math.cos(a1) * radius

            x2 = self.r.cx + math.sin(a2) * radius
            y2 = self.r.cy + math.cos(a2) * radius

            aspect_type = aspect["type"]

            color = ASPECT_COLORS.get(aspect_type, "#888888")
            width = ASPECT_WIDTH.get(aspect_type, 1)

            self.r._add(
                f'<line '
                f'x1="{x1:.2f}" '
                f'y1="{y1:.2f}" '
                f'x2="{x2:.2f}" '
                f'y2="{y2:.2f}" '
                f'stroke="{color}" '
                f'stroke-width="{width}" '
                f'opacity="0.9" />'
            )