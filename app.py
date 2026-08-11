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
        #suggestions, #lunarSuggestions {
            position: absolute; background: #1c1c1c; border: 1px solid #444; border-radius: 10px;
            width: 100%; max-height: 200px; overflow-y: auto; z-index: 1000; margin-top: 4px; display: none;
        }
        .suggestion-item { padding: 10px; cursor: pointer; border-bottom: 1px solid #333; }
        .suggestion-item:hover { background: #2a2a2a; }
        .hint { font-size: 0.85em; color: #888; margin-top: 4px; }
        #overlay {
            position: fixed; top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(9, 10, 15, 0.95);
            display: none; justify-content: center; align-items: center;
            z-index: 1000; flex-direction: column;
        }
        #overlay .sign-emoji { font-size: 100px; animation: float 2s ease-in-out infinite; }
        #overlay .sign-name {
            font-family: 'Uncial Antiqua', cursive; font-size: 2em;
            color: #d4af37; margin-top: 15px;
            text-shadow: 0 0 15px rgba(212, 175, 55, 0.5);
        }
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-15px); }
        }
        .planet-list table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .planet-list th, .planet-list td { padding: 8px; text-align: left; border-bottom: 1px solid #444; }
        .planet-list th { color: #d4af37; }
        .interpretation-text { margin-top: 20px; line-height: 1.7; }
        /* ===== ЛУНАР — ОФОРМЛЕНИЕ ОТЧЁТА ===== */

#lunarPassport,
#planetList,
#aspectList,
#houseList,
#interpretationText {
    margin-top: 24px;
}
/* ===== БЛОКИ ИНТЕРПРЕТАЦИИ ===== */

.interpretation-block {
    position: relative;
    margin: 18px 0;
    padding: 20px 22px 22px 24px;

    background:
        linear-gradient(
            135deg,
            rgba(35, 35, 35, 0.78),
            rgba(10, 10, 10, 0.58)
        );

    border: 1px solid rgba(212, 175, 55, 0.20);
    border-left: 3px solid rgba(212, 175, 55, 0.55);
    border-radius: 10px;

    box-shadow:
        0 4px 18px rgba(0, 0, 0, 0.22);

    transition:
        border-color 0.25s ease,
        background 0.25s ease,
        transform 0.25s ease;
}

/* Небольшой эффект при наведении */
.interpretation-block:hover {
    border-color: rgba(212, 175, 55, 0.38);
    border-left-color: rgba(212, 175, 55, 0.85);
    background:
        linear-gradient(
            135deg,
            rgba(42, 42, 42, 0.82),
            rgba(12, 12, 12, 0.64)
        );
}

/* Заголовок блока */
.interpretation-block-title {
    margin-bottom: 13px;

    color: #d4af37;
    font-size: 1.15rem;
    font-weight: 600;

    letter-spacing: 0.06em;
    text-transform: uppercase;

    padding-bottom: 9px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.20);
}

/* Сам текст */
.interpretation-block-text {
    color: #e4e4e4;

    font-size: 1rem;
    line-height: 1.8;

    text-align: left;
}

/* Первый блок — главный */
.interpretation-block:first-child {
    border-left-color: #d4af37;
    background:
        linear-gradient(
            135deg,
            rgba(55, 45, 20, 0.32),
            rgba(15, 15, 15, 0.62)
        );
}

.interpretation-block:first-child .interpretation-block-title {
    font-size: 1.25rem;
}

/* Последний блок — итог */
.interpretation-block:last-child {
    margin-top: 24px;
    border-left-color: rgba(212, 175, 55, 0.75);
}

/* Мобильная версия */
@media (max-width: 600px) {

    .interpretation-block {
        margin: 14px 0;
        padding: 16px 16px 18px 18px;
    }

    .interpretation-block-title {
        font-size: 1rem;
        letter-spacing: 0.04em;
    }

    .interpretation-block:first-child .interpretation-block-title {
        font-size: 1.08rem;
    }

    .interpretation-block-text {
        font-size: 0.95rem;
        line-height: 1.7;
    }
}

/* Заголовки секций */
#lunarPassport::before {
    content: "✦ Паспорт лунара";
}

#planetList::before {
    content: "✦ Планеты";
}

#aspectList::before {
    content: "✦ Аспекты";
}

#houseList::before {
    content: "✦ Дома";
}

#interpretationText::before {
    content: "✦ Интерпретация";
}

