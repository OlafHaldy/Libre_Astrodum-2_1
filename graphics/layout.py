"""
Liber Astrodum

graphics/layout.py

Автоматическое размещение подписей планет.

Версия 2.0
"""

import math


class PlanetLayout:

    BASE_RADIUS = 245

    RADIUS_STEP = 18

    GROUP_DISTANCE = 7.0

    FAN_STEP = 4.0

    def __init__(self, planets):

        self.planets = planets

    # ---------------------------------------------------------

    @staticmethod
    def normalize(angle):
        return angle % 360

    # ---------------------------------------------------------

    @staticmethod
    def circular_difference(a, b):

        d = (b - a + 180) % 360 - 180
        return d

    # ---------------------------------------------------------

    def group_planets(self):

        planets = sorted(
            self.planets,
            key=lambda p: p["longitude"]
        )

        groups = []

        current = []

        for planet in planets:

            if not current:
                current.append(planet)
                continue

            prev = current[-1]

            diff = abs(
                self.circular_difference(
                    prev["longitude"],
                    planet["longitude"]
                )
            )

            if diff <= self.GROUP_DISTANCE:

                current.append(planet)

            else:

                groups.append(current)
                current = [planet]

        if current:
            groups.append(current)

        return groups

    # ---------------------------------------------------------

    def build(self):

        result = []

        groups = self.group_planets()

        for group in groups:

            # -----------------------------
            # Одиночная планета
            # -----------------------------

            if len(group) == 1:

                p = dict(group[0])

                p["label_angle"] = self.normalize(
                    p["longitude"]
                )

                p["label_radius"] = self.BASE_RADIUS

                result.append(p)

                continue

            # -----------------------------
            # Центр группы
            # -----------------------------

            center = sum(
                p["longitude"] for p in group
            ) / len(group)

            n = len(group)

            start = center - self.FAN_STEP * (n - 1) / 2

            for i, planet in enumerate(group):

                p = dict(planet)

                p["label_angle"] = self.normalize(
                    start + i * self.FAN_STEP
                )

                p["label_radius"] = (
                    self.BASE_RADIUS
                    + i * self.RADIUS_STEP
                )

                result.append(p)

        result.sort(
            key=lambda p: p["longitude"]
        )

        return result