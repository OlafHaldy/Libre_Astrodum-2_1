"""
Liber Astrodum
core/receptions.py

Взаимные рецепции между планетами.

Рецепция — это когда планета находится в знаке, которым управляет другая планета.
Взаимная рецепция — когда обе планеты находятся в знаках друг друга.

Используется для:
- Оценки силы связей между планетами
- Понимания взаимных влияний
- Уточнения интерпретации аспектов

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0
"""

from core.rulerships import SIGN_RULER, get_ruler_by_sign


# ==========================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ==========================================================

def build_receptions(planets):
    """
    Рассчитывает рецепции между всеми планетами.

    planets: dict вида { "Sun": {"sign": "Leo", ...}, ... }

    Возвращает:
        {
            "Sun": {
                "receives": ["Mercury", "Venus"],      # планеты, которые в знаке Солнца
                "received_by": ["Moon"],               # планеты, в чьём знаке находится Солнце
                "mutual": ["Moon"]                     # взаимные рецепции
            },
            ...
        }
    """
    # Словарь: знак → управитель
    sign_to_ruler = SIGN_RULER

    # Словарь: планета → знак
    planet_to_sign = {}
    for name, data in planets.items():
        if "sign" in data:
            planet_to_sign[name] = data["sign"]

    result = {}

    for planet_a, sign_a in planet_to_sign.items():
        # Кто управляет знаком планеты A
        ruler_of_a = sign_to_ruler.get(sign_a)

        # Кто находится в знаке планеты A (кто управляется этой планетой)
        receives = []
        for planet_b, sign_b in planet_to_sign.items():
            if planet_b == planet_a:
                continue
            # Если знак планеты B управляется планетой A
            if sign_to_ruler.get(sign_b) == planet_a:
                receives.append(planet_b)

        # В чьём знаке находится планета A (кто управляет её знаком)
        received_by = []
        if ruler_of_a:
            received_by.append(ruler_of_a)

        # Взаимные рецепции: планета A в знаке B, и планета B в знаке A
        mutual = []
        if ruler_of_a:
            for planet_b, sign_b in planet_to_sign.items():
                if planet_b == planet_a:
                    continue
                # Если планета B находится в знаке A
                # И планета A находится в знаке B
                if sign_to_ruler.get(sign_b) == planet_a and ruler_of_a == planet_b:
                    mutual.append(planet_b)

        result[planet_a] = {
            "receives": receives,
            "received_by": received_by,
            "mutual": mutual,
        }

    return result


# ==========================================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ
# ==========================================================

def get_reception_description(receptions, planet):
    """
    Возвращает человекочитаемое описание рецепций для планеты.
    """
    data = receptions.get(planet, {})
    parts = []

    if data.get("mutual"):
        parts.append(f"Взаимная рецепция с {', '.join(data['mutual'])}")
    if data.get("receives"):
        parts.append(f"Принимает {', '.join(data['receives'])}")
    if data.get("received_by"):
        parts.append(f"Принят {', '.join(data['received_by'])}")

    if not parts:
        return "Нет рецепций"
    return "; ".join(parts)


# ==========================================================
# ФУНКЦИЯ ДЛЯ ПРОМПТА
# ==========================================================

def format_receptions_for_prompt(receptions):
    """
    Форматирует рецепции для использования в промпте.
    """
    lines = []
    for planet, data in receptions.items():
        if data.get("mutual"):
            lines.append(f"{planet}: взаимная рецепция с {', '.join(data['mutual'])}")
        elif data.get("receives"):
            lines.append(f"{planet}: принимает {', '.join(data['receives'])}")
        elif data.get("received_by"):
            lines.append(f"{planet}: принят {', '.join(data['received_by'])}")

    if not lines:
        return "Взаимных рецепций нет"

    return "\n".join(lines)