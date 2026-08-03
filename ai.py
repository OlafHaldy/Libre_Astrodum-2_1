import os
import time
import logging
import requests

logger = logging.getLogger(__name__)

class AIError(Exception):
    pass

TIMEOUT = 120

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

def generate(prompt) -> str:
    # Умный разбор: если prompt — словарь (как из prompt_engine), берём prompt_text
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
            logger.info("Trying Gemini...")
            return _call_gemini(prompt_text)
        except AIError as e2:
            logger.warning("Gemini failed: %s", e2)
            raise AIError("All AI providers unavailable, falling back to autonomous engine.")