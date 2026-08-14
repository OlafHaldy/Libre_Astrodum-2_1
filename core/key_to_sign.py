import random
from functools import lru_cache
from data.key_topics import KEY_CATEGORIES, ALL_TOPICS
from ai import generate

SIGN_NAMES_RU = {
    'Aries': 'Овен', 'Taurus': 'Телец', 'Gemini': 'Близнецы',
    'Cancer': 'Рак', 'Leo': 'Лев', 'Virgo': 'Дева',
    'Libra': 'Весы', 'Scorpio': 'Скорпион', 'Sagittarius': 'Стрелец',
    'Capricorn': 'Козерог', 'Aquarius': 'Водолей', 'Pisces': 'Рыбы'
}

@lru_cache(maxsize=200)
def generate_aphorism(sign_ru: str, topic: str) -> str:
    """Генерирует афоризм с кэшированием"""
    
    prompt = f"""Ты — Астродо, хранитель Небесного Архива Liber Astrodum.

Создай афоризм для знака {sign_ru} на тему: {topic}.

Стиль:
- Ровно 2-3 предложения
- Иронично, но не зло
- Философски, с глубиной
- В характере знака {sign_ru}
- Как Шопенгауэр, но для знака зодиака
- Никаких «вас ждёт», «будьте осторожны»

Пример для Водолея на тему «прощание»:
«Если вы решили уйти — погодите, не спешите. Я придержу вам дверь и вызову лифт.»

Не используй markdown. Не добавляй заголовков. Только текст афоризма."""

    try:
        return generate(prompt)
    except:
        return f"Сегодня {sign_ru} молчит. Звёзды говорят тише обычного."


def get_random_topic(category: str = None) -> tuple:
    """Возвращает (категория, тема)"""
    
    if category and category in KEY_CATEGORIES:
        cat_data = KEY_CATEGORIES[category]
        topic = random.choice(cat_data["themes"])
        return category, topic
    else:
        # Выбираем случайную категорию и тему
        cat_name = random.choice(list(KEY_CATEGORIES.keys()))
        cat_data = KEY_CATEGORIES[cat_name]
        topic = random.choice(cat_data["themes"])
        return cat_name, topic


def get_key_aphorism(sign: str, category: str = None) -> dict:
    """Основная функция получения афоризма"""
    
    sign_ru = SIGN_NAMES_RU.get(sign, sign)
    cat_name, topic = get_random_topic(category)
    aphorism = generate_aphorism(sign_ru, topic)
    
    return {
        "sign": sign_ru,
        "category": cat_name,
        "category_icon": KEY_CATEGORIES[cat_name]["icon"],
        "topic": topic,
        "aphorism": aphorism
    }