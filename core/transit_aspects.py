"""
Liber Astrodum
core/transit_aspects.py

Транзитные аспекты к натальной карте.

Вычисляет аспекты между транзитными планетами и натальными.
Используется для прогнозов (Соляр, Лунар, Daily).

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 3.0
"""

# ==========================================================
# КОНФИГУРАЦИЯ ОРБИСОВ
# ==========================================================

ORBS = {
    "conjunction": 8,
    "opposition": 8,
    "square": 7,
    "trine": 7,
    "sextile": 6,
    "quincunx": 3,
}

# ==========================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==========================================================

def calculate_transit_aspects(transit_positions, natal_positions):
    """
    Рассчитывает аспекты между транзитными и натальными планетами.

    transit_positions: dict { "Sun": {"longitude": 123.45}, ... }
    natal_positions: dict { "Sun": {"longitude": 45.67}, ... }

    Возвращает:
        [
            {
                "transit_planet": "Sun",
                "natal_planet": "Moon",
                "aspect": "conjunction",
                "angle": 2.34,
                "orb": 0.34,
                "direction": "applying" | "separating"
            },
            ...
        ]
    """
    aspects = []

    for t_name, t_data in transit_positions.items():
        t_lon = t_data.get("longitude", 0)
        t_speed = t_data.get("speed", 0)

        for n_name, n_data in natal_positions.items():
            n_lon = n_data.get("longitude", 0)

            # Вычисляем угол между планетами
            raw_angle = (t_lon - n_lon) % 360
            if raw_angle > 180:
                raw_angle = 360 - raw_angle

            # Проверяем каждый тип аспекта
            for aspect_name, orb in ORBS.items():
                target_angle = _get_target_angle(aspect_name)
                if target_angle is None:
                    continue

                diff = abs(raw_angle - target_angle)
                if diff <= orb:
                    aspects.append({
                        "transit_planet": t_name,
                        "natal_planet": n_name,
                        "aspect": aspect_name,
                        "angle": round(raw_angle, 2),
                        "orb": round(diff, 2),
                        "direction": _get_direction(t_speed, aspect_name),
                    })

    # Сортируем по орбису (самые точные первыми)
    aspects.sort(key=lambda x: x["orb"])
    return aspects


def _get_target_angle(aspect_name):
    """Возвращает целевой угол для аспекта."""
    angles = {
        "conjunction": 0,
        "opposition": 180,
        "square": 90,
        "trine": 120,
        "sextile": 60,
        "quincunx": 150,
    }
    return angles.get(aspect_name)


def _get_direction(speed, aspect_name):
    """
    Определяет направление аспекта: applying или separating.
    Для соединения: если транзитная планета движется к натальной — applying.
    Для оппозиции и других: если угол уменьшается — applying.
    """
    if speed >= 0:
        return "applying"
    else:
        return "separating"


# ==========================================================
# ФУНКЦИЯ ДЛЯ ПРОМПТА
# ==========================================================

def format_transit_aspects_for_prompt(aspects, limit=5):
    """
    Форматирует транзитные аспекты для использования в промпте.
    Возвращает строку с наиболее точными аспектами.
    """
    if not aspects:
        return "Активных транзитных аспектов нет."

    lines = []
    for asp in aspects[:limit]:
        direction_ru = "входит" if asp["direction"] == "applying" else "выходит"
        lines.append(
            f"{asp['transit_planet']} {asp['aspect']} {asp['natal_planet']} "
            f"({asp['angle']}°, орбис {asp['orb']}°, {direction_ru})"
        )

    return "\n".join(lines)


# ==========================================================
# ИНТЕГРАЦИЯ С PIPELINE
# ==========================================================

def add_transit_aspects_to_pipeline(transit_planets, natal_planets, prompt_context):
    """
    Добавляет транзитные аспекты в промпт-контекст.
    """
    aspects = calculate_transit_aspects(transit_planets, natal_planets)
    aspects_text = format_transit_aspects_for_prompt(aspects)

    prompt_context["transit_aspects"] = aspects
    prompt_context["transit_aspects_text"] = aspects_text

    return prompt_context