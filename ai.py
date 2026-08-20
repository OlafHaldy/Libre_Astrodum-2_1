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


def _call_groq(prompt_text, model="openai/gpt-oss-120b", temperature=0.7, max_tokens=3000):
    # ... остальное без изменений
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

    model = "gemini-2.5-flash"  # ← актуальная модель
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    # ... (остальной код без изменений)
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
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise AIError("GROQ_API_KEY не задан")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openai/gpt-oss-120b",  # ← новая модель
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise AIError(f"Groq short returned invalid response: {e}")


def generate_short(prompt) -> str:
    """
    Генерация короткого текста для /api/v1/key.
    """
    if isinstance(prompt, dict):
        prompt_text = prompt.get("prompt_text") or prompt.get("content") or ""
    else:
        prompt_text = str(prompt)

    try:
        logger.info("Trying Groq (short)...")
        return _call_groq_short(prompt_text)
    except Exception as e:
        logger.warning("Groq short failed: %s", e)
        raise AIError("Short AI generation unavailable.")
