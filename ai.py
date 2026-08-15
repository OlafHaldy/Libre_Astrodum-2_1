import os
import time
import logging
import requests

logger = logging.getLogger(__name__)


class AIError(Exception):
    pass


TIMEOUT = 120

SECTION_KEYS = [
    "MAIN",
    "STRENGTHS",
    "WEAKNESSES",
    "PSYCHOLOGY",
    "TENSION",
    "HERMETIC",
    "TRANSFORMATION",
    "CONCLUSION",
]


def _normalize_interpretation(text: str) -> str:
    if not text:
        return text
    text = text.replace(r"\:", ":")

    if "[SECTION:MAIN]" in text:
        return text.strip()

    paragraphs = [
        part.strip()
        for part in text.split("\n\n")
        if part.strip()
    ]

    if len(paragraphs) == 8:
        sections = []
        for key, paragraph in zip(SECTION_KEYS, paragraphs):
            sections.append(f"[SECTION:{key}]\n{paragraph}")
        normalized = "\n\n".join(sections)
        logger.info("AI interpretation normalized into 8 sections.")
        return normalized

    logger.warning(
        "AI interpretation has no section markers and contains %s paragraphs; "
        "leaving response unchanged.",
        len(paragraphs),
    )
    return text.strip()


def _call_groq(prompt_text, model="llama-3.3-70b-versatile", temperature=0.7, max_tokens=3000):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise AIError("GROQ_API_KEY не задан")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            logger.warning("Groq connection error: %s", e)
            time.sleep(2 ** attempt)
            continue

        if resp.status_code == 429:
            wait = 2 ** attempt
            logger.warning("Groq quota exceeded, waiting %s sec...", wait)
            time.sleep(wait)
            continue

        if resp.status_code in (400, 401, 403, 404, 413):
            logger.error("Groq error %s: %s", resp.status_code, resp.text[:300])
            raise AIError(f"Groq model {model} unavailable ({resp.status_code})")

        resp.raise_for_status()

        try:
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            raise AIError("Groq returned invalid response.")

    raise AIError("Groq quota exceeded after retries.")


def _call_gemini(prompt_text, temperature=0.7, max_tokens=3000):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AIError("GEMINI_API_KEY не задан")

    model = "gemini-2.0-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }

    for attempt in range(2):
        try:
            resp = requests.post(url, json=payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            logger.warning("Gemini connection error: %s", e)
            time.sleep(2 ** attempt)
            continue

        if resp.status_code == 429:
            wait = 2 ** attempt
            logger.warning("Gemini quota exceeded, waiting %s sec...", wait)
            time.sleep(wait)
            continue

        if resp.status_code in (400, 404):
            logger.error("Gemini error %s: %s", resp.status_code, resp.text[:300])
            raise AIError(f"Gemini model {model} unavailable ({resp.status_code})")

        resp.raise_for_status()

        try:
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            raise AIError("Gemini returned invalid response.")

    raise AIError("Gemini quota exceeded after retries.")


def _call_deepseek(prompt_text, model="deepseek-chat", temperature=0.7, max_tokens=3000):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise AIError("DEEPSEEK_API_KEY не задан")

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        except requests.RequestException as e:
            logger.warning("DeepSeek connection error: %s", e)
            time.sleep(2 ** attempt)
            continue

        if resp.status_code == 429:
            wait = 2 ** attempt
            logger.warning("DeepSeek quota exceeded, waiting %s sec...", wait)
            time.sleep(wait)
            continue

        if resp.status_code in (400, 401, 403, 404, 413):
            logger.error("DeepSeek error %s: %s", resp.status_code, resp.text[:300])
            raise AIError(f"DeepSeek model {model} unavailable ({resp.status_code})")

        resp.raise_for_status()

        try:
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception:
            raise AIError("DeepSeek returned invalid response.")

    raise AIError("DeepSeek quota exceeded after retries.")


def generate(prompt) -> str:
    if isinstance(prompt, dict):
        prompt_text = prompt.get("prompt_text") or prompt.get("content") or ""
    else:
        prompt_text = str(prompt)

    # 1. Пробуем Groq
    try:
        logger.info("Trying Groq...")
        return _call_groq(prompt_text)
    except AIError as e:
        logger.warning("Groq failed: %s", e)

    # 2. Пробуем DeepSeek
    try:
        logger.info("Trying DeepSeek...")
        return _call_deepseek(prompt_text)
    except AIError as e:
        logger.warning("DeepSeek failed: %s", e)

    # 3. Пробуем Gemini
    try:
        logger.info("Trying Gemini...")
        return _call_gemini(prompt_text)
    except AIError as e2:
        logger.warning("Gemini failed: %s", e2)
        raise AIError("All AI providers unavailable, falling back to autonomous engine.")
    def _call_groq_short(prompt):
    """Groq с ограничением на короткий ответ."""
    from groq import Groq
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=30,
        temperature=0.8
    )
    return response.choices[0].message.content

# ===== НОВАЯ ФУНКЦИЯ ДЛЯ КОРОТКИХ ОТВЕТОВ =====

def _call_groq_short(prompt):
    """Groq с ограничением на короткий ответ."""
    from groq import Groq
    import os
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=30,
        temperature=0.8
    )
    return response.choices[0].message.content


def _call_deepseek_short(prompt):
    """DeepSeek с ограничением на короткий ответ."""
    import requests
    import os
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 30,
        "temperature": 0.8
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _call_gemini_short(prompt):
    """Gemini с ограничением на короткий ответ."""
    import google.generativeai as genai
    import os
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 30,
            "temperature": 0.8
        }
    )
    return response.text


def generate_short(prompt) -> str:
    """Генерация короткого ответа (для афоризмов) — максимум 1 предложение."""
    if isinstance(prompt, dict):
        prompt_text = prompt.get("prompt_text") or prompt.get("content") or ""
    else:
        prompt_text = str(prompt)

    # Добавляем системную инструкцию
    system = "Ты — Астродо. Отвечай только ОДНИМ коротким предложением, максимум 10 слов. Без пояснений."
    full_prompt = f"{system}\n\n{prompt_text}"

    # 1. Пробуем Groq (short)
    try:
        logger.info("Trying Groq (short)...")
        return _call_groq_short(full_prompt)
    except Exception as e:
        logger.warning("Groq short failed: %s", e)

    # 2. Пробуем DeepSeek (short)
    try:
        logger.info("Trying DeepSeek (short)...")
        return _call_deepseek_short(full_prompt)
    except Exception as e:
        logger.warning("DeepSeek short failed: %s", e)

    # 3. Пробуем Gemini (short)
    try:
        logger.info("Trying Gemini (short)...")
        return _call_gemini_short(full_prompt)
    except Exception as e:
        logger.warning("Gemini short failed: %s", e)
        raise Exception("All AI providers unavailable for short generation.")