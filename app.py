from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import os
import logging
import requests
from dotenv import load_dotenv

# ==========================
# Загружаем переменные окружения
# ==========================
load_dotenv()

# ==========================
# Путь к эфемеридам ДОЛЖЕН быть задан ДО импорта swisseph
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EPHE_PATH = os.path.join(BASE_DIR, "ephe")
os.environ["SE_EPHE_PATH"] = EPHE_PATH

# Только теперь импортируем Swiss Ephemeris
import swisseph as swe

# ==========================
# Логирование
# ==========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================
# FastAPI
# ==========================
app = FastAPI(title="Liber Astrodum 2.1")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================== ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ ПОИСКА ГОРОДА ==================

def geocode_city(city: str):
    """
    Получить координаты города через OpenStreetMap Nominatim.
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "LiberAstrodum/2.1 (olafhaldy.pages.dev)"
    }
    params = {
        "q": city,
        "format": "json",
        "limit": 1
    }
    r = requests.get(url, params=params, headers=headers, timeout=15)
    if r.status_code != 200:
        raise Exception("Ошибка обращения к Nominatim")
    data = r.json()
    if not data:
        raise Exception(f"Город '{city}' не найден")
    return float(data[0]["lat"]), float(data[0]["lon"])

# ================== API ПОИСКА ГОРОДА (автодополнение) ==================

@app.get("/api/city-search")
def city_search(q: str = Query(..., min_length=2)):
    """Поиск городов для автодополнения."""
    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "LiberAstrodum/2.1 (olafhaldy.pages.dev)"
    }
    params = {
        "q": q,
        "format": "json",
        "limit": 5,
        "accept-language": "ru",
    }
    r = requests.get(url, params=params, headers=headers, timeout=15)
    if r.status_code != 200:
        return []
    data = r.json()
    results = []
    for place in data:
        results.append({
            "display_name": place["display_name"],
            "lat": float(place["lat"]),
            "lon": float(place["lon"]),
        })
    return results

# ================== HTML-СТРАНИЦА ==================

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liber Astrodum — Книга Звездного Дара</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>&#128302;</text></svg>">
    <link href="https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Uncial+Antiqua&family=Marck+Script&family=Caveat&family=Cormorant+Infant:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Cormorant Infant', serif;
            min-height: 100vh;
            background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.65)), url('/static/bg.jpg') no-repeat center center fixed;
            background-size: cover;
            color: #f0f0f0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .container { max-width: 700px; width: 100%; text-align: center; }
        .app-title h1 {
            font-family: 'UnifrakturMaguntia', cursive;
            font-size: 3.5em;
            background: linear-gradient(135deg, #b0b0b0 0%, #e8e8e8 20%, #ffffff 35%, #a0a0a0 50%, #d0d0d0 65%, #f5f5f5 80%, #909090 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.7)) drop-shadow(0 0 8px rgba(192,192,192,0.8));
            margin-bottom: 10px;
        }
        .poem { color: #c092f9; font-style: italic; font-size: 1.15em; line-height: 1.6; text-shadow: 0 2px 5px rgba(0,0,0,0.5); font-family: 'Marck Script', cursive; }
        .poem-author { color: #b8860b; font-size: 0.95em; margin-bottom: 30px; font-family: 'Caveat', cursive; }
        .menu-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; max-width: 600px; margin: 0 auto; }
        .menu-card {
            background: rgba(28, 28, 28, 0.8); border: 1px solid #444; border-radius: 14px;
            padding: 25px 15px; text-align: center; cursor: pointer; transition: all 0.3s;
            backdrop-filter: blur(5px); text-decoration: none; color: inherit; display: block;
        }
        .menu-card:hover { border-color: #b8860b; box-shadow: 0 0 15px rgba(184, 134, 11, 0.3); transform: translateY(-2px); }
        .menu-card-icon { font-size: 2.5em; margin-bottom: 10px; }
        .menu-card-title { color: #d4af37; font-family: 'Uncial Antiqua', cursive; font-size: 1.2em; margin-bottom: 5px; }
        .menu-card-desc { color: #888; font-size: 0.9em; }
        .menu-card-disabled { opacity: 0.4; cursor: not-allowed; }
        .menu-card-disabled:hover { border-color: #444; box-shadow: none; transform: none; }
        @media (max-width: 768px) { .menu-cards { grid-template-columns: repeat(2, 1fr); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="app-title"><h1>Liber Astrodum</h1></div>
        <div class="poem">Спроси у Сатурна о будущей горсти беды<br>И он не обманет, как люди – меняя обличье.<br>О радостной встрече - Юпитера скажут следы<br>(Где Кронос молчит, там от Зевса исходит величье)</div>
        <div class="poem-author">— Олаф Халди</div>
        <div class="menu-cards">
            <a href="/lunar" class="menu-card">
                <div class="menu-card-icon">🌙</div>
                <div class="menu-card-title">Лунар</div>
                <div class="menu-card-desc">Прогноз на месяц</div>
            </a>
            <div class="menu-card menu-card-disabled">
                <div class="menu-card-icon">☉</div>
                <div class="menu-card-title">Натальная карта</div>
                <div class="menu-card-desc">В разработке</div>
            </div>
            <div class="menu-card menu-card-disabled">
                <div class="menu-card-icon">☀</div>
                <div class="menu-card-title">Соляр</div>
                <div class="menu-card-desc">В разработке</div>
            </div>
            <div class="menu-card menu-card-disabled">
                <div class="menu-card-icon">⏳</div>
                <div class="menu-card-title">Прогрессии</div>
                <div class="menu-card-desc">В разработке</div>
            </div>
            <div class="menu-card menu-card-disabled">
                <div class="menu-card-icon">💞</div>
                <div class="menu-card-title">Синастрия</div>
                <div class="menu-card-desc">В разработке</div>
            </div>
            <div class="menu-card menu-card-disabled">
                <div class="menu-card-icon">🔮</div>
                <div class="menu-card-title">Элекция</div>
                <div class="menu-card-desc">В разработке</div>
            </div>
        </div>
    </div>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE
@app.get("/lunar", response_class=HTMLResponse)
def lunar_page():
    return open("lunar.html", "r", encoding="utf-8").read()
# ================== НОВЫЙ API (Лунар) ==================

@app.get("/api/v1/lunar")
def lunar_v1(
    year: int,
    month: int,
    natal_year: int,
    natal_month: int,
    natal_day: int,
    natal_hour: int,
    natal_minute: int,

    lat: float,
    lon: float,

    birth_lat: float,
    birth_lon: float,

    birth_city: str = "",
    lunar_city: str = "",
):
    """Лунар через полный конвейер Liber Astrodum 2.0."""
    import swisseph as swe
    from builders.lunar_builder import build_lunar_chart
    from core.pipeline import run_full_pipeline
    from core.prompt_builder import build_prompt_from_dict
    from ai import generate
    from graphics.wheel_renderer import draw_wheel

    from datetime import datetime
    import requests
    import os

    # Получаем реальное смещение от TimeZoneDB
    timestamp = int(datetime(natal_year, natal_month, natal_day, 12, 0, 0).timestamp())
    url = "https://api.timezonedb.com/v2.1/get-time-zone"
    params = {
        "key": os.getenv("TIMEZONEDB_API_KEY"),
        "format": "json",
        "by": "position",
        "lat": birth_lat,
        "lng": birth_lon,
        "time": timestamp
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    if data["status"] != "OK":
        raise Exception(f"TimeZoneDB error: {data.get('message', 'unknown')}")
    utc_offset = data["gmtOffset"] / 3600.0
    print(f"[NATAL] Historical UTC offset for birthplace: {utc_offset}h")

    jd_natal = swe.julday(
        natal_year, natal_month, natal_day,
        (natal_hour - utc_offset) + natal_minute / 60.0,
    )
    moon_data, _ = swe.calc_ut(jd_natal, swe.MOON)
    natal_moon_longitude = moon_data[0]
        # Определяем знак натального Солнца для заставки
    sun_data, _ = swe.calc_ut(jd_natal, swe.SUN)
    sun_longitude = sun_data[0]
    SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    natal_sun_sign = SIGNS[int(sun_longitude // 30)]
    chart = build_lunar_chart(
        natal_moon_longitude,
        year, month,
        lat, lon,
        natal_month=natal_month,
        natal_day=natal_day
    )
    wheel_svg = draw_wheel(chart)

    result = run_full_pipeline(chart)
    prompt = build_prompt_from_dict(result["prompt_context"], "lunar")
    print("\n===== LUNAR PROMPT =====")
    print(prompt)
    print("===== END LUNAR PROMPT =====\n")
    print("\n===== PROMPT CHECK =====")
    print(prompt[-5000:])
    print("===== END PROMPT CHECK =====\n")
    try:
        interpretation = generate(prompt)
        print("\n===== LUNAR INTERPRETATION =====")
        print(repr(interpretation))
        print("===== END INTERPRETATION =====\n")
    except Exception as e:
        logger.error(f"LLM failed: {e}")
        interpretation = "Интерпретация временно недоступна."

    return {
        "report": {
            "title": "Лунар",

            "person": {
                "birth_date": f"{natal_day:02d}.{natal_month:02d}.{natal_year}",
                "birth_time": f"{natal_hour:02d}:{natal_minute:02d}",
                "birth_city": birth_city,
            },

            "calculation": {
                "return_datetime": chart.datetime,
                "house_system": "Placidus",
                "lunar_city": lunar_city,
                "target_year": year,
                "target_month": month,
            }
        },

        "date": chart.datetime,
        "interpretation": interpretation,
        "analysis": result["analysis"],
        "planets": chart.planets,
        "houses": chart.houses,
        "aspects": chart.aspects,
        "natal_sun_sign": natal_sun_sign,  # ← новое поле
    "wheel": wheel_svg
}

   