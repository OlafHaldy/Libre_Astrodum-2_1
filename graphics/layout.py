"""
Liber Astrodum

graphics/layout.py

Wheel Layout
Версия 3.0

Единая геометрия астрологического колеса.
"""

from dataclasses import dataclass


@dataclass
class WheelLayout:

    width: int
    height: int

    def __post_init__(self):

        # ---------------------------------
        # Центр
        # ---------------------------------

        self.cx = self.width / 2
        self.cy = self.height / 2

        # ---------------------------------
        # Внешний радиус
        # ---------------------------------

        self.radius = min(self.width, self.height) * 0.45

        # ---------------------------------
        # Кольца
        # ---------------------------------

        self.r_outer = self.radius

        self.r_signs = self.radius - 25

        self.r_house_ring = self.radius - 65

        self.r_houses = self.radius - 105

        self.r_planets = self.radius - 145

        self.r_aspects = self.radius - 180

        self.r_center = self.radius - 225

        # ---------------------------------
        # Размеры
        # ---------------------------------

        self.planet_radius = 15

        self.house_font = 18

        self.sign_font = 26

        self.degree_font = 10

        self.aspect_width = 1.4