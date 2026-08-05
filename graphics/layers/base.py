"""
Liber Astrodum
Layer: Base

Фон и основные окружности колеса.
"""

from graphics.theme import BACKGROUND, GOLD


class BaseLayer:

    def __init__(self, renderer):
        self.r = renderer

    # ------------------------------------------------------

    def draw(self):

        self._draw_background()
        self._draw_circles()

    # ------------------------------------------------------

    def _draw_background(self):

        self.r._add(
            f'''
            <rect

                width="{self.r.width}"
                height="{self.r.height}"

                fill="{BACKGROUND}"

            />
            '''
        )

    # ------------------------------------------------------

    def _draw_circles(self):

        radii = [

            self.r.r_signs,
            self.r.r_houses,
            self.r.r_planets,

        ]

        for radius in radii:

            self.r._add(

                f'''
                <circle

                    cx="{self.r.cx}"
                    cy="{self.r.cy}"

                    r="{radius}"

                    fill="none"

                    stroke="{GOLD}"

                    stroke-width="1.5"

                />
                '''

            )