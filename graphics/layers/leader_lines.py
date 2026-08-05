"""
Liber Astrodum

Leader Lines Layer

Версия 1.0

Рисует соединительные линии
от подписи планеты к её реальному положению.
"""

import math

from graphics.theme import GOLD


class LeaderLinesLayer:

    def __init__(self, renderer):
        self.r = renderer

    def draw(self, layout):

        for obj in layout:

            # настоящее положение планеты
            angle_planet = math.radians(obj["longitude"] + 180)

            # положение подписи
            angle_label = math.radians(obj["label_angle"] + 180)

            r1 = self.r.r_planets + 12
            r2 = obj["label_radius"] - 10

            x1 = self.r.cx + math.sin(angle_planet) * r1
            y1 = self.r.cy + math.cos(angle_planet) * r1

            x2 = self.r.cx + math.sin(angle_label) * r2
            y2 = self.r.cy + math.cos(angle_label) * r2

            self.r._add(
                f'<line '
                f'x1="{x1:.2f}" '
                f'y1="{y1:.2f}" '
                f'x2="{x2:.2f}" '
                f'y2="{y2:.2f}" '
                f'stroke="{GOLD}" '
                f'stroke-width="0.7" '
                f'opacity="0.75"/>'
            )