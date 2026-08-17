from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

import os
import logging
import requests
from dotenv import load_dotenv
from datetime import datetime
from ai import generate, generate_short


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

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Liber Astrodum — Книга Звездного Дара</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><polygon points='50,5 61,39 95,39 68,61 79,95 50,75 21,95 32,61 5,39 39,39' fill='%23d4af37' stroke='%23b8860b' stroke-width='2'/></svg>">
    <link href="https://fonts.googleapis.com/css2?family=UnifrakturMaguntia&family=Uncial+Antiqua&family=Marck+Script&family=Caveat&family=Cormorant+Infant:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Cormorant Infant', serif;
            min-height: 100vh;
            color: #f0f0f0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            position: relative;
            overflow-x: hidden;
        }
        #bg-video {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            object-fit: cover;
            z-index: -2;
        }
        .overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.55);
            z-index: -1;
        }
        .container { max-width: 1200px; width: 100%; }

        /* Шапка: прогноз слева, заголовок по центру, луна справа */
        .header {
            display: grid;
            grid-template-columns: 200px 1fr 220px;
            gap: 20px;
            align-items: center;
            margin-bottom: 20px;
        }
        .header-left { text-align: left; }
        .header-left img {
            width: 100px;
            height: 100px;
            object-fit: contain;
            cursor: pointer;
            transition: transform 0.3s, filter 0.3s;
            filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.4));
        }
        .header-left img:hover {
            transform: scale(1.08);
            filter: drop-shadow(0 0 25px rgba(212, 175, 55, 0.7));
        }
        .header-left-label {
            color: #d4af37;
            font-family: 'Caveat', cursive;
            font-size: 1.2em;
            text-align: center;
            margin-top: 5px;
        }
        .header-center { text-align: center; }
        .app-title h1 {
            font-family: 'UnifrakturMaguntia', cursive;
            font-size: 3em;
            background: linear-gradient(135deg, #b0b0b0 0%, #e8e8e8 20%, #ffffff 35%, #a0a0a0 50%, #d0d0d0 65%, #f5f5f5 80%, #909090 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.7)) drop-shadow(0 0 8px rgba(192,192,192,0.8));
        }
        .header-right {
            text-align: center;
            background: rgba(28, 28, 28, 0.8);
            border: 1px solid #444;
            border-radius: 14px;
            padding: 20px;
            backdrop-filter: blur(5px);
        }
        .moon-phase {
            font-size: 2.5em;
            text-align: center;
        }
        .moon-label {
            color: #d4af37;
            font-family: 'Cormorant SC', serif;
            font-size: 1.2em;
            text-align: center;
            margin: 10px 0;
            font-style: normal;
        }
        .moon-sign, .lunar-day {
            font-family: 'Cormorant Infant', serif;
            font-size: 1em;
            text-align: center;
            margin: 5px 0;
            color: #e4e4e4;
        }
        .event-title {
            font-family: 'Cormorant SC', serif;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #b8860b;
            margin-top: 15px;
            margin-bottom: 5px;
            text-align: center;
        }
        .event-text {
            font-family: 'Caveat', cursive;
            font-size: 1.1em;
            color: #f0f0f0;
            line-height: 1.4;
            text-align: center;
        }

        /* Стих */
        .poem-section { text-align: center; margin-bottom: 30px; }
        .poem { color: #bb915e !important; font-style: italic; font-size: 1.15em; line-height: 1.6; text-shadow: 0 2px 5px rgba(0,0,0,0.5); font-family: 'Marck Script', cursive; }
        .poem-author { color: #b8860b; font-size: 0.95em; font-family: 'Caveat', cursive; }

        /* Крупные иконки Лунар и Натал */
        .main-modes {
            display: flex;
            justify-content: center;
            gap: 60px;
            margin-bottom: 40px;
        }
        .main-mode-card {
            text-align: center;
            cursor: pointer;
            text-decoration: none;
            color: inherit;
            display: block;
        }
        .main-mode-card img {
            width: 200px;
            height: 200px;
            object-fit: contain;
            transition: transform 0.3s, filter 0.3s;
            filter: drop-shadow(0 0 15px rgba(212, 175, 55, 0.4));
        }
        .main-mode-card:hover img {
            transform: scale(1.08);
            filter: drop-shadow(0 0 25px rgba(212, 175, 55, 0.7));
        }
        .main-mode-title {
            color: #d4af37;
            font-family: 'Uncial Antiqua', cursive;
            font-size: 1.4em;
            margin-top: 10px;
        }
        .main-mode-desc {
            color: #888;
            font-size: 1em;
            margin-top: 3px;
        }

        /* Мелкие стандартные окна для режимов в разработке */
        .dev-modes {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }
        .dev-mode-card {
            background: rgba(28, 28, 28, 0.8);
            border: 1px solid #444;
            border-radius: 12px;
            padding: 15px 20px;
            text-align: center;
            opacity: 0.5;
            cursor: not-allowed;
        }
        .dev-mode-title {
            color: #d4af37;
            font-family: 'Uncial Antiqua', cursive;
            font-size: 1em;
        }
        .dev-mode-desc {
            color: #888;
            font-size: 0.8em;
            margin-top: 3px;
        }

        /* Лунный календарь */
        .moon-phase { font-size: 2em; text-align: center; }
        .moon-label { color: #d4af37; text-align: center; margin: 8px 0; font-style: italic; }
        .moon-sign, .lunar-day { text-align: center; margin: 3px 0; font-size: 0.9em; }
        .event-title { font-size: 0.75em; text-transform: uppercase; letter-spacing: 1px; color: #b8860b; margin-top: 10px; margin-bottom: 3px; }
        .event-text { color: #f0f0f0; line-height: 1.3; text-align: center; font-size: 0.85em; }

        .error-modal {
            position: fixed;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            background: #1c1c1c;
            border: 2px solid #d4af37;
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            max-width: 380px;
            width: 90%;
            z-index: 1001;
            display: none;
            box-shadow: 0 10px 30px rgba(0,0,0,0.7);
            backdrop-filter: blur(10px);
        }
        .error-modal p { color: #f0f0f0; font-size: 1.15em; line-height: 1.6; margin-bottom: 25px; }
        .error-modal button {
            background: none;
            border: 1px solid #b8860b;
            color: #d4af37;
            padding: 10px 25px;
            border-radius: 20px;
            cursor: pointer;
            font-family: 'Uncial Antiqua', cursive;
            font-size: 1em;
        }
        .overlay-bg {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.6); z-index: 1000; display: none;
        }

        @media (max-width: 768px) {
            .header { grid-template-columns: 1fr; }
            .main-modes { flex-direction: column; align-items: center; }
        }
        .app-subtitle {
    font-family: 'Caveat', cursive;
    font-size: 0.9em;
    color: #b8860b;
    letter-spacing: 3px;
    opacity: 0.7;
    margin-top: -5px;
    text-shadow: 0 0 10px rgba(184, 134, 11, 0.2);
}
    </style>
</head>
<body>
    <video autoplay muted loop playsinline id="bg-video">
        <source src="/static/bg_main.mp4" type="video/mp4">
    </video>
    <div class="overlay"></div>

    <div class="container">
        <div class="header">
            <div class="header-left">
                <a href="/daily">
                    <img src="/static/zodiac/zodiac_circle.png" alt="Прогноз на день">
                    
                </a>
            </div>
            <div class="header-center">
                <div class="app-title">
    <h1>Liber Astrodum</h1>
    <div class="app-subtitle">В поисках небесного кода</div>
</div>
            </div>
            <div class="header-right">
                <div class="side-widget-title">🌙 Лунный календарь</div>
                <div id="moonWidget">Загрузка...</div>
            </div>
        </div>

        <div class="poem-section">
            <div class="poem">Спроси у Сатурна о будущей горсти беды<br>И он не обманет, как люди – меняя обличье.<br>О радостной встрече - Юпитера скажут следы<br>(Где Кронос молчит, там от Зевса исходит величье)</div>
            <div class="poem-author">— Олаф Халди</div>
        </div>

        <div class="main-modes">
    <a href="/lunar" class="main-mode-card">
        <img src="/static/icons/icon_lunar.png" alt="Лунар">
        <div class="main-mode-desc">Прогноз на месяц</div>
    </a>
    <a href="/natal" class="main-mode-card">
        <img src="/static/icons/icon_natal.png" alt="Натальная карта">
        <div class="main-mode-desc">Карта рождения</div>
    </a>
</div>

        <div class="dev-modes">
            <div class="dev-mode-card">
                <div class="dev-mode-title">☀ Соляр</div>
                <div class="dev-mode-desc">В разработке</div>
            </div>
            <div class="dev-mode-card">
                <div class="dev-mode-title">⏳ Прогрессии</div>
                <div class="dev-mode-desc">В разработке</div>
            </div>
            <div class="dev-mode-card">
                <div class="dev-mode-title">💞 Синастрия</div>
                <div class="dev-mode-desc">В разработке</div>
            </div>
            <div class="dev-mode-card">
                <div class="dev-mode-title">🔮 Элекция</div>
                <div class="dev-mode-desc">В разработке</div>
            </div>
        </div>
    </div>

    <div id="errorOverlay" class="overlay-bg" onclick="closeErrorModal()"></div>
    <div id="errorModal" class="error-modal">
        <p>Звёзды, как и астролог-мечтатель, любят покой. Позвольте ему отложить до завтра ваш запрос.</p>
        <button onclick="closeErrorModal()">Принимаю</button>
    </div>

    <script>
        function showErrorModal() {
            document.getElementById('errorOverlay').style.display = 'block';
            document.getElementById('errorModal').style.display = 'block';
        }
        function closeErrorModal() {
            document.getElementById('errorOverlay').style.display = 'none';
            document.getElementById('errorModal').style.display = 'none';
        }

        // Загружаем прогноз на день


        // Загружаем лунный календарь
        fetch('/widget')
            .then(r => r.json())
            .then(data => {
                document.getElementById('moonWidget').innerHTML = `
                    <div class="moon-phase">${data.moon_emoji}</div>
                    <div class="moon-label">${data.moon_phase}</div>
                    <div class="moon-sign">Луна в знаке: ${data.moon_sign}</div>
                    <div class="lunar-day">День ${data.lunar_day}: ${data.lunar_day_name}</div>

                    <div class="event-title">🌿 Совет дня</div>
                    <div class="event-text">${data.advice}</div>
                `;
            })
            .catch(() => {
                document.getElementById('moonWidget').innerHTML = 'Данные недоступны.';
            });
    </script>
</body>
</html>"""
@app.get("/api/v1/daily")
def daily_v1(sign: str = "Aquarius"):
    """Короткий прогноз на день для знака зодиака."""
    import swisseph as swe
    from datetime import datetime
    from ai import generate

    # Текущие транзиты
    now = datetime.utcnow()
    jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)

    transit_positions = {}
    SIGNS = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    PLANET_IDS = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
        'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN
    }

    SIGN_NAMES_RU = {
        'Aries': 'Овен', 'Taurus': 'Телец', 'Gemini': 'Близнецы',
        'Cancer': 'Рак', 'Leo': 'Лев', 'Virgo': 'Дева',
        'Libra': 'Весы', 'Scorpio': 'Скорпион', 'Sagittarius': 'Стрелец',
        'Capricorn': 'Козерог', 'Aquarius': 'Водолей', 'Pisces': 'Рыбы'
    }

    PLANET_NAMES_RU = {
        'Sun': 'Солнце', 'Moon': 'Луна', 'Mercury': 'Меркурий',
        'Venus': 'Венера', 'Mars': 'Марс', 'Jupiter': 'Юпитер',
        'Saturn': 'Сатурн'
    }

    sign_ru = SIGN_NAMES_RU.get(sign, sign)

    for name, pid in PLANET_IDS.items():
        data, _ = swe.calc_ut(jd, pid)
        lon = data[0]
        sign_num = int(lon // 30)
        degree = round(lon % 30, 2)
        transit_positions[name] = {
            "sign": SIGNS[sign_num],
            "degree": degree,
            "longitude": lon
        }

    transit_text = "\n".join([
        f"{PLANET_NAMES_RU.get(name, name)}: {data['degree']}° {data['sign']}"
        for name, data in transit_positions.items()
    ])

    prompt = f"""Ты — Астродо, хранитель Небесного Архива Liber Astrodum.

Составь короткий прогноз на сегодня для знака {sign_ru}.

Текущие положения планет:
{transit_text}

ВАЖНО: Используй только классических управителей знаков:
Овен — Марс, Телец — Венера, Близнецы — Меркурий, Рак — Луна,
Лев — Солнце, Дева — Меркурий, Весы — Венера, Скорпион — Марс,
Стрелец — Юпитер, Козерог — Сатурн, Водолей — Сатурн, Рыбы — Юпитер.

Требования:
1. Ровно 2-3 предложения
2. Афористичный, философский стиль
3. Без «вас ждёт», «будьте осторожны», «удачный день»
4. Укажи, какая планета сегодня наиболее влияет на знак {sign_ru}
5. Дай один неожиданный, но точный совет

Не используй markdown. Не добавляй заголовков. Просто текст из 2-3 предложений."""

    try:
        interpretation = generate(prompt)
    except Exception as e:
        interpretation = "Сегодня звёзды говорят тихо. Прислушайся к тишине."

    return {
        "sign": sign_ru,
        "date": now.strftime("%Y-%m-%d"),
        "interpretation": interpretation,
        "transits": transit_positions
    }
@app.get("/api/v1/daily-personal")
def daily_personal_v1(
    natal_year: int,
    natal_month: int,
    natal_day: int,
    natal_hour: int = 12,
    natal_minute: int = 0,
    lat: float = 50.45,
    lon: float = 30.52,
):
    """Персональный прогноз на день по натальной карте."""
    import swisseph as swe
    from datetime import datetime
    from ai import generate
    from builders.natal_builder import build_natal_chart

    # Строим натальную карту
    chart = build_natal_chart(natal_year, natal_month, natal_day, natal_hour, natal_minute, lat, lon)

    # Текущие транзиты
    now = datetime.utcnow()
    jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)

    PLANET_IDS = {
        'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY,
        'Venus': swe.VENUS, 'Mars': swe.MARS, 'Jupiter': swe.JUPITER,
        'Saturn': swe.SATURN
    }
    SIGNS_RU = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева',
                'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']
    PLANET_NAMES_RU = {
        'Sun': 'Солнце', 'Moon': 'Луна', 'Mercury': 'Меркурий',
        'Venus': 'Венера', 'Mars': 'Марс', 'Jupiter': 'Юпитер',
        'Saturn': 'Сатурн'
    }

    transit_text = []
    for name, pid in PLANET_IDS.items():
        t_data, _ = swe.calc_ut(jd, pid)
        t_lon = t_data[0]
        t_sign = SIGNS_RU[int(t_lon // 30)]
        t_degree = round(t_lon % 30, 2)
        transit_text.append(f"{PLANET_NAMES_RU.get(name, name)}: {t_degree}° {t_sign}")

    # Натальные позиции
    natal_text = []
    for name, data in chart.planets.items():
        n_sign = SIGNS_RU[int(data['longitude'] // 30)]
        n_degree = round(data['longitude'] % 30, 2)
        natal_text.append(f"{PLANET_NAMES_RU.get(name, name)}: {n_degree}° {n_sign}")

    prompt = f"""Ты — Астродо, хранитель Небесного Архива Liber Astrodum.

Составь персональный прогноз на сегодня.

НАТАЛЬНАЯ КАРТА ЧЕЛОВЕКА:
{chr(10).join(natal_text)}

ТЕКУЩИЕ ПОЛОЖЕНИЯ ПЛАНЕТ:
{chr(10).join(transit_text)}

ВАЖНО:
1. Используй только классических управителей знаков:
Овен — Марс, Телец — Венера, Близнецы — Меркурий, Рак — Луна,
Лев — Солнце, Дева — Меркурий, Весы — Венера, Скорпион — Марс,
Стрелец — Юпитер, Козерог — Сатурн, Водолей — Сатурн, Рыбы — Юпитер.

2. Найди, какая транзитная планета сегодня образует самый важный аспект к натальной карте.

3. Дай короткий, но глубокий персональный прогноз.

Требования:
- Ровно 2-3 предложения
- Афористичный, философский стиль
- Без «вас ждёт», «будьте осторожны», «удачный день»
- Обращайся к человеку лично, но без панибратства
- Дай один неожиданный, но точный совет

Не используй markdown. Не добавляй заголовков. Просто текст из 2-3 предложений."""

    try:
        interpretation = generate(prompt)
    except Exception as e:
        interpretation = "Сегодня звёзды говорят тихо. Прислушайся к тишине."

    return {
        "date": now.strftime("%Y-%m-%d"),
        "interpretation": interpretation
    }
# ================== ЛУННЫЙ КАЛЕНДАРЬ ==================

# ================== ЛУННЫЙ КАЛЕНДАРЬ ==================

def get_moon_phase():
    """Возвращает полную информацию о Луне для виджета."""
    from datetime import datetime
    import swisseph as swe

    now = datetime.utcnow()
    jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)
    sun_lon = swe.calc_ut(jd, swe.SUN)[0][0]
    moon_lon = swe.calc_ut(jd, swe.MOON)[0][0]
    angle = (moon_lon - sun_lon) % 360

    # Фаза Луны
    if angle < 22.5 or angle >= 337.5:
        phase_emoji, phase_name = "🌑", "Новолуние"
    elif 22.5 <= angle < 67.5:
        phase_emoji, phase_name = "🌒", "Молодая луна"
    elif 67.5 <= angle < 112.5:
        phase_emoji, phase_name = "🌓", "Первая четверть"
    elif 112.5 <= angle < 157.5:
        phase_emoji, phase_name = "🌔", "Прибывающая луна"
    elif 157.5 <= angle < 202.5:
        phase_emoji, phase_name = "🌕", "Полнолуние"
    elif 202.5 <= angle < 247.5:
        phase_emoji, phase_name = "🌖", "Убывающая луна"
    elif 247.5 <= angle < 292.5:
        phase_emoji, phase_name = "🌗", "Последняя четверть"
    else:
        phase_emoji, phase_name = "🌘", "Старая луна"

    # Знак Луны
    signs = ['Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева',
             'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы']
    moon_sign = signs[int(moon_lon // 30)]

    # Лунный день
    lunar_day = int(angle / 12) + 1
    if lunar_day > 30:
        lunar_day = 1

    # Названия дней
    lunar_day_names = {
        1: "День творения", 2: "День дара", 3: "День воина",
        4: "День равновесия", 5: "День вкушения", 6: "День пророчества",
        7: "День молитвы", 8: "День трансформации", 9: "День искушений",
        10: "День источника", 11: "День энергетического меча",
        12: "День чаши", 13: "День змеи", 14: "День трубы",
        15: "День полноты", 16: "День равновесия", 17: "День танца",
        18: "День зеркала", 19: "День паука", 20: "День орла",
        21: "День коня", 22: "День слона", 23: "День очищения",
        24: "День медведя", 25: "День черепахи", 26: "День жабы",
        27: "День жезла", 28: "День лотоса", 29: "День завершения",
        30: "День золотого лебедя",
    }
    lunar_day_name = lunar_day_names.get(lunar_day, "")

    # Советы
    lunar_advices = {
        1: "День творения — планируйте, мечтайте, загадывайте желания.",
        2: "День дара — принимайте дары судьбы, будьте щедры.",
        3: "День воина — действуйте решительно, защищайте свои границы.",
        4: "День равновесия — ищите баланс во всём, не перегружайтесь.",
        5: "День вкушения — наслаждайтесь жизнью, радуйтесь простому.",
        6: "День пророчества — прислушивайтесь к интуиции и знакам.",
        7: "День молитвы — обратитесь к высшему, практикуйте благодарность.",
        8: "День трансформации — отпускайте старое, готовьтесь к новому.",
        9: "День искушений — будьте осторожны с соблазнами, не поддавайтесь.",
        10: "День источника — наполняйтесь энергией, ищите вдохновение.",
        11: "День энергетического меча — направьте силу на важное, отсеките лишнее.",
        12: "День чаши — откройтесь любви, заботе, нежности.",
        13: "День змеи — мудрость через тишину, наблюдайте.",
        14: "День трубы — заявите о себе, ваш голос важен.",
        15: "День полноты — завершайте начатое, подводите итоги.",
        16: "День равновесия — восстановите гармонию, отдохните.",
        17: "День танца — позвольте себе радость движения, лёгкость.",
        18: "День зеркала — посмотрите на себя честно, примите себя.",
        19: "День паука — плетите свою судьбу, будьте терпеливы.",
        20: "День орла — поднимитесь над ситуацией, увидьте перспективу.",
        21: "День коня — вперёд, без колебаний, риск оправдан.",
        22: "День слона — мудрость, стойкость, не торопитесь.",
        23: "День очищения — избавьтесь от лишнего, очистите пространство.",
        24: "День медведя — сила в покое, берегите энергию.",
        25: "День черепахи — медленно, но верно, не сдавайтесь.",
        26: "День жабы — смирение, принимайте то, что есть.",
        27: "День жезла — власть над собой, управляйте своей жизнью.",
        28: "День лотоса — расцветайте, раскрывайте свой потенциал.",
        29: "День завершения — отпустите всё лишнее, готовьтесь к новому циклу.",
        30: "День золотого лебедя — совершенство, благодарность, свет.",
    }
    advice = lunar_advices.get(lunar_day, "Доверьтесь интуиции и наблюдайте за ритмами природы.")

    return {
        "phase_emoji": phase_emoji,
        "phase_name": phase_name,
        "moon_sign": moon_sign,
        "lunar_day": lunar_day,
        "lunar_day_name": lunar_day_name,
        "advice": advice,
    }


# ===== ЭНДПОИНТ ВИДЖЕТА =====
@app.get("/widget")
def widget_data():
    """Текущая фаза Луны, знак, лунный день."""
    moon_data = get_moon_phase()
    return JSONResponse(content={
        "moon_emoji": moon_data["phase_emoji"],
        "moon_phase": moon_data["phase_name"],
        "moon_sign": moon_data["moon_sign"],
        "lunar_day": moon_data["lunar_day"],
        "lunar_day_name": moon_data["lunar_day_name"],
        "advice": moon_data["advice"],
    })
@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE

@app.get("/lunar", response_class=HTMLResponse)
def lunar_page():
    return open("lunar.html", "r", encoding="utf-8").read()

@app.get("/natal", response_class=HTMLResponse)
def natal_page():
    return open("natal.html", "r", encoding="utf-8").read()
@app.get("/key", response_class=HTMLResponse)
def key_page():
    return open("key.html", "r", encoding="utf-8").read()

# ================== API НАТАЛЬНОЙ КАРТЫ ==================

@app.get("/api/v1/natal")
def natal_v1(
    natal_year: int,
    natal_month: int,
    natal_day: int,
    natal_hour: int = 12,
    natal_minute: int = 0,
    lat: float = 50.45,
    lon: float = 30.52,
):
    """Натальная карта через полный конвейер."""
    import swisseph as swe
    from builders.natal_builder import build_natal_chart
    from core.pipeline import run_full_pipeline
    from core.prompt_builder import build_prompt_from_dict
    from ai import generate
    from graphics.wheel_renderer import draw_wheel

    chart = build_natal_chart(natal_year, natal_month, natal_day, natal_hour, natal_minute, lat, lon)
    wheel_svg = draw_wheel(chart)

    result = run_full_pipeline(chart)
    prompt = build_prompt_from_dict(result["prompt_context"], "natal")

    try:
        interpretation = generate(prompt)
    except Exception as e:
        logger.error(f"LLM failed: {e}")
        interpretation = "Интерпретация временно недоступна."

    sun_sign = chart.planets['Sun']['sign']

    return {
        "date": chart.datetime,
        "interpretation": interpretation,
        "analysis": result["analysis"],
        "planets": chart.planets,
        "houses": chart.houses,
        "aspects": chart.aspects,
        "natal_sun_sign": sun_sign,
        "wheel": wheel_svg
    }

# ================== API ЛУНАРА ==================
@app.get("/daily", response_class=HTMLResponse)
def daily_page():
    return open("daily.html", "r", encoding="utf-8").read()
@app.get("/daily-personal", response_class=HTMLResponse)
def daily_personal_page():
    return open("daily_personal.html", "r", encoding="utf-8").read()
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

    jd_natal = swe.julday(
        natal_year, natal_month, natal_day,
        (natal_hour - utc_offset) + natal_minute / 60.0,
    )
    moon_data, _ = swe.calc_ut(jd_natal, swe.MOON)
    natal_moon_longitude = moon_data[0]

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

    try:
        interpretation = generate(prompt)
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
        "natal_sun_sign": natal_sun_sign,
        "wheel": wheel_svg
    }
import datetime

@app.get("/api/v1/key")
def key_v1(sign: str = "Aquarius"):
    import datetime
    from ai import generate

    SIGN_NAMES_RU = {
        'Aries': 'Овен', 'Taurus': 'Телец', 'Gemini': 'Близнецы',
        'Cancer': 'Рак', 'Leo': 'Лев', 'Virgo': 'Дева',
        'Libra': 'Весы', 'Scorpio': 'Скорпион', 'Sagittarius': 'Стрелец',
        'Capricorn': 'Козерог', 'Aquarius': 'Водолей', 'Pisces': 'Рыбы'
    }

    sign_ru = SIGN_NAMES_RU.get(sign, sign)
    today = datetime.datetime.now()
    topic = "мудрость и покой"

    # === ПРОСТЕЙШИЙ ПРОМПТ ===
    prompt = f"Напиши одну короткую фразу для знака {sign_ru} на тему {topic}. Максимум 10 слов. Только фраза."

    try:
        raw = generate(prompt)
        # === ПРОСТЕЙШАЯ ЧИСТКА ===
        aphorism = raw.strip()[:200]
        if not aphorism:
            aphorism = "Сегодня звёзды говорят тихо."
    except Exception as e:
        logger.warning("Key aphorism generation failed: %s", e)
        aphorism = "Сегодня звёзды говорят тихо."

    return {
        "sign": sign_ru,
        "topic": topic,
        "aphorism": aphorism
    }