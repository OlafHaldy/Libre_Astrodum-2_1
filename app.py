from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
from dotenv import load_dotenv
import swisseph as swe

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EPHE_PATH = os.path.join(BASE_DIR, "ephe")

swe.set_ephe_path(EPHE_PATH)
logger.info(f"Swiss path = {EPHE_PATH}")
logger.info(f"Exists = {os.path.exists(EPHE_PATH)}")
logger.info(f"Contains seas_18 = {os.path.exists(os.path.join(EPHE_PATH, 'seas_18.se1'))}")

logger.info(f"Swiss Ephemeris path: {EPHE_PATH}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Liber Astrodum 2.1")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ================== HTML-СТРАНИЦА ==================

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>Liber Astrodum – Книга Звездного Дара</title>
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
            position: relative;
            overflow-x: hidden;
        }
        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: transparent;
            box-shadow:
                20vw 10vh 2px rgba(255,255,255,0.8),
                55vw 20vh 1px rgba(255,255,255,0.6),
                80vw 15vh 2px rgba(255,255,255,0.7),
                10vw 30vh 1px rgba(255,255,255,0.5),
                60vw 40vh 2px rgba(255,255,255,0.9),
                90vw 50vh 1px rgba(255,255,255,0.4),
                30vw 60vh 2px rgba(255,255,255,0.8),
                70vw 70vh 1px rgba(255,255,255,0.6),
                5vw 80vh 2px rgba(255,255,255,0.7),
                85vw 85vh 1px rgba(255,255,255,0.5),
                45vw 90vh 2px rgba(255,255,255,0.8),
                15vw 95vh 1px rgba(255,255,255,0.6);
            animation: twinkle 3s infinite alternate;
            pointer-events: none;
        }
        @keyframes twinkle {
            0% { opacity: 0.6; }
            100% { opacity: 1; }
        }

        .container { max-width: 1200px; width: 100%; }
        .app-title { text-align: center; margin-bottom: 10px; }
        .app-title h1 {
            font-family: 'UnifrakturMaguntia', 'Uncial Antiqua', cursive;
            font-size: 3em;
            background: linear-gradient(
                135deg,
                #b0b0b0 0%,
                #e8e8e8 20%,
                #ffffff 35%,
                #a0a0a0 50%,
                #d0d0d0 65%,
                #f5f5f5 80%,
                #909090 100%
            );
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.7)) 
                    drop-shadow(0 0 8px rgba(192,192,192,0.8));
        }
        .poem {
            text-align: left;
            margin-bottom: 5px;
            color: #c092f9;
            font-style: italic;
            font-size: 1.15em;
            line-height: 1.6;
            text-shadow: 0 2px 5px rgba(0,0,0,0.5);
            font-family: 'Marck Script', cursive;
        }
        .poem-author {
            text-align: left;
            color: #b8860b;
            font-size: 0.95em;
            margin-bottom: 20px;
            font-style: normal;
            font-family: 'Caveat', cursive;
        }
        .app-subtitle {
            color: #f8f8f8;
            font-size: 1.725em;
            text-align: center;
            margin-bottom: 30px;
            line-height: 1.5;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
            font-style: italic;
        }
        .lang-switch { display: flex; justify-content: center; gap: 10px; margin-bottom: 15px; }
        .lang-btn {
            background: rgba(30, 30, 30, 0.8);
            border: 1px solid #4a4a4a;
            color: #ccc;
            padding: 8px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-family: 'Cormorant Infant', serif;
            font-size: 16px;
            transition: all 0.3s;
            backdrop-filter: blur(5px);
        }
        .lang-btn.active { background: #b8860b; border-color: #ffd700; color: white; }

        /* Сетка */
        .layout {
            display: flex;
            gap: 30px;
            align-items: flex-start;
            max-width: 1200px;
            width: 100%;
            margin: 0 auto;
        }
        .main-content {
            flex: 1;
            max-width: 700px;
            margin: 0 auto;
        }
        .side-menu {
            position: fixed;
            left: 20px;
            top: 250px;
            width: 180px;
            padding: 12px;
            gap: 4px;
            z-index: 100;
            flex-shrink: unset;
            background-image: url('/static/shelf_bg.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-color: rgba(30, 20, 10, 0.7);
            background-blend-mode: overlay;
            backdrop-filter: blur(10px);
            border: 1px solid #5a5a5a;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            display: flex;
            flex-direction: column;
            max-height: calc(100vh - 280px);
            overflow-y: auto;
            scrollbar-width: thin;
            scrollbar-color: #b8860b #2c2c2c;
        }
        .menu-title {
            color: #d4af37;
            font-family: 'Uncial Antiqua', cursive;
            font-size: 1.1em;
            margin-bottom: 10px;
            text-align: center;
        }
        .menu-hint {
            color: #888;
            font-family: 'Caveat', cursive;
            font-size: 0.9em;
            text-align: center;
            margin-top: 15px;
            font-style: italic;
        }
        .side-menu .mode-btn {
            background: none;
            border: none;
            color: #aaa;
            padding: 6px 8px;
            font-size: 15px;
            cursor: pointer;
            font-family: 'Cormorant Infant', serif;
            text-align: left;
            transition: all 0.3s;
            width: 100%;
            outline: none;
            box-shadow: none;
            backdrop-filter: none;
        }
        .side-menu .mode-btn:hover {
            color: #d4af37;
            text-shadow: 0 0 8px rgba(212, 175, 55, 0.4);
        }
        .side-menu .mode-btn.active {
            color: #ffd700;
            text-shadow: 0 0 12px rgba(255, 215, 0, 0.6);
        }
        .lang-btn {
            width: 120px;
            height: 44px;
            padding: 0;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .card {
            background-image: url('/static/card_bg.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-color: rgba(30, 20, 10, 0.6);
            background-blend-mode: overlay;
            border: 1px solid #5a5a5a;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.08);
            backdrop-filter: blur(10px);
        }
        label { 
            display: block; 
            margin-top: 18px; 
            font-weight: 400; 
            color: #256057; 
            letter-spacing: 0.5px;
            font-size: 1.2em;
            font-family: 'Caveat', cursive;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            margin-top: 6px;
            background: #1c1c1c;
            border: 1px solid #444;
            border-radius: 10px;
            color: #ffffff;
            font-size: 16px;
            font-family: 'Cormorant Infant', serif;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #b8860b;
            box-shadow: 0 0 10px rgba(184, 134, 11, 0.4);
        }
        textarea { height: 90px; resize: vertical; }
        select {
            cursor: pointer;
            appearance: none;
            background: #1c1c1c url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%23d4af37' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10z'/%3E%3C/svg%3E") no-repeat right 15px center;
            padding-right: 35px;
        }
        .row { display: flex; gap: 12px; }
        .row > div { flex: 1; }
        button {
            background: linear-gradient(135deg, #b8860b, #d4af37);
            color: #1a1a1a;
            border: none;
            padding: 14px 30px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 12px;
            cursor: pointer;
            margin-top: 25px;
            width: 100%;
            font-family: 'Cormorant Infant', serif;
            letter-spacing: 1px;
            transition: transform 0.2s, box-shadow 0.2s;
            text-transform: uppercase;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(184, 134, 11, 0.5);
        }
        button:active { transform: translateY(0); }

        #overlay {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(9, 10, 15, 0.95);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            flex-direction: column;
        }
        #overlay .sign-emoji { font-size: 100px; animation: float 2s ease-in-out infinite; }
        #overlay .sign-name {
            font-family: 'Uncial Antiqua', cursive;
            font-size: 2em;
            color: #d4af37;
            margin-top: 15px;
            text-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }

        #result { margin-top: 25px; display: none; position: relative; max-width: 700px; margin-left: auto; margin-right: auto; }
        .section {
            background: rgba(28, 28, 28, 0.8);
            border: 1px solid #444;
            border-radius: 14px;
            padding: 20px;
            margin-bottom: 16px;
            backdrop-filter: blur(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        }
        .section h3 {
            font-family: 'Uncial Antiqua', cursive;
            color: #d4af37;
            font-size: 1.3em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .section p {
            line-height: 1.7;
            color: #f0f0f0;
            text-shadow: 0 1px 2px rgba(0,0,0,0.7);
        }
        .loading { text-align: center; color: #d4af37; margin-top: 25px; font-style: italic; }
        #suggestions div:hover { background: #3a3a3a; }
        .hint { font-size: 0.85em; color: #888; margin-top: 4px; }

        /* Мобильная версия */
        @media (max-width: 800px) {
            .layout { flex-direction: column; }
            .side-menu {
                position: static;
                width: 100%;
                flex-direction: row;
                flex-wrap: wrap;
                gap: 8px;
                padding: 15px;
                justify-content: center;
                border-radius: 14px;
                background-image: none;
                background-color: rgba(44, 44, 44, 0.85);
            }
            .side-menu .mode-btn {
                background: none;
                border: none;
                color: #aaa;
                padding: 6px 8px;
                font-size: 15px;
                cursor: pointer;
                font-family: 'Cormorant Infant', serif;
                text-align: left;
                transition: all 0.3s;
                width: 100%;
                outline: none;
                box-shadow: none;
                backdrop-filter: none;
            }
            .app-title h1 { font-size: 2em; padding: 0 50px; }
            .poem { font-size: 1em; }
            .card { padding: 20px; border-radius: 14px; }
            button { font-size: 16px; padding: 12px 20px; }
            input, textarea, select { font-size: 16px; }
            .braziers-container { display: none; }
            #celestial-widget { display: none !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="app-title"><h1>Liber Astrodum</h1></div>
        <div class="poem">
            Спроси у Сатурна о будущей горсти беды<br>
            И он не обманет, как люди – меняя обличье.<br>
            О радостной встрече - Юпитера скажут следы<br>
            (Где Кронос молчит, там от Зевса исходит величье)
        </div>
        <div class="poem-author">— Олаф Халди</div>
        <div class="app-subtitle">
            · Едва уловимый шепот звезд ·
        </div>

        <div class="lang-switch">
            <button class="lang-btn active" onclick="switchLang('ru')">Услышать</button>
            <button class="lang-btn" onclick="switchLang('uk')">Почути</button>
        </div>

        <div class="layout">
            <div class="main-content">
                <!-- Панель Лунара -->
                <div class="card" id="lunarCard">
                    <h3 style="color: #d4af37; font-family: 'Uncial Antiqua', cursive; text-align: center; margin-bottom: 20px;">☽ Лунар — Прогноз на месяц</h3>
                    <div class="row">
                        <div><label>Год рождения</label><input type="number" id="natalYear" value="1991"></div>
                        <div><label>Месяц</label><input type="number" id="natalMonth" value="2"></div>
                        <div><label>День</label><input type="number" id="natalDay" value="14"></div>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <div style="flex: 1;">
                            <label>Год прогноза</label>
                            <input type="number" id="lunarYear" value="2026">
                        </div>
                        <div style="flex: 1;">
                            <label>Месяц прогноза</label>
                            <input type="number" id="lunarMonth" value="8" min="1" max="12">
                        </div>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <div style="flex: 1;">
                            <label>Широта</label>
                            <input type="number" id="lat" value="50.45" step="any">
                        </div>
                        <div style="flex: 1;">
                            <label>Долгота</label>
                            <input type="number" id="lon" value="30.52" step="any">
                        </div>
                    </div>
                    <button onclick="askLunar()" style="margin-top: 15px;">Построить Лунар</button>
                    <div id="lunarResult" style="margin-top: 20px; display: none;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        async function askLunar() {
            const natalYear = document.getElementById('natalYear').value;
            const natalMonth = document.getElementById('natalMonth').value;
            const natalDay = document.getElementById('natalDay').value;
            const year = document.getElementById('lunarYear').value;
            const month = document.getElementById('lunarMonth').value || 1;
            const lat = document.getElementById('lat').value || 50.45;
            const lon = document.getElementById('lon').value || 30.52;

            const resultBlock = document.getElementById('lunarResult');
            resultBlock.style.display = 'block';
            resultBlock.innerHTML = '<div class="loading">Звёзды советуют...</div>';

            const params = new URLSearchParams({ year, month, natal_year: natalYear, natal_month: natalMonth, natal_day: natalDay, lat, lon });
            try {
                const response = await fetch('/api/v1/lunar?' + params.toString());
                const data = await response.json();
                if (data.interpretation) {
                    resultBlock.innerHTML = `<div class="details">${data.interpretation.replace(/\n/g, '<br>')}</div>`;
                } else {
                    resultBlock.innerHTML = '<div class="details">Интерпретация временно недоступна.</div>';
                }
            } catch (e) {
                resultBlock.innerHTML = '<div class="verdict">Ошибка соединения со звёздами</div>';
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE

# ================== НОВЫЙ API (Лунар) ==================

@app.get("/api/v1/lunar")
def lunar_v1(
    year: int = Query(...),
    month: int = Query(1),
    natal_year: int = Query(...),
    natal_month: int = Query(...),
    natal_day: int = Query(...),
    lat: float = Query(50.45),
    lon: float = Query(30.52),
):
    """Лунар через полный конвейер Liber Astrodum 2.0."""
    from builders.lunar_builder import build_lunar_chart
    from core.pipeline import run_full_pipeline
    from core.prompt_builder import build_prompt_from_dict
    from ai import generate
    import swisseph as swe

    # Натальная Луна
    jd_natal = swe.julday(natal_year, natal_month, natal_day, 12)
    moon_data, _ = swe.calc_ut(jd_natal, swe.MOON)
    natal_moon_longitude = moon_data[0]

    # Лунар
    chart = build_lunar_chart(natal_moon_longitude, year, month, lat, lon)
    result = run_full_pipeline(chart)
    prompt = build_prompt_from_dict(result["prompt_context"], "lunar")

    try:
        interpretation = generate(prompt)
    except Exception as e:
        logger.error(f"LLM failed: {e}")
        interpretation = "Интерпретация временно недоступна."

    return {
        "date": chart.datetime,
        "interpretation": interpretation,
        "analysis": result["analysis"],
    }