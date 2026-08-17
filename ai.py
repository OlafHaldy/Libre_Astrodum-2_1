import os
import time
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

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

    try:
        logger.info("Trying Groq...")
        return _call_groq(prompt_text)
    except AIError as e:
        logger.warning("Groq failed: %s", e)

    try:
        logger.info("Trying DeepSeek...")
        return _call_deepseek(prompt_text)
    except AIError as e:
        logger.warning("DeepSeek failed: %s", e)

    try:
        logger.info("Trying Gemini...")
        return _call_gemini(prompt_text)
    except AIError as e2:
        logger.warning("Gemini failed: %s", e2)
        raise AIError("All AI providers unavailable, falling back to autonomous engine.")


# ===== КОРОТКАЯ ГЕНЕРАЦИЯ ДЛЯ КЛЮЧА К ЗНАКУ =====

def _call_groq_short(prompt):
    """Groq с ограничением на короткий ответ (как основная, но с max_tokens=60)."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise AIError("GROQ_API_KEY не задан")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # === ТОТ ЖЕ ФОРМАТ, ЧТО В _call_groq() ===
    payload = {
        "model": "llama-3.3-70b-versatile",  # ← та же модель, что в основной
        "messages": [{"role": "user", "content": prompt}],  # ← БЕЗ system!
        "temperature": 0.7,
        "max_tokens": 3000,  # ← только это отличается
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)

    if resp.status_code in (400, 401, 403, 404, 413):
        logger.error("Groq short error %s: %s", resp.status_code, resp.text[:300])
        raise AIError(f"Groq short unavailable ({resp.status_code})")

    resp.raise_for_status()

    try:
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise AIError(f"Groq short returned invalid response: {e}")


def _call_deepseek_short(prompt):
    """DeepSeek с ограничением на короткий ответ."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise AIError("DEEPSEEK_API_KEY не задан")

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 60,
        "temperature": 0.8,
    }

    resp = requests.post(url, headers=headers, json=data, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _call_gemini_short(prompt):
    """Gemini с ограничением на короткий ответ."""
    import google.generativeai as genai

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise AIError("GEMINI_API_KEY не задан")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": 60, "temperature": 0.8},
    )
    return response.text.strip()


def generate_short(prompt) -> str:
    """
    Генерация короткого текста для /api/v1/key.
    С цепочкой fallback: Groq → DeepSeek → Gemini.
    """
    if isinstance(prompt, dict):
        prompt_text = prompt.get("prompt_text") or prompt.get("content") or ""
    else:
        prompt_text = str(prompt)

    system_prompt = (
        "Ты — генератор афоризмов. "
        "Твоя задача — создать ОДНУ короткую афористическую фразу. "
        "Ответ должен содержать максимум 10 слов. "
        "Только одна фраза. "
        "Никаких объяснений, комментариев, вступлений, "
        "пояснений, вариантов или дополнительного текста."
    )

    full_prompt = f"{system_prompt}\n\n{prompt_text}"

    # 1. Пробуем Groq
    try:
        logger.info("Trying Groq (short)...")
        return _call_groq_short(full_prompt)
    except Exception as e:
        logger.warning("Groq short failed: %s", e)

    # 2. Пробуем DeepSeek
    try:
        logger.info("Trying DeepSeek (short)...")
        return _call_deepseek_short(full_prompt)
    except Exception as e:
        logger.warning("DeepSeek short failed: %s", e)

    # 3. Пробуем Gemini
    try:
        logger.info("Trying Gemini (short)...")
        return _call_gemini_short(full_prompt)
    except Exception as e:
        logger.warning("Gemini short failed: %s", e)
        raise AIError("All AI providers unavailable for short generation.")



