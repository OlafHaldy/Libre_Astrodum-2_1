
from pathlib import Path


PROMPTS_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT_PATH = PROMPTS_DIR / "system_prompt.md"
LIBER_ASTRODO_PATH = PROMPTS_DIR / "liber_astrodo.md"
CANONS_PATH = PROMPTS_DIR / "canons.md"


def load_text(path):
    """Безопасно читает UTF-8 текстовый файл."""
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""


def _load_system_text():
    return "\n\n".join(
        text
        for text in (
            load_text(SYSTEM_PROMPT_PATH),
            load_text(LIBER_ASTRODO_PATH),
            load_text(CANONS_PATH),
        )
        if text
    )


def _language_instruction(lang):
    if lang == "uk":
        return "Пиши українською мовою."
    return "Пиши на русском языке."


def _mode_instruction(mode):
    if mode == "psychological":
        return (
            "Держи психологический фокус: описывай внутренние состояния, "
            "выбор и возможности роста."
        )
    return (
        "Держи герметический фокус: раскрывай связь небесных символов, "
        "времени и человеческого пути."
    )


def _interpretation_instruction():
    return """
СТРУКТУРА ИНТЕРПРЕТАЦИИ

Создай ровно восемь последовательных разделов.

Используй маркеры строго в следующем виде:

[SECTION:MAIN]
[SECTION:STRENGTHS]
[SECTION:WEAKNESSES]
[SECTION:PSYCHOLOGY]
[SECTION:TENSION]
[SECTION:HERMETIC]
[SECTION:TRANSFORMATION]
[SECTION:CONCLUSION]

Не изменяй маркеры.
Не добавляй другие маркеры.
Не используй Markdown-заголовки.
Не используй списки внутри разделов.

Каждый раздел должен добавлять новое измерение и продолжать предыдущий.
Не повторяй одну мысль разными словами.

[SECTION:MAIN]
Раскрой центральный внутренний процесс периода. Не перечисляй механически
планеты, дома, знаки и диспозиторов. Покажи, что происходит с человеком
и почему именно этот процесс становится главным.

[SECTION:STRENGTHS]
Покажи силы карты, которые помогают проходить центральный процесс.
Не перечисляй общие положительные качества планет. Каждая сила должна
иметь собственную функцию в развитии главной темы.

[SECTION:WEAKNESSES]
Покажи, где центральный процесс встречает сопротивление.
Не создавай список недостатков. Покажи, где человек может избегать
необходимого изменения, терять ясность или возвращаться к старой модели.

[SECTION:PSYCHOLOGY]
Покажи, как происходящий процесс может переживаться изнутри:
чувства, сомнения, желания, страхи, внутренние реакции и изменения
восприятия. Не ставь психологических диагнозов и не представляй
возможные реакции как неизбежные факты.

[SECTION:TENSION]
Покажи внутреннее противоречие между действующими силами.
Не описывай обе стороны отдельно. Покажи, чего требует каждая сторона
и почему человеку приходится искать собственную меру между ними.

[SECTION:HERMETIC]
Подними интерпретацию от психологического смысла к более глубокому
внутреннему процессу. Покажи, что может потребовать освобождения,
принятия, созревания, преобразования или соединения.

Используй герметические и алхимические образы только тогда, когда они
действительно следуют из конкретной карты.

Не добавляй красивый символический мотив без основания.
Не превращай герметический слой в набор загадочных фраз.
Читатель должен понимать, какой внутренний процесс описывается.

[SECTION:TRANSFORMATION]
Покажи возможный путь внутреннего преобразования.
Объясни, что человек может принять, отпустить, соединить, выдержать
или изменить в своём отношении к происходящему.
Это не список бытовых советов.

[SECTION:CONCLUSION]
Сведи весь процесс в единый смысл.
Не пересказывай предыдущие разделы.
Не предсказывай неизбежное событие.
Покажи, какое новое отношение к происходящему становится возможным
и где остаётся пространство человеческого выбора.

ФИНАЛЬНОЕ ОГРАНИЧЕНИЕ

Верни только восемь разделов интерпретации.
Не добавляй вступления или заключения вне этих разделов.
"""


def _format_mapping(title, values):
    if not values:
        return f"{title}: нет данных"

    lines = [title]
    lines.extend(f"{name}: {value}" for name, value in values.items())
    return "\n".join(lines)


def _format_list(title, values):
    if not values:
        return f"{title}: нет данных"

    lines = [title]
    lines.extend(f"- {value}" for value in values)
    return "\n".join(lines)


def _build_messages(natal_data, transit_data, question, lang, mode):
    natal_data = natal_data or {}
    transit_data = transit_data or {}
    system_text = _load_system_text()

    system_prompt = f"""{system_text}

{_interpretation_instruction()}
{_mode_instruction(mode)}
{_language_instruction(lang)}
"""

    user_prompt = "\n\n".join(
        [
            _format_mapping(
                "НАТАЛЬНЫЕ ПОЛОЖЕНИЯ:",
                natal_data.get("positions"),
            ),
            _format_mapping(
                "ДОМА ГОРОСКОПА:",
                natal_data.get("houses"),
            ),
            _format_list(
                "НАТАЛЬНЫЕ АСПЕКТЫ:",
                natal_data.get("aspects"),
            ),
            _format_mapping(
                "ТЕКУЩИЕ ТРАНЗИТЫ:",
                transit_data.get("transits"),
            ),
            _format_list(
                "ТРАНЗИТНЫЕ АСПЕКТЫ:",
                transit_data.get("transit_aspects"),
            ),
            f"ВОПРОС ПОЛЬЗОВАТЕЛЯ:\n{question}",
        ]
    )

    return {
        "model": None,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "prompt_text": f"{system_prompt}\n\n{user_prompt}",
    }


def build_prompt(
    natal_data,
    transit_data,
    question,
    lang="ru",
    mode="hermetic",
    *legacy_args,
):
    """Строит сообщения для провайдера и сохраняет совместимость с app.py."""

    if isinstance(lang, (list, tuple)):
        legacy_lang = legacy_args[0] if legacy_args else "ru"

        prompt = _build_messages(
            {
                "positions": natal_data,
                "houses": transit_data,
                "aspects": question,
            },
            {
                "transits": {},
                "transit_aspects": lang,
            },
            legacy_lang,
            "hermetic",
        )

        return prompt["prompt_text"]

    return _build_messages(
        natal_data,
        transit_data,
        question,
        lang,
        mode,
    )