#lunarPassport::before,
#planetList::before,
#aspectList::before,
#houseList::before,
#interpretationText::before {
    display: block;
    margin-bottom: 14px;
    color: #d4af37;
    font-size: 1.35rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}

/* Все таблицы отчёта */
#lunarPassport table,
#planetList table,
#aspectList table,
#houseList table {
    width: 100%;
    border-collapse: collapse;
    background: rgba(0, 0, 0, 0.18);
    border: 1px solid rgba(212, 175, 55, 0.22);
    border-radius: 10px;
    overflow: hidden;
}

/* Ячейки */
#lunarPassport td,
#planetList td,
#planetList th,
#aspectList td,
#aspectList th,
#houseList td,
#houseList th {
    padding: 11px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    text-align: left;
}

/* Заголовки таблиц */
#planetList th,
#aspectList th,
#houseList th {
    color: #d4af37;
    font-weight: 600;
    background: rgba(212, 175, 55, 0.06);
}

/* Последняя строка без нижней линии */
#lunarPassport tr:last-child td,
#planetList tr:last-child td,
#aspectList tr:last-child td,
#houseList tr:last-child td {
    border-bottom: none;
}

/* Подсветка строк при наведении */
#planetList tr:hover,
#aspectList tr:hover,
#houseList tr:hover {
    background: rgba(212, 175, 55, 0.05);
}

/* Левая колонка паспорта */
#lunarPassport td:first-child {
    width: 38%;
    color: #c9b878;
}

/* Значения паспорта */
#lunarPassport td:last-child {
    color: #f0f0f0;
}

/* Интерпретация */
#interpretationText {
    margin-top: 30px;
    padding: 22px 24px;
    background: rgba(0, 0, 0, 0.22);
    border: 1px solid rgba(212, 175, 55, 0.18);
    border-radius: 12px;
    line-height: 1.8;
    color: #e5e5e5;
}

/* Заголовок интерпретации внутри панели */
#interpretationText::before {
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(212, 175, 55, 0.25);
}

/* Мобильная версия */
@media (max-width: 600px) {

    #lunarPassport td,
    #planetList td,
    #planetList th,
    #aspectList td,
    #aspectList th,
    #houseList td,
    #houseList th {
        padding: 9px 8px;
        font-size: 0.9rem;
    }

    #lunarPassport td:first-child {
        width: 45%;
    }

    #interpretationText {
        padding: 18px 15px;
        line-height: 1.7;
    }
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
        </div>

        <div id="result" style="display: none; margin-top: 20px; width: 100%;">
            <div style="background: rgba(28, 28, 28, 0.8); border: 1px solid #444; border-radius: 14px; padding: 20px; backdrop-filter: blur(5px);">
                <h3 style="color: #d4af37; font-family: 'Uncial Antiqua', cursive; margin-bottom: 15px;">☽ Лунар — Результат</h3>
                <div id="wheelContainer"></div>
                <div id="lunarPassport"
     style="
        margin:20px 0;
        padding:16px;
        border:1px solid #555;
        border-radius:10px;
        background:rgba(0,0,0,.25);
        color:#ddd;">
