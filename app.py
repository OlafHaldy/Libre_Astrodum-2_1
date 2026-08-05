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

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="ru">
<head>

    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
        /* ... (весь твой красивый CSS, который был раньше, без изменений) ... */
        .container { max-width: 700px; width: 100%; }
        .app-title h1 {
            font-family: 'UnifrakturMaguntia', 'Uncial Antiqua', cursive;
            font-size: 3em;
            background: linear-gradient(135deg, #b0b0b0 0%, #e8e8e8 20%, #ffffff 35%, #a0a0a0 50%, #d0d0d0 65%, #f5f5f5 80%, #909090 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.7)) drop-shadow(0 0 8px rgba(192,192,192,0.8));
            text-align: center; margin-bottom: 10px;
            
        }
        .poem { color: #c092f9; font-style: italic; font-size: 1.15em; line-height: 1.6; text-shadow: 0 2px 5px rgba(0,0,0,0.5); font-family: 'Marck Script', cursive; margin-bottom: 5px; }
        .poem-author { color: #b8860b; font-size: 0.95em; margin-bottom: 20px; font-style: normal; font-family: 'Caveat', cursive; }
        .card {
            background-image: url('/static/card_bg.jpg');
            background-size: cover;
            background-color: rgba(30, 20, 10, 0.6);
            background-blend-mode: overlay;
            border: 1px solid #5a5a5a;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
            backdrop-filter: blur(10px);
        }
        label { display: block; margin-top: 18px; color: #256057; font-size: 1.2em; font-family: 'Caveat', cursive; }
        input, select { width: 100%; padding: 12px; margin-top: 6px; background: #1c1c1c; border: 1px solid #444; border-radius: 10px; color: #fff; font-size: 16px; font-family: 'Cormorant Infant', serif; }
        input:focus { outline: none; border-color: #b8860b; box-shadow: 0 0 10px rgba(184, 134, 11, 0.4); }
        .row { display: flex; gap: 12px; } .row > div { flex: 1; }
        button {
            background: linear-gradient(135deg, #b8860b, #d4af37);
            color: #1a1a1a; border: none; padding: 14px 30px; font-size: 18px; font-weight: bold;
            border-radius: 12px; cursor: pointer; margin-top: 25px; width: 100%; font-family: 'Cormorant Infant', serif; text-transform: uppercase;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(184, 134, 11, 0.5); }
        .loading { text-align: center; color: #d4af37; margin-top: 25px; font-style: italic; }
        #suggestions {
            position: absolute; background: #1c1c1c; border: 1px solid #444; border-radius: 10px;
            width: 100%; max-height: 200px; overflow-y: auto; z-index: 1000; margin-top: 4px; display: none;
        }
        .suggestion-item { padding: 10px; cursor: pointer; border-bottom: 1px solid #333; }
        .suggestion-item:hover { background: #2a2a2a; }
        .hint { font-size: 0.85em; color: #888; margin-top: 4px; }
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
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }
    </style>
</head>

<body>
    <div id="overlay">
        <div class="sign-emoji" id="signEmoji"></div>
        <div class="sign-name" id="signName"></div>
    
    </div>
    <div class="container">
        <div class="app-title"><h1>Liber Astrodum</h1></div>
        <div class="poem">Спроси у Сатурна о будущей горсти беды<br>И он не обманет, как люди – меняя обличье.<br>О радостной встрече - Юпитера скажут следы<br>(Где Кронос молчит, там от Зевса исходит величье)</div>
        <div class="poem-author">— Олаф Халди</div>

        <!-- НАЧАЛО: Оборачиваем форму в контейнер -->
        <div id="formContainer">
            <h3 style="color: #d4af37; font-family: 'Uncial Antiqua', cursive; text-align: center; margin-bottom: 20px;">☽ Лунар — Прогноз на месяц</h3>
            <div class="row">
                <div><label>Год рождения</label><input type="number" id="natalYear" value="1991"></div>
                <div><label>Месяц</label><input type="number" id="natalMonth" value="2"></div>
                <div><label>День</label><input type="number" id="natalDay" value="14"></div>
            </div>
            <div class="row">
                <div><label>Час рождения</label><input type="number" id="natalHour" value="6"></div>
                <div><label>Минуты</label><input type="number" id="natalMinute" value="55"></div>
            </div>
            <div style="position: relative;">
                <label>Город рождения</label>
                <input type="text" id="birthCity" value="Дубно" placeholder="Начните вводить город...">
                <div id="suggestions" style="display:none;"></div>
            </div>
            <div style="position: relative; margin-top: 18px;">
                <label>Место встречи лунара (где вы сейчас)</label>
                <input type="text" id="lunarCity" value="Ровно" placeholder="Начните вводить город...">
                <div id="lunarSuggestions" style="display:none;"></div>
            </div>
            <div style="display: flex; gap: 10px; margin-top: 18px;">
                <div style="flex: 1;"><label>Год прогноза</label><input type="number" id="lunarYear" value="2026"></div>
                <div style="flex: 1;"><label>Месяц прогноза</label><input type="number" id="lunarMonth" value="8" min="1" max="12"></div>
            </div>
            <button onclick="askLunar()">Построить Лунар</button>
            <div id="lunarResult" style="margin-top: 20px; display: none;"></div>
        </div>
        <div id="result" style="display: none; margin-top: 20px;">
            <canvas id="chart" width="300" height="300"></canvas>
            <div id="planetList"></div>
        </div>

    </div>
    </div>

<script>
    // --- Заставка и цитаты ---
    const signEmojis = {
        'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊',
        'Cancer': '♋', 'Leo': '♌', 'Virgo': '♍',
        'Libra': '♎', 'Scorpio': '♏', 'Sagittarius': '♐',
        'Capricorn': '♑', 'Aquarius': '♒', 'Pisces': '♓'
    };
    const signNamesRu = {
        'Aries': 'Овен', 'Taurus': 'Телец', 'Gemini': 'Близнецы',
        'Cancer': 'Рак', 'Leo': 'Лев', 'Virgo': 'Дева',
        'Libra': 'Весы', 'Scorpio': 'Скорпион', 'Sagittarius': 'Стрелец',
        'Capricorn': 'Козерог', 'Aquarius': 'Водолей', 'Pisces': 'Рыбы'
    };
    const signMottos = {
        'Aries': '«Я — первый луч рассвета, пробуждающий мир к действию.»',
        'Taurus': '«Я — плодородная земля, что превращает семя в древо жизни.»',
        'Gemini': '«Я — мост между мирами, где слово обретает плоть.»',
        'Cancer': '«Я — колыбель души, хранящая память всех начал.»',
        'Leo': '«Я — свет, что зажигает другие светильники, не теряя себя.»',
        'Virgo': '«Я — служитель порядка, превращающий хаос в исцеление.»',
        'Libra': '«Я — точка равновесия, где встречаются свет и тень.»',
        'Scorpio': '«Я — пламя, сжигающее старое, чтобы из пепла восстало новое.»',
        'Sagittarius': '«Я — стрела, пущенная в бесконечность, ищущая истину.»',
        'Capricorn': '«Я — вершина, к которой ведут десять тысяч шагов.»',
        'Aquarius': '«Я — вода жизни, изливающаяся на жаждущее человечество.»',
        'Pisces': '«Я — океан, где растворяются все границы и рождается вера.»'
    };
    const signMottoAuthor = '— Алиса Бейли, «Эзотерическая астрология»';

    function showOverlay(signKey) {
        const emoji = signEmojis[signKey] || '❓';
        const name = signNamesRu[signKey] || signKey;
        const motto = signMottos[signKey] || '';
        
        document.getElementById('signEmoji').innerHTML = emoji;
        document.getElementById('signName').textContent = name;
        
        const oldMotto = document.getElementById('signMotto');
        const oldAuthor = document.getElementById('signMottoAuthor');
        if (oldMotto) oldMotto.remove();
        if (oldAuthor) oldAuthor.remove();
        
        const mottoElement = document.createElement('div');
        mottoElement.id = 'signMotto';
        mottoElement.style.cssText = 'color: #d4af37; font-style: italic; font-size: 1.2em; margin-top: 15px; text-align: center; max-width: 450px; line-height: 1.5; text-shadow: 0 0 10px rgba(212, 175, 55, 0.3);';
        mottoElement.textContent = motto;
        document.getElementById('overlay').appendChild(mottoElement);
        
        const authorElement = document.createElement('div');
        authorElement.id = 'signMottoAuthor';
        authorElement.style.cssText = 'color: #b8860b; font-size: 0.9em; margin-top: 8px; text-align: center; font-style: normal;';
        authorElement.textContent = signMottoAuthor;
        document.getElementById('overlay').appendChild(authorElement);
        
        document.getElementById('overlay').style.display = 'flex';
        setTimeout(() => { document.getElementById('overlay').style.display = 'none'; }, 10000);
    }

    // --- Координаты по умолчанию ---
    let birthLat = 50.4188;
    let birthLon = 25.7456;
    let lunarLat = 50.6199;
    let lunarLon = 26.2516;

    // --- Поиск города рождения ---
    const birthCityInput = document.getElementById('birthCity');
    const suggestionsBox = document.getElementById('suggestions');
    birthCityInput.addEventListener('input', function() {
        const query = this.value.trim();
        if (query.length < 2) { suggestionsBox.style.display = 'none'; return; }
        fetch(`/api/city-search?q=${encodeURIComponent(query)}`)
            .then(r => r.json())
            .then(data => {
                suggestionsBox.innerHTML = '';
                if (!data.length) {
                    suggestionsBox.innerHTML = '<div class="suggestion-item">Ничего не найдено</div>';
                    suggestionsBox.style.display = 'block';
                    return;
                }
                data.forEach(place => {
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = place.display_name;
                    div.addEventListener('click', function() {
                        birthLat = place.lat;
                        birthLon = place.lon;
                        birthCityInput.value = place.display_name;
                        suggestionsBox.style.display = 'none';
                    });
                    suggestionsBox.appendChild(div);
                });
                suggestionsBox.style.display = 'block';
            });
    });
    document.addEventListener('click', function(e) {
        if (!birthCityInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = 'none';
        }
    });

    // --- Поиск места встречи ---
    const lunarCityInput = document.getElementById('lunarCity');
    const lunarSuggestionsBox = document.getElementById('lunarSuggestions');
    lunarCityInput.addEventListener('input', function() {
        const query = this.value.trim();
        if (query.length < 2) { lunarSuggestionsBox.style.display = 'none'; return; }
        fetch(`/api/city-search?q=${encodeURIComponent(query)}`)
            .then(r => r.json())
            .then(data => {
                lunarSuggestionsBox.innerHTML = '';
                if (!data.length) {
                    lunarSuggestionsBox.innerHTML = '<div class="suggestion-item">Ничего не найдено</div>';
                    lunarSuggestionsBox.style.display = 'block';
                    return;
                }
                data.forEach(place => {
                    const div = document.createElement('div');
                    div.className = 'suggestion-item';
                    div.textContent = place.display_name;
                    div.addEventListener('click', function() {
                        lunarLat = place.lat;
                        lunarLon = place.lon;
                        lunarCityInput.value = place.display_name;
                        lunarSuggestionsBox.style.display = 'none';
                    });
                    lunarSuggestionsBox.appendChild(div);
                });
                lunarSuggestionsBox.style.display = 'block';
            });
    });
    document.addEventListener('click', function(e) {
        if (!lunarCityInput.contains(e.target) && !lunarSuggestionsBox.contains(e.target)) {
            lunarSuggestionsBox.style.display = 'none';
        }
    });

    // --- Запрос лунара ---
    async function askLunar() {
        const natalYear = document.getElementById('natalYear').value;
        const natalMonth = document.getElementById('natalMonth').value;
        const natalDay = document.getElementById('natalDay').value;
        const natalHour = document.getElementById('natalHour').value || 12;
        const natalMinute = document.getElementById('natalMinute').value || 0;
        const year = document.getElementById('lunarYear').value;
        const month = document.getElementById('lunarMonth').value || 1;

        const resultBlock = document.getElementById('lunarResult');
        resultBlock.style.display = 'block';
        resultBlock.innerHTML = '<div class="loading">Звёзды советуют...</div>';

        const params = new URLSearchParams({
            year, month,
            natal_year: natalYear, natal_month: natalMonth, natal_day: natalDay,
            natal_hour: natalHour, natal_minute: natalMinute,
            lat: lunarLat, lon: lunarLon,
            birth_lat: birthLat, birth_lon: birthLon
        });

        try {
            const response = await fetch('/api/v1/lunar?' + params.toString());
            const data = await response.json();
                        // Скрываем форму и показываем холст для результатов
            document.getElementById('lunarCard').style.display = 'none';
            document.getElementById('result').style.display = 'block';

            // --- Строим таблицу планет ---
            let planetsHtml = '<h3>Планеты в знаках</h3><ul>';
            const planets = data.analysis.chart.planets;
            for (const [name, info] of Object.entries(planets)) {
                const emoji = signEmojis[info.sign] || '';
                planetsHtml += `<li>${emoji} ${name}: ${info.degree}° ${info.sign}</li>`;
            }
            planetsHtml += '</ul>';

            // --- Строим список домов ---
            let housesHtml = '<h3>Дома</h3><ul>';
            const houses = data.analysis.chart.houses;
            for (const [num, info] of Object.entries(houses)) {
                if (parseInt(num) >= 1 && parseInt(num) <= 12) {
                    housesHtml += `<li>Дом ${num}: ${info.degree}° ${info.sign}</li>`;
                }
            }
            housesHtml += '</ul>';

            // --- Показываем результат ---
            resultBlock.innerHTML = `
                <div class="tech-panel">
                    ${planetsHtml}
                    ${housesHtml}
                </div>
                        // Рисуем диаграмму
        const planets = data.analysis.chart.planets;
        const labels = Object.keys(planets);
        const longitudes = Object.values(planets).map(p => p.longitude);

        const ctx = document.getElementById('chart').getContext('2d');
        new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Планеты',
                    data: longitudes.map((lon, i) => ({x: Math.cos(lon * Math.PI / 180) * 100, y: Math.sin(lon * Math.PI / 180) * 100})),
                    backgroundColor: 'gold',
                    pointRadius: 5
                }]
            },
            options: {
                scales: {
                    x: { display: false },
                    y: { display: false }
                },
                plugins: { legend: { display: false } }
            }
        });
                <div class="details">${data.interpretation.replace(/\n/g, '<br>')}</div>
            `;
            showOverlay('Aquarius'); // Временный пример
        } catch (e) {
            resultBlock.innerHTML = '<div class="verdict">Ошибка соединения со звёздами</div>';
        }
    }
</script>
    <div id="result" style="display: none; margin-top: 20px;"><div id="result" style="display: none; margin-top: 20px;">
    <canvas id="chart" width="300" height="300"></canvas>
    <div id="planetList"></div>
</div>
</div>
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
    natal_hour: int = Query(12),
    natal_minute: int = Query(0),
    lat: float = Query(50.45),          # место встречи
    lon: float = Query(30.52),
    birth_lat: float = Query(50.45),    # место рождения
    birth_lon: float = Query(30.52),
):
    """Лунар через полный конвейер Liber Astrodum 2.0."""
    import swisseph as swe
    from builders.lunar_builder import build_lunar_chart
    from core.pipeline import run_full_pipeline
    from core.prompt_builder import build_prompt_from_dict
    from ai import generate

    
        # 1. Находим натальную Луну с точным историческим UTC-смещением
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
    print(f"[NATAL] Natal Moon longitude: {natal_moon_longitude:.4f}°")

    # 2. Строим лунарную карту через ПРОФЕССИОНАЛЬНЫЙ БИЛДЕР
    chart = build_lunar_chart(
        natal_moon_longitude,
        year, month,
        lat, lon,
        natal_month=natal_month,
        natal_day=natal_day
    )

    # 3. Прогон через новое ядро
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
    