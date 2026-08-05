"""
Liber Astrodum
graphics/glyphs.py

Версия 4.1
Глифы + русские названия.
"""

# ----------------------------------------------------
# ЗНАКИ ЗОДИАКА
# ----------------------------------------------------

ZODIAC = {
    "Aries": {
        "glyph": "♈",
        "ru": "Овен",
        "short": "Ове"
    },
    "Taurus": {
        "glyph": "♉",
        "ru": "Телец",
        "short": "Тел"
    },
    "Gemini": {
        "glyph": "♊",
        "ru": "Близнецы",
        "short": "Бли"
    },
    "Cancer": {
        "glyph": "♋",
        "ru": "Рак",
        "short": "Рак"
    },
    "Leo": {
        "glyph": "♌",
        "ru": "Лев",
        "short": "Лев"
    },
    "Virgo": {
        "glyph": "♍",
        "ru": "Дева",
        "short": "Дев"
    },
    "Libra": {
        "glyph": "♎",
        "ru": "Весы",
        "short": "Вес"
    },
    "Scorpio": {
        "glyph": "♏",
        "ru": "Скорпион",
        "short": "Ско"
    },
    "Sagittarius": {
        "glyph": "♐",
        "ru": "Стрелец",
        "short": "Стр"
    },
    "Capricorn": {
        "glyph": "♑",
        "ru": "Козерог",
        "short": "Коз"
    },
    "Aquarius": {
        "glyph": "♒",
        "ru": "Водолей",
        "short": "Вод"
    },
    "Pisces": {
        "glyph": "♓",
        "ru": "Рыбы",
        "short": "Рыб"
    },
}

# ----------------------------------------------------
# ПЛАНЕТЫ
# ----------------------------------------------------

PLANETS = {
    "Sun": {
        "glyph": "☉",
        "ru": "Солнце",
        "short": "☉"
    },
    "Moon": {
        "glyph": "☽",
        "ru": "Луна",
        "short": "☽"
    },
    "Mercury": {
        "glyph": "☿",
        "ru": "Меркурий",
        "short": "☿"
    },
    "Venus": {
        "glyph": "♀",
        "ru": "Венера",
        "short": "♀"
    },
    "Mars": {
        "glyph": "♂",
        "ru": "Марс",
        "short": "♂"
    },
    "Jupiter": {
        "glyph": "♃",
        "ru": "Юпитер",
        "short": "♃"
    },
    "Saturn": {
        "glyph": "♄",
        "ru": "Сатурн",
        "short": "♄"
    },
    "Uranus": {
        "glyph": "♅",
        "ru": "Уран",
        "short": "♅"
    },
    "Neptune": {
        "glyph": "♆",
        "ru": "Нептун",
        "short": "♆"
    },
    "Pluto": {
        "glyph": "♇",
        "ru": "Плутон",
        "short": "♇"
    },
    "Chiron": {
        "glyph": "⚷",
        "ru": "Хирон",
        "short": "⚷"
    },
}

# ----------------------------------------------------
# СЛУЖЕБНЫЕ ФУНКЦИИ
# ----------------------------------------------------

def zodiac_glyph(sign):
    return ZODIAC.get(sign, {}).get("glyph", "")


def zodiac_name(sign):
    return ZODIAC.get(sign, {}).get("ru", sign)


def zodiac_short(sign):
    return ZODIAC.get(sign, {}).get("short", sign[:3])


def planet_glyph(name):
    return PLANETS.get(name, {}).get("glyph", "")


def planet_name(name):
    return PLANETS.get(name, {}).get("ru", name)


def planet_short(name):
    return PLANETS.get(name, {}).get("short", name)