</div>
                


                <div id="planetList"></div>
                <div id="aspectList"></div>
                <div id="houseList"></div>

                <div id="interpretationText"></div>
            </div>
        </div>
    </div>

    <script>
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

        let birthLat = 50.4188, birthLon = 25.7456;
        let lunarLat = 50.6199, lunarLon = 26.2516;

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
                            birthLat = place.lat; birthLon = place.lon;
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
                            lunarLat = place.lat; lunarLon = place.lon;
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

    async function askLunar() {
        const planetNames = {
            Sun: 'Солнце', Moon: 'Луна', Mercury: 'Меркурий',
            Venus: 'Венера', Mars: 'Марс', Jupiter: 'Юпитер', Saturn: 'Сатурн'
        };
        const signNames = {
            Aries: 'Овен', Taurus: 'Телец', Gemini: 'Близнецы', Cancer: 'Рак',
            Leo: 'Лев', Virgo: 'Дева', Libra: 'Весы', Scorpio: 'Скорпион',
            Sagittarius: 'Стрелец', Capricorn: 'Козерог', Aquarius: 'Водолей', Pisces: 'Рыбы'
        };
        const aspectNames = {
            conjunction: 'соединение', opposition: 'оппозиция', square: 'квадрат',
            trine: 'тригон', sextile: 'секстиль', quincunx: 'квинконс'
        };
        const aspectSymbols = {
            conjunction: '☌', opposition: '☍', square: '□',
            trine: '△', sextile: '⚹', quincunx: '⚻'
        };

        const natalYear = document.getElementById('natalYear').value;
        const natalMonth = document.getElementById('natalMonth').value;
        const natalDay = document.getElementById('natalDay').value;
        const natalHour = document.getElementById('natalHour').value || 12;
        const natalMinute = document.getElementById('natalMinute').value || 0;
        const year = document.getElementById('lunarYear').value;
        const month = document.getElementById('lunarMonth').value || 1;

        // Скрываем форму и показываем анимацию загрузки
        document.getElementById('formContainer').style.display = 'none';
        const resultBlock = document.getElementById('result');
        resultBlock.style.display = 'block';
        resultBlock.innerHTML = '<div class="loading">Звёзды складывают узор...</div>';

        const params = new URLSearchParams({
            year, month,
            natal_year: natalYear, natal_month: natalMonth, natal_day: natalDay,
            natal_hour: natalHour, natal_minute: natalMinute,
            lat: lunarLat, lon: lunarLon,
            birth_lat: birthLat, birth_lon: birthLon,
            birth_city: document.getElementById("birthCity").value,
            lunar_city: document.getElementById("lunarCity").value
        });

        try {
            const response = await fetch('/api/v1/lunar?' + params.toString());
            const data = await response.json();

            // Показываем заставку
            // Определяем знак для заставки по Луне (главная планета лунара)
const sunSign = data.natal_sun_sign || 'Aquarius';
showOverlay(sunSign);
            // Паспорт лунара
            const person = data.report?.person || {};
            const calc = data.report?.calculation || {};
            const passportHtml = `
                <div style="margin:20px 0;padding:18px;border:1px solid #6f5620;border-radius:12px;background:rgba(20,20,20,.55);color:#ddd;line-height:1.7;">
                    <h3 style="margin-top:0;color:#d4af37;">✦ Паспорт лунара</h3>
                    <table style="width:100%;border-collapse:collapse;">
                        <tr><td><b>Дата рождения</b></td><td>${person.birth_date || '—'}</td></tr>
                        <tr><td><b>Дата лунарного возвращения</b></td><td>${calc.return_datetime || '—'}</td></tr>
                        <tr><td><b>Период действия</b></td><td>${calc.target_month || ''}.${calc.target_year || ''}</td></tr>
                        <tr><td><b>Место построения</b></td><td>${calc.lunar_city || '—'}</td></tr>
                        <tr><td><b>Система домов</b></td><td>${calc.house_system || '—'}</td></tr>
                    </table>
                </div>
            `;

            // Колесо
            const wheelHtml = data.wheel ? `<div id="wheelContainer">${data.wheel}</div>` : '';

            // Таблица планет
            let planetListHtml = '<h3 style="color:#d4af37;">Планеты в знаках</h3>';
            planetListHtml += '<table style="width:100%;color:#f0f0f0;border-collapse:collapse;">';
            planetListHtml += '<tr><th>Планета</th><th>Знак</th><th>Градус</th></tr>';
            if (data.planets) {
                for (const [name, info] of Object.entries(data.planets)) {
                    const planet = planetNames[name] || name;
                    const sign = signNames[info.sign] || info.sign;
                    planetListHtml += `<tr><td>${planet}</td><td>${sign}</td><td>${info.degree}°</td></tr>`;
                }
            }
            planetListHtml += '</table>';

            // Таблица домов
            let houseListHtml = '<h3 style="color:#d4af37;margin-top:20px;">Дома</h3>';
            houseListHtml += '<table style="width:100%;color:#f0f0f0;border-collapse:collapse;">';
            houseListHtml += '<tr><th>Дом</th><th>Знак</th><th>Градус</th></tr>';
            for (let i = 1; i <= 12; i++) {
                const house = data.houses?.[i];
                if (house) {
                    const sign = signNames[house.sign] || house.sign;
                    houseListHtml += `<tr><td>${i}</td><td>${sign}</td><td>${house.degree?.toFixed(2)}°</td></tr>`;
                }
            }
            const asc = data.houses?.Ascendant;
            const mc = data.houses?.MC;
            if (asc) {
                const sign = signNames[asc.sign] || asc.sign;
                houseListHtml += `<tr><td><b>ASC</b></td><td>${sign}</td><td>${asc.degree?.toFixed(2)}°</td></tr>`;
            }
            if (mc) {
                const sign = signNames[mc.sign] || mc.sign;
                houseListHtml += `<tr><td><b>MC</b></td><td>${sign}</td><td>${mc.degree?.toFixed(2)}°</td></tr>`;
            }
            houseListHtml += '</table>';

            // Таблица аспектов
            let aspectListHtml = '';
            if (data.aspects && data.aspects.length > 0) {
                aspectListHtml = '<h3 style="color:#d4af37;margin-top:20px;">Аспекты</h3>';
                aspectListHtml += '<table style="width:100%;color:#f0f0f0;border-collapse:collapse;">';
                aspectListHtml += '<tr><th>Планета 1</th><th>Аспект</th><th>Планета 2</th><th>Угол</th></tr>';
                for (const aspect of data.aspects) {
                    const p1 = planetNames[aspect.planet1] || aspect.planet1;
                    const p2 = planetNames[aspect.planet2] || aspect.planet2;
                    const name = aspectNames[aspect.type] || aspect.type;
                    const symbol = aspectSymbols[aspect.type] || '';
                    aspectListHtml += `<tr><td>${p1}</td><td>${symbol} ${name}</td><td>${p2}</td><td>${aspect.angle}°</td></tr>`;
                }
                aspectListHtml += '</table>';
            }

            // Интерпретация с парсингом секций
            // Интерпретация с парсингом секций
            const interpretationText = data.interpretation || '';
            console.log("INTERPRETATION RAW:", interpretationText.substring(0, 500));
            
            const sectionRegex = /\[SECTION:(MAIN|STRENGTHS|WEAKNESSES|PSYCHOLOGY|TENSION|HERMETIC|TRANSFORMATION|CONCLUSION)\]\s*/g;
            const interpretationSections = [];
            let match;
            while ((match = sectionRegex.exec(interpretationText)) !== null) {
                interpretationSections.push({
                    key: match[1],
                    start: sectionRegex.lastIndex,
                    markerStart: match.index
                });
            }
            
            console.log("SECTIONS FOUND:", interpretationSections.length);
            
            let interpretationHtml = '';
            
            if (interpretationSections.length > 0) {
                // Есть маркеры — парсим по секциям
                const interpretationTitles = {
                    MAIN: 'Главная тема', STRENGTHS: 'Сильные стороны', WEAKNESSES: 'Слабые места',
                    PSYCHOLOGY: 'Психологический слой', TENSION: 'Внутреннее напряжение',
                    HERMETIC: 'Герметический смысл', TRANSFORMATION: 'Путь преобразования', CONCLUSION: 'Итог'
                };
                for (let i = 0; i < interpretationSections.length; i++) {
                    const section = interpretationSections[i];
                    const endPos = i + 1 < interpretationSections.length
                        ? interpretationSections[i + 1].markerStart
                        : interpretationText.length;
                    const sectionText = interpretationText.slice(section.start, endPos).trim();
                    if (sectionText) {
                        const title = interpretationTitles[section.key] || section.key;
                        interpretationHtml += `
                            <div class="interpretation-block">
                                <div class="interpretation-block-title">✦ ${title}</div>
                                <div class="interpretation-block-text">${sectionText.replace(/\n/g, '<br>')}</div>
                            </div>
                        `;
                    }
                }
            } else {
                // Нет маркеров — показываем как есть, убирая маркеры если они в другом формате
                const cleanText = interpretationText
                    .replace(/\[SECTION:\w+\]\s*/g, '')
                    .replace(/SECTION:\w+\s*/g, '')
                    .trim();
                
                if (cleanText) {
                    interpretationHtml = `
                        <div class="interpretation-block">
                            <div class="interpretation-block-text">${cleanText.replace(/\n/g, '<br>')}</div>
                        </div>
                    `;
                } else {
                    interpretationHtml = '<p>Интерпретация временно недоступна.</p>';
                }
            }
            // Собираем всё вместе
            resultBlock.innerHTML = `
                <div style="background: rgba(28, 28, 28, 0.8); border: 1px solid #444; border-radius: 14px; padding: 20px; backdrop-filter: blur(5px);">
                    <h3 style="color: #d4af37; font-family: 'Uncial Antiqua', cursive; margin-bottom: 15px;">☽ Лунар — Результат</h3>
                    ${wheelHtml}
                    ${passportHtml}
                    ${planetListHtml}
                    ${houseListHtml}
                    ${aspectListHtml}
                    <h3 style="color: #d4af37; margin-top: 20px;">Интерпретация</h3>
                    ${interpretationHtml}
                </div>
            `;
        } catch (e) {
            console.error("LUNAR ERROR:", e);
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
   