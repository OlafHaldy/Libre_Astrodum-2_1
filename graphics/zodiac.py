"""
Liber Astrodum
graphics/zodiac.py

Отрисовка кольца Зодиака.

Версия 3.0
"""

from graphics.theme import (
    GOLD,
    WHITE,
    ZODIAC_COLORS,
    SIGN_RING_OUTER,
    SIGN_RING_INNER,
    FONT_NORMAL,
)

from graphics.geometry import (
    polar_to_cartesian,
    describe_arc,
    midpoint,
)

# Unicode-символы знаков
ZODIAC_SYMBOLS = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓",
}

# Порядок знаков
ZODIAC_ORDER = [
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
    "Pisces",
]


class ZodiacLayer:

    def __init__(self, renderer):
        self.r = renderer

    def draw(self):

        self.draw_sectors()

        self.draw_symbols()

    # =======================================================
    # СЕКТОРА
    # =======================================================

    def draw_sectors(self):

        for i, sign in enumerate(ZODIAC_ORDER):

            start = i * 30

            end = start + 30

            path = describe_arc(
                self.r.cx,
                self.r.cy,
                SIGN_RING_OUTER,
                start,
                end,
            )

            self.r._add(
                f'''
<path d="{path}"
fill="none"
stroke="{GOLD}"
stroke-width="1.2"/>
'''
            )

            inner = describe_arc(
                self.r.cx,
                self.r.cy,
                SIGN_RING_INNER,
                start,
                end,
            )

            self.r._add(
                f'''
<path d="{inner}"
fill="none"
stroke="{GOLD}"
stroke-width="1"/>
'''
            )

    # =======================================================
    # СИМВОЛЫ
    # =======================================================

    def draw_symbols(self):

        radius = (SIGN_RING_OUTER + SIGN_RING_INNER) / 2

        for i, sign in enumerate(ZODIAC_ORDER):

            lon = i * 30 + 15

            x, y = polar_to_cartesian(
                self.r.cx,
                self.r.cy,
                radius,
                lon,
            )

            color = ZODIAC_COLORS.get(sign, WHITE)

            symbol = ZODIAC_SYMBOLS[sign]

            self.r._add(
                f'''
<text
x="{x:.2f}"
y="{y:.2f}"
fill="{color}"
font-size="26"
font-family="DejaVu Sans"
text-anchor="middle"
dominant-baseline="middle">
{symbol}
</text>
'''
            )

            # Подпись знака

            x2, y2 = polar_to_cartesian(
                self.r.cx,
                self.r.cy,
                radius - 32,
                lon,
            )

            self.r._add(
                f'''
<text
x="{x2:.2f}"
y="{y2:.2f}"
fill="{WHITE}"
font-size="{FONT_NORMAL}"
font-family="Georgia"
text-anchor="middle"
dominant-baseline="middle">
{sign}
</text>
'''
            )