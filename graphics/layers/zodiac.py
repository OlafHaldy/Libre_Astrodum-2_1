"""
Liber Astrodum
Слой знаков Зодиака
Версия 1.0
"""

import math

from graphics.theme import GOLD, WHITE
from graphics.glyphs import ZODIAC_GLYPHS, ZODIAC_NAMES


class ZodiacLayer:

    def __init__(self, renderer):
        self.r = renderer

    def draw(self):

        radius = self.r.r_signs + 18

        signs = [
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
        ]

        for i, sign in enumerate(signs):

            # центр каждого знака
            longitude = i * 30 + 15

            angle = math.radians(longitude + 180)

            x = self.r.cx + math.sin(angle) * radius
            y = self.r.cy + math.cos(angle) * radius

            glyph = ZODIAC_GLYPHS[sign]
            name = ZODIAC_NAMES[sign]

            # символ знака
            self.r._add(
                f'<text '
                f'x="{x:.2f}" '
                f'y="{y:.2f}" '
                f'font-size="22" '
                f'fill="{GOLD}" '
                f'text-anchor="middle">'
                f'{glyph}'
                f'</text>'
            )

            # русское название
            self.r._add(
                f'<text '
                f'x="{x:.2f}" '
                f'y="{y+20:.2f}" '
                f'font-size="10" '
                f'fill="{WHITE}" '
                f'text-anchor="middle">'
                f'{name}'
                f'</text>'
            )