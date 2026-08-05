"""
Liber Astrodum

Сектора знаков Зодиака

Версия 1.0
"""

import math

from graphics.theme import ZODIAC_COLORS


class ZodiacSectorsLayer:

    def __init__(self, renderer):
        self.r = renderer

    def draw(self):

        r_outer = self.r.r_signs
        r_inner = self.r.r_houses

        for i, sign in enumerate([
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces"
        ]):

            start = i * 30
            end = start + 30

            a1 = math.radians(start + 180)
            a2 = math.radians(end + 180)

            x1 = self.r.cx + math.sin(a1) * r_outer
            y1 = self.r.cy + math.cos(a1) * r_outer

            x2 = self.r.cx + math.sin(a2) * r_outer
            y2 = self.r.cy + math.cos(a2) * r_outer

            x3 = self.r.cx + math.sin(a2) * r_inner
            y3 = self.r.cy + math.cos(a2) * r_inner

            x4 = self.r.cx + math.sin(a1) * r_inner
            y4 = self.r.cy + math.cos(a1) * r_inner

            large_arc = 0

            path = (
                f"M {x1:.2f},{y1:.2f} "
                f"A {r_outer},{r_outer} 0 {large_arc} 1 {x2:.2f},{y2:.2f} "
                f"L {x3:.2f},{y3:.2f} "
                f"A {r_inner},{r_inner} 0 {large_arc} 0 {x4:.2f},{y4:.2f} Z"
            )

            self.r._add(
                f'<path d="{path}" '
                f'fill="{ZODIAC_COLORS[sign]}" '
                f'fill-opacity="0.15" '
                f'stroke="none" />'
            )