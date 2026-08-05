"""
Liber Astrodum
Layer: Planets

Версия 2.0
Часть 1

Подготовка данных планет.
"""

from dataclasses import dataclass
import math

from graphics.theme import WHITE


# ==========================================================
# ГЛИФЫ
# ==========================================================

PLANET_GLYPHS = {

    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
    "Chiron": "⚷",
    "North Node": "☊",
    "South Node": "☋",

}


# ==========================================================
# ЦВЕТА ПЛАНЕТ
# ==========================================================

PLANET_COLORS = {

    "Sun": "#FFD700",
    "Moon": "#E6E6E6",

    "Mercury": "#F8F8F8",

    "Venus": "#7CFC00",

    "Mars": "#FF4040",

    "Jupiter": "#C070FF",

    "Saturn": "#B0B0B0",

    "Uranus": "#55CCFF",

    "Neptune": "#3F7FFF",

    "Pluto": "#A00040",

    "Chiron": "#00CED1",

    "North Node": "#FFFFFF",

    "South Node": "#AAAAAA",

}


# ==========================================================
# ОПИСАНИЕ ПЛАНЕТЫ
# ==========================================================

@dataclass
class PlanetNode:

    name: str

    glyph: str

    color: str

    longitude: float

    sign: str

    degree: float

    retrograde: bool

    x: float = 0.0
    y: float = 0.0

    draw_x: float = 0.0
    draw_y: float = 0.0

    group: int = -1


# ==========================================================
# LAYER
# ==========================================================

class PlanetsLayer:

    def __init__(self, renderer):

        self.r = renderer

        self.planets = []

    # ------------------------------------------------------
    # Главная функция слоя
    # ------------------------------------------------------

    def draw(self):

        self._collect_planets()

        self._calculate_positions()

        self._resolve_collisions()

        self._draw_planets()

    # ------------------------------------------------------
    # Считывание планет из Chart
    # ------------------------------------------------------

    def _collect_planets(self):

        self.planets = []

        for name, data in self.r.chart.planets.items():

            node = PlanetNode(

                name=name,

                glyph=PLANET_GLYPHS.get(name, "?"),

                color=PLANET_COLORS.get(name, WHITE),

                longitude=data["longitude"],

                sign=data["sign"],

                degree=data["degree"],

                retrograde=data.get("retrograde", False)

            )

            self.planets.append(node)

    # ------------------------------------------------------
    # Геометрия
    # ------------------------------------------------------

    def _calculate_positions(self):

        radius = self.r.r_planets

        for node in self.planets:

            angle = math.radians(node.longitude + 180)

            node.x = self.r.cx + math.sin(angle) * radius
            node.y = self.r.cy + math.cos(angle) * radius

            node.draw_x = node.x
            node.draw_y = node.y

        # ------------------------------------------------------
    # Поиск близко расположенных планет
    # ------------------------------------------------------

    def _resolve_collisions(self):

        groups = self._group_planets()

        for group in groups:

            if len(group) == 1:
                continue

            self._offset_group(group)

    # ------------------------------------------------------
    # Группировка
    # ------------------------------------------------------

    def _group_planets(self):

        tolerance = 8.0      # градусов

        planets = sorted(
            self.planets,
            key=lambda p: p.longitude
        )

        groups = []

        current = []

        for planet in planets:

            if not current:

                current.append(planet)

                continue

            prev = current[-1]

            diff = abs(planet.longitude - prev.longitude)

            if diff > 180:
                diff = 360 - diff

            if diff <= tolerance:

                current.append(planet)

            else:

                groups.append(current)

                current = [planet]

        if current:
            groups.append(current)

        return groups

    # ------------------------------------------------------
    # Разведение группы
    # ------------------------------------------------------

    def _offset_group(self, group):

        spacing = 22

        center = (len(group) - 1) / 2

        for i, planet in enumerate(group):

            angle = math.radians(planet.longitude + 180)

            tangent_x = math.cos(angle)
            tangent_y = -math.sin(angle)

            shift = (i - center) * spacing

            planet.draw_x = planet.x + tangent_x * shift
            planet.draw_y = planet.y + tangent_y * shift

        # ------------------------------------------------------
    # Отрисовка всех планет
    # ------------------------------------------------------

    def _draw_planets(self):

        for planet in self.planets:

            moved = (
                abs(planet.draw_x - planet.x) > 0.1
                or
                abs(planet.draw_y - planet.y) > 0.1
            )

            if moved:
                self._draw_leader(planet)

            self._draw_planet(planet)

    # ------------------------------------------------------

    def _draw_leader(self, planet):

        self.r._add(

            f'''
            <line

                x1="{planet.x:.2f}"
                y1="{planet.y:.2f}"

                x2="{planet.draw_x:.2f}"
                y2="{planet.draw_y:.2f}"

                stroke="#888888"
                stroke-width="1"

            />
            '''

        )

    # ------------------------------------------------------

    def _draw_planet(self, planet):

        radius = 15

        #
        # Кружок
        #

        self.r._add(

            f'''
            <circle

                cx="{planet.draw_x:.2f}"
                cy="{planet.draw_y:.2f}"

                r="{radius}"

                fill="#2b2b2b"

                stroke="{planet.color}"

                stroke-width="2"

            />
            '''

        )

        #
        # Глиф
        #

        self.r._add(

            f'''
            <text

                x="{planet.draw_x:.2f}"
                y="{planet.draw_y+1:.2f}"

                fill="{planet.color}"

                font-size="20"

                font-family="DejaVu Sans"

                text-anchor="middle"

                dominant-baseline="middle"

            >

            {planet.glyph}

            </text>
            '''

        )

        #
        # Ретроградность
        #

        if planet.retrograde:

            self.r._add(

                f'''
                <text

                    x="{planet.draw_x+13:.2f}"
                    y="{planet.draw_y-12:.2f}"

                    fill="#ff6666"

                    font-size="10"

                    font-family="DejaVu Sans"

                >

                ℞

                </text>
                '''

            )

        #
        # Градусы
        #

        self._draw_degree(
    planet.draw_x,
    planet.draw_y + 24,
    planet.degree
)
		    # ------------------------------------------------------
    # Подпись градусов
    # ------------------------------------------------------

    def _draw_degree(self, x, y, degree):

        text = f"{degree:.1f}°"

        self.r._add(

            f'''
            <text

                x="{x:.2f}"

                y="{y:.2f}"

                fill="#ffffff"

                font-size="10"

                text-anchor="middle"

                font-family="Segoe UI Symbol, Noto Sans Symbols, Arial Unicode MS"

            >

            {text}

            </text>
            '''

        )