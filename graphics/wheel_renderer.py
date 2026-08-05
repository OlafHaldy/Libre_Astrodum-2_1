"""
Liber Astrodum
SVG Wheel Renderer
Версия 5.0
"""

from graphics.layout import WheelLayout

from graphics.layers.zodiac import ZodiacLayer
from graphics.layers.houses import HousesLayer
from graphics.layers.planets import PlanetsLayer
from graphics.layers.aspects import AspectsLayer
from graphics.layers.base import BaseLayer
from graphics.layers.zodiac_sectors import ZodiacSectorsLayer
from graphics.layers.house_numbers import HouseNumbersLayer
from graphics.layers.leader_lines import LeaderLinesLayer


class WheelRenderer:

    def __init__(self, chart, width=900, height=900):

        self.chart = chart

        self.layout = WheelLayout(width, height)

        self.width = width
        self.height = height

        self.cx = self.layout.cx
        self.cy = self.layout.cy

        self.r_signs = self.layout.r_signs
        self.r_houses = self.layout.r_houses
        self.r_planets = self.layout.r_planets

        self.elements = []

    # ----------------------------------------------------

    def _add(self, svg):

        self.elements.append(svg)

    # ----------------------------------------------------

    def build(self):

        layers = [

    BaseLayer(self),

    ZodiacSectorsLayer(self),

    ZodiacLayer(self),

    HousesLayer(self),

    HouseNumbersLayer(self),

    AspectsLayer(self),

    LeaderLinesLayer(self),

    PlanetsLayer(self),

]

        ]

        for layer in layers:
            layer.draw()

    # ----------------------------------------------------

    def render(self):

        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {self.width} {self.height}">\n'
            + "\n".join(self.elements)
            + "\n</svg>"
        )


# ============================================================

def draw_wheel(chart):

    renderer = WheelRenderer(chart)

    renderer.build()

    return renderer.render()