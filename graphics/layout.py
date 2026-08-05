"""
Liber Astrodum

graphics/layout.py

Единая геометрия колеса.

Версия 1.0
"""


class WheelLayout:

    def __init__(self, width=900, height=900):

        self.width = width
        self.height = height

        # ------------------------------------
        # Центр
        # ------------------------------------

        self.cx = width / 2
        self.cy = height / 2

        # ------------------------------------
        # Основные радиусы
        # ------------------------------------

        self.r_outer = 430

        self.r_signs = 395

        self.r_houses = 325

        self.r_planets = 255

        self.r_aspects = 215

        self.r_center = 45

        # ------------------------------------
        # Толщина колец
        # ------------------------------------

        self.sign_band = self.r_outer - self.r_signs

        self.house_band = self.r_signs - self.r_houses

        self.planet_band = self.r_houses - self.r_planets

        # ------------------------------------
        # Отступы
        # ------------------------------------

        self.planet_label_offset = 22

        self.house_number_offset = 18

        self.sign_glyph_offset = 20

        # ------------------------------------
        # Линии
        # ------------------------------------

        self.cusp_inner = self.r_planets

        self.cusp_outer = self.r_signs

        self.aspect_radius = self.r_aspects