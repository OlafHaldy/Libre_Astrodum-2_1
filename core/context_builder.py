"""
Liber Astrodum

core/context_builder.py

Prompt Context Builder v1.0.

Преобразует результаты аналитического конвейера
Liber Astrodum в единый структурированный контекст
для последующего Prompt Builder / LLM слоя.

ВАЖНО:

Context Builder НЕ:
    - интерпретирует карту заново;
    - делает новые астрологические выводы;
    - генерирует литературный текст;
    - использует LLM.

Его задача:

    Facts
      ↓
    Priorities
      ↓
    Relations
      ↓
    Patterns
      ↓
    Themes
      ↓
    Semantics
      ↓
    Interpretations
      ↓
    Narrative
      ↓
    Composition
      ↓
    Evidence
      ↓
    PromptContext

PromptContext становится единственным
структурированным входом для Prompt Builder.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum / Astrodum Engine

Версия:
    1.0
"""

from dataclasses import dataclass, field
from typing import Any


# ==========================================================
# КОНСТАНТЫ
# ==========================================================

DEFAULT_MAX_PLANS = 3
DEFAULT_MAX_EVIDENCE = 12
DEFAULT_MAX_KEY_FACTORS = 8
DEFAULT_MAX_SUPPORTS = 8
DEFAULT_MAX_TENSIONS = 8
DEFAULT_MAX_SECTIONS = 12


# ==========================================================
# PROMPT CONTEXT
# ==========================================================

@dataclass
class PromptContext:
    """
    Единый структурированный контекст для Prompt Builder.

    Это НЕ готовый текст промпта.

    Здесь находятся уже обработанные результаты
    аналитического двигателя.
    """

    chart_type: str = ""

    chart: dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # ОСНОВНАЯ ТЕМА
    # ------------------------------------------------------

    main_theme: dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------
    # СТРУКТУРНЫЕ ПРИОРИТЕТЫ
    # ------------------------------------------------------

    key_factors: list[dict[str, Any]] = field(
        default_factory=list
    )

    strengths: list[dict[str, Any]] = field(
        default_factory=list
    )

    challenges: list[dict[str, Any]] = field(
        default_factory=list
    )

    contradictions: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ------------------------------------------------------
    # КОМПОЗИЦИЯ
    # ------------------------------------------------------

    composition_plans: list[dict[str, Any]] = field(
        default_factory=list
    )

    sections: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ------------------------------------------------------
    # НАРРАТИВ
    # ------------------------------------------------------

    narratives: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ------------------------------------------------------
    # ДОКАЗАТЕЛЬСТВА
    # ------------------------------------------------------

    evidence: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ------------------------------------------------------
    # ТЕМЫ / СЕМАНТИКА
    # ------------------------------------------------------

    themes: list[dict[str, Any]] = field(
        default_factory=list
    )

    semantics: list[dict[str, Any]] = field(
        default_factory=list
    )

    interpretations: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ------------------------------------------------------
    # СТАРЫЙ / LEGACY КОНТРАКТ
    # ------------------------------------------------------

    dominant_elements: list[str] = field(
        default_factory=list
    )

    dominant_modes: list[str] = field(
        default_factory=list
    )

    dominant_houses: list[int] = field(
        default_factory=list
    )

    receptions_text: str = ""

    accidental_dignities_text: str = ""

    transit_aspects_text: str = ""

    # ------------------------------------------------------
    # ДОПОЛНИТЕЛЬНО
    # ------------------------------------------------------

    data: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "chart_type": self.chart_type,
            "chart": dict(self.chart),
            "main_theme": dict(self.main_theme),

            "key_factors": list(
                self.key_factors
            ),

            "strengths": list(
                self.strengths
            ),

            "challenges": list(
                self.challenges
            ),

            "contradictions": list(
                self.contradictions
            ),

            "composition_plans": list(
                self.composition_plans
            ),

            "sections": list(
                self.sections
            ),

            "narratives": list(
                self.narratives
            ),

            "evidence": list(
                self.evidence
            ),

            "themes": list(
                self.themes
            ),

            "semantics": list(
                self.semantics
            ),

            "interpretations": list(
                self.interpretations
            ),

            "dominant_elements": list(
                self.dominant_elements
            ),

            "dominant_modes": list(
                self.dominant_modes
            ),

            "dominant_houses": list(
                self.dominant_houses
            ),

            "receptions": self.receptions_text,

            "accidental_dignities": (
                self.accidental_dignities_text
            ),

            "transit_aspects_text": (
                self.transit_aspects_text
            ),

            "data": dict(self.data),
        }

    def __repr__(self) -> str:
        return (
            f"<PromptContext "
            f"type={self.chart_type!r} "
            f"themes={len(self.themes)} "
            f"narratives={len(self.narratives)} "
            f"plans={len(self.composition_plans)} "
            f"evidence={len(self.evidence)}>"
        )


# ==========================================================
# ВСПОМОГАТЕЛЬНЫЕ
# ==========================================================

def _as_list(collection) -> list:
    if collection is None:
        return []

    if hasattr(collection, "all"):
        return list(
            collection.all()
        )

    if isinstance(
        collection,
        (list, tuple, set),
    ):
        return list(collection)

    return list(collection)


def _get(
    item,
    name: str,
    default=None,
):
    if item is None:
        return default

    if isinstance(item, dict):
        return item.get(
            name,
            default,
        )

    return getattr(
        item,
        name,
        default,
    )


def _dictify(item) -> dict[str, Any]:
    """
    Превращает dataclass-подобный объект
    в обычный dict без жёсткой зависимости
    от конкретного класса.
    """

    if item is None:
        return {}

    if isinstance(
        item,
        dict,
    ):
        return dict(item)

    if hasattr(
        item,
        "to_dict",
    ):
        try:
            value = item.to_dict()

            if isinstance(
                value,
                dict,
            ):
                return value

        except Exception:
            pass

    result = {}

    if hasattr(
        item,
        "__dict__",
    ):
        result.update(
            item.__dict__
        )

    return result


def _tuple_strings(value) -> tuple[str, ...]:
    if not value:
        return ()

    return tuple(
        sorted(
            {
                item
                for item in value
                if isinstance(
                    item,
                    str,
                )
            }
        )
    )


def _tuple_ints(value) -> tuple[int, ...]:
    if not value:
        return ()

    return tuple(
        sorted(
            {
                item
                for item in value
                if isinstance(
                    item,
                    int,
                )
            }
        )
    )


def _unique_dicts(
    values,
    key_fields=(
        "theme_key",
        "type",
        "key",
        "kind",
        "object",
    ),
) -> list[dict[str, Any]]:
    """
    Убирает очевидные дубли.
    """

    result = []
    seen = set()

    for value in values:

        item = _dictify(value)

        if not item:
            continue

        signature = None

        for field_name in key_fields:

            field_value = item.get(
                field_name
            )

            if field_value not in (
                None,
                "",
                (),
                [],
            ):
                signature = (
                    field_name,
                    str(field_value),
                )
                break

        if signature is None:
            signature = (
                "__raw__",
                repr(
                    sorted(
                        item.items()
                    )
                ),
            )

        if signature in seen:
            continue

        seen.add(signature)
        result.append(item)

    return result


# ==========================================================
# CHART
# ==========================================================

def _build_chart_context(
    chart,
) -> dict[str, Any]:

    if chart is None:
        return {}

    result = _dictify(
        chart
    )

    if result:
        return result

    chart_type = _get(
        chart,
        "type",
        None,
    )

    datetime_value = _get(
        chart,
        "datetime",
        None,
    )

    if chart_type is not None:
        result["type"] = chart_type

    if datetime_value is not None:
        result["datetime"] = str(
            datetime_value
        )

    return result


# ==========================================================
# MAIN THEME
# ==========================================================

def _build_main_theme(
    composition_plans,
    narratives,
    themes,
) -> dict[str, Any]:

    plans = _as_list(
        composition_plans
    )

    narratives_list = _as_list(
        narratives
    )

    themes_list = _as_list(
        themes
    )

    if plans:
        strongest = plans[0]

        return {
            "theme_key": _get(
                strongest,
                "theme_key",
                "unknown",
            ),
            "core_theme": _get(
                strongest,
                "core_theme",
                "",
            ),
            "dominant_process": _get(
                strongest,
                "dominant_process",
                None,
            ),
            "strength": _get(
                strongest,
                "strength",
                0.0,
            ),
            "confidence": _get(
                strongest,
                "confidence",
                0.0,
            ),
            "domains": _tuple_strings(
                _get(
                    strongest,
                    "domains",
                    (),
                )
            ),
            "planets": _tuple_strings(
                _get(
                    strongest,
                    "planets",
                    (),
                )
            ),
            "houses": _tuple_ints(
                _get(
                    strongest,
                    "houses",
                    (),
                )
            ),
        }

    if narratives_list:

        strongest = narratives_list[0]

        return {
            "theme_key": _get(
                strongest,
                "theme_key",
                "unknown",
            ),
            "core_theme": _get(
                strongest,
                "core_theme",
                "",
            ),
            "dominant_process": _get(
                strongest,
                "dominant_process",
                None,
            ),
            "strength": _get(
                strongest,
                "strength",
                0.0,
            ),
            "confidence": _get(
                strongest,
                "confidence",
                0.0,
            ),
            "domains": _tuple_strings(
                _get(
                    strongest,
                    "domains",
                    (),
                )
            ),
            "planets": _tuple_strings(
                _get(
                    strongest,
                    "planets",
                    (),
                )
            ),
            "houses": _tuple_ints(
                _get(
                    strongest,
                    "houses",
                    (),
                )
            ),
        }

    if themes_list:

        strongest = themes_list[0]

        return {
            "theme_key": _get(
                strongest,
                "theme_key",
                "unknown",
            ),
            "strength": _get(
                strongest,
                "strength",
                0.0,
            ),
            "coherence": _get(
                strongest,
                "coherence",
                0.0,
            ),
            "domains": (),
            "planets": _tuple_strings(
                _get(
                    strongest,
                    "planets",
                    (),
                )
            ),
            "houses": _tuple_ints(
                _get(
                    strongest,
                    "houses",
                    (),
                )
            ),
        }

    return {}


# ==========================================================
# COMPOSITIONS
# ==========================================================

def _build_composition_context(
    composition_plans,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:

    plans = _as_list(
        composition_plans
    )

    plans = plans[:DEFAULT_MAX_PLANS]

    result = []
    sections = []

    for plan in plans:

        plan_dict = _dictify(
            plan
        )

        if not plan_dict:
            continue

        clean_plan = {
            "theme_key": plan_dict.get(
                "theme_key",
                "",
            ),
            "strength": plan_dict.get(
                "strength",
                0.0,
            ),
            "confidence": plan_dict.get(
                "confidence",
                0.0,
            ),
            "core_theme": plan_dict.get(
                "core_theme",
                "",
            ),
            "dominant_process": plan_dict.get(
                "dominant_process"
            ),
            "domains": _tuple_strings(
                plan_dict.get(
                    "domains",
                    (),
                )
            ),
            "planets": _tuple_strings(
                plan_dict.get(
                    "planets",
                    (),
                )
            ),
            "houses": _tuple_ints(
                plan_dict.get(
                    "houses",
                    (),
                )
            ),
            "central_claims": tuple(
                plan_dict.get(
                    "central_claims",
                    (),
                )
            ),
            "tensions": _tuple_strings(
                plan_dict.get(
                    "tensions",
                    (),
                )
            ),
            "supports": _tuple_strings(
                plan_dict.get(
                    "supports",
                    (),
                )
            ),
            "resolutions": _tuple_strings(
                plan_dict.get(
                    "resolutions",
                    (),
                )
            ),
        }

        result.append(
            clean_plan
        )

        for section in _as_list(
            _get(
                plan,
                "sections",
                (),
            )
        ):

            section_dict = _dictify(
                section
            )

            if not section_dict:
                continue

            section_context = {
                "theme_key": clean_plan[
                    "theme_key"
                ],
                "section_type": section_dict.get(
                    "section_type",
                    "",
                ),
                "title": section_dict.get(
                    "title",
                    "",
                ),
                "purpose": section_dict.get(
                    "purpose",
                    "",
                ),
                "priority": section_dict.get(
                    "priority",
                    0.0,
                ),
                "sources": tuple(
                    section_dict.get(
                        "sources",
                        (),
                    )
                ),
                "instructions": tuple(
                    section_dict.get(
                        "instructions",
                        (),
                    )
                ),
                "data": dict(
                    section_dict.get(
                        "data",
                        {},
                    )
                    or {}
                ),
            }

            sections.append(
                section_context
            )

    return (
        result,
        sections[
            :DEFAULT_MAX_SECTIONS
        ],
    )


# ==========================================================
# NARRATIVES
# ==========================================================

def _build_narrative_context(
    narratives,
) -> list[dict[str, Any]]:

    result = []

    for narrative in _as_list(
        narratives
    )[:DEFAULT_MAX_PLANS]:

        item = _dictify(
            narrative
        )

        if not item:
            continue

        result.append(
            {
                "theme_key": item.get(
                    "theme_key",
                    "",
                ),
                "strength": item.get(
                    "strength",
                    0.0,
                ),
                "confidence": item.get(
                    "confidence",
                    0.0,
                ),
                "core_theme": item.get(
                    "core_theme",
                    "",
                ),
                "dominant_process": item.get(
                    "dominant_process"
                ),
                "mechanisms": _tuple_strings(
                    item.get(
                        "mechanisms",
                        (),
                    )
                ),
                "dynamics": _tuple_strings(
                    item.get(
                        "dynamics",
                        (),
                    )
                ),
                "tensions": _tuple_strings(
                    item.get(
                        "tensions",
                        (),
                    )
                ),
                "supports": _tuple_strings(
                    item.get(
                        "supports",
                        (),
                    )
                ),
                "manifestations": _tuple_strings(
                    item.get(
                        "manifestations",
                        (),
                    )
                ),
                "resolution": _tuple_strings(
                    item.get(
                        "resolution",
                        (),
                    )
                ),
            }
        )

    return result


# ==========================================================
# EVIDENCE
# ==========================================================

def _build_evidence_context(
    evidence,
) -> list[dict[str, Any]]:

    evidence_list = _as_list(
        evidence
    )

    result = []

    for item in evidence_list:

        data = _dictify(
            item
        )

        if not data:
            continue

        result.append(
            {
                "source": data.get(
                    "source",
                    "",
                ),
                "theme_key": data.get(
                    "theme_key",
                    "",
                ),
                "kind": data.get(
                    "kind",
                    "",
                ),
                "key": data.get(
                    "key",
                    "",
                ),
                "confidence": data.get(
                    "confidence",
                    0.0,
                ),
                "strength": data.get(
                    "strength",
                    0.0,
                ),
                "object": data.get(
                    "object",
                    "",
                ),
                "data": dict(
                    data.get(
                        "data",
                        {},
                    )
                    or {}
                ),
            }
        )

    result.sort(
        key=lambda item: (
            float(
                item.get(
                    "strength",
                    0.0,
                )
                or 0.0
            ),
            float(
                item.get(
                    "confidence",
                    0.0,
                )
                or 0.0
            ),
        ),
        reverse=True,
    )

    return result[
        :DEFAULT_MAX_EVIDENCE
    ]


# ==========================================================
# KEY FACTORS
# ==========================================================

def _build_key_factors(
    priorities,
) -> list[dict[str, Any]]:

    factors = []

    for item in _as_list(
        priorities
    )[:DEFAULT_MAX_KEY_FACTORS]:

        data = _dictify(
            item
        )

        if not data:
            continue

        factors.append(
            {
                "type": data.get(
                    "type",
                    "",
                ),
                "object": data.get(
                    "object",
                    "",
                ),
                "importance": data.get(
                    "importance",
                    data.get(
                        "strength",
                        0.0,
                    ),
                ),
                "confidence": data.get(
                    "confidence",
                    0.0,
                ),
                "importance_reasons": list(
                    data.get(
                        "importance_reasons",
                        (),
                    )
                    or ()
                ),
                "data": dict(
                    data.get(
                        "data",
                        {},
                    )
                    or {}
                ),
            }
        )

    return factors


# ==========================================================
# TENSIONS / SUPPORTS
# ==========================================================

def _build_contradictions(
    patterns,
) -> list[dict[str, Any]]:

    result = []

    source = patterns

    if source is None:
        return result

    tension_values = _get(
        source,
        "tensions",
        (),
    )

    for item in _as_list(
        tension_values
    ):

        data = _dictify(
            item
        )

        if not data:
            continue

        result.append(
            {
                "type": data.get(
                    "type",
                    "tension",
                ),
                "planet1": data.get(
                    "planet1",
                    data.get(
                        "source",
                        "?",
                    ),
                ),
                "planet2": data.get(
                    "planet2",
                    data.get(
                        "target",
                        "?",
                    ),
                ),
                "aspect": data.get(
                    "aspect",
                    data.get(
                        "theme_hint",
                        "",
                    ),
                ),
                "strength": data.get(
                    "strength",
                    data.get(
                        "importance",
                        0.0,
                    ),
                ),
                "data": data,
            }
        )

    return result[
        :DEFAULT_MAX_TENSIONS
    ]


def _collect_global_supports(
    narratives,
    composition_plans,
) -> list[str]:

    result = []

    for collection in (
        narratives,
        composition_plans,
    ):

        for item in _as_list(
            collection
        ):

            values = _get(
                item,
                "supports",
                (),
            )

            for value in _as_list(
                values
            ):

                if isinstance(
                    value,
                    str,
                ) and value not in result:

                    result.append(
                        value
                    )

    return result[
        :DEFAULT_MAX_SUPPORTS
    ]


# ==========================================================
# DOMINANTS
# ==========================================================

def _build_dominants(
    semantics,
    chart,
) -> tuple[
    list[str],
    list[str],
    list[int],
]:

    profiles = _as_list(
        semantics
    )

    elements = []
    modes = []
    houses = []

    # ------------------------------------------------------
    # Дома из наиболее сильных семантических профилей
    # ------------------------------------------------------

    for profile in profiles:

        profile_houses = _get(
            profile,
            "houses",
            (),
        )

        for house in _as_list(
            profile_houses
        ):

            if (
                isinstance(
                    house,
                    int,
                )
                and house not in houses
            ):
                houses.append(
                    house
                )

    houses = sorted(
        houses
    )

    # ------------------------------------------------------
    # chart.dominants если они уже существуют
    # ------------------------------------------------------

    chart_data = _dictify(
        chart
    )

    if chart_data:

        raw_elements = chart_data.get(
            "dominant_elements",
            (),
        )

        raw_modes = chart_data.get(
            "dominant_modes",
            (),
        )

        elements.extend(
            str(item)
            for item in _as_list(
                raw_elements
            )
        )

        modes.extend(
            str(item)
            for item in _as_list(
                raw_modes
            )
        )

    return (
        list(
            dict.fromkeys(
                elements
            )
        ),
        list(
            dict.fromkeys(
                modes
            )
        ),
        houses[:6],
    )


# ==========================================================
# FACTOR SPLIT
# ==========================================================

def _build_strengths_and_challenges(
    composition_plans,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:

    strengths = []
    challenges = []

    for plan in _as_list(
        composition_plans
    ):

        mechanisms = set(
            _as_list(
                _get(
                    plan,
                    "central_claims",
                    (),
                )
            )
        )

        supports = _as_list(
            _get(
                plan,
                "supports",
                (),
            )
        )

        tensions = _as_list(
            _get(
                plan,
                "tensions",
                (),
            )
        )

        strength = float(
            _get(
                plan,
                "strength",
                0.0,
            )
            or 0.0
        )

        confidence = float(
            _get(
                plan,
                "confidence",
                0.0,
            )
            or 0.0
        )

        theme_key = _get(
            plan,
            "theme_key",
            "",
        )

        if supports:

            strengths.append(
                {
                    "object": theme_key,
                    "confidence": confidence,
                    "confidence_reasons": [
                        "structural_support",
                        "coherent_process",
                    ],
                    "strength": strength,
                    "supports": tuple(
                        supports
                    ),
                }
            )

        if tensions:

            challenges.append(
                {
                    "object": theme_key,
                    "confidence": confidence,
                    "confidence_reasons": [
                        "structural_tension",
                        "identified_contradiction",
                    ],
                    "strength": strength,
                    "tensions": tuple(
                        tensions
                    ),
                }
            )

    return (
        strengths[:DEFAULT_MAX_KEY_FACTORS],
        challenges[:DEFAULT_MAX_KEY_FACTORS],
    )


# ==========================================================
# MAIN BUILDER
# ==========================================================

def build_prompt_context(
    compositions=None,
    narratives=None,
    evidence=None,
    semantics=None,
    interpretations=None,
    themes=None,
    patterns=None,
    relations=None,
    priorities=None,
    chart=None,
    chart_type=None,
) -> PromptContext:
    """
    Строит единый PromptContext.

    Основной путь:

        Composition
            +
        Narrative
            +
        Evidence
            ↓
        PromptContext
    """

    composition_list = _as_list(
        compositions
    )

    narrative_list = _as_list(
        narratives
    )

    evidence_list = _as_list(
        evidence
    )

    semantic_list = _as_list(
        semantics
    )

    interpretation_list = _as_list(
        interpretations
    )

    theme_list = _as_list(
        themes
    )

    # ------------------------------------------------------
    # CHART TYPE
    # ------------------------------------------------------

    resolved_chart_type = (
        chart_type
        or _get(
            chart,
            "type",
            "",
        )
        or ""
    )

    # ------------------------------------------------------
    # COMPOSITION
    # ------------------------------------------------------

    composition_context, section_context = (
        _build_composition_context(
            composition_list
        )
    )

    # ------------------------------------------------------
    # NARRATIVE
    # ------------------------------------------------------

    narrative_context = (
        _build_narrative_context(
            narrative_list
        )
    )

    # ------------------------------------------------------
    # EVIDENCE
    # ------------------------------------------------------

    evidence_context = (
        _build_evidence_context(
            evidence_list
        )
    )

    # ------------------------------------------------------
    # MAIN THEME
    # ------------------------------------------------------

    main_theme = _build_main_theme(
        composition_list,
        narrative_list,
        theme_list,
    )

    # ------------------------------------------------------
    # KEY FACTORS
    # ------------------------------------------------------

    key_factors = (
        _build_key_factors(
            priorities
        )
    )

    # ------------------------------------------------------
    # CONTRADICTIONS
    # ------------------------------------------------------

    contradictions = (
        _build_contradictions(
            patterns
        )
    )

    # ------------------------------------------------------
    # STRENGTHS / CHALLENGES
    # ------------------------------------------------------

    strengths, challenges = (
        _build_strengths_and_challenges(
            composition_list
        )
    )

    # ------------------------------------------------------
    # DOMINANTS
    # ------------------------------------------------------

    (
        dominant_elements,
        dominant_modes,
        dominant_houses,
    ) = _build_dominants(
        semantic_list,
        chart,
    )

    # ------------------------------------------------------
    # GLOBAL SUPPORTS
    # ------------------------------------------------------

    global_supports = (
        _collect_global_supports(
            narrative_list,
            composition_list,
        )
    )

    # ------------------------------------------------------
    # DATA
    # ------------------------------------------------------

    context_data = {
        "composition_count": len(
            composition_context
        ),
        "narrative_count": len(
            narrative_context
        ),
        "evidence_count": len(
            evidence_context
        ),
        "semantic_count": len(
            semantic_list
        ),
        "interpretation_count": len(
            interpretation_list
        ),
        "theme_count": len(
            theme_list
        ),
        "global_supports": tuple(
            global_supports
        ),
    }

    return PromptContext(
        chart_type=resolved_chart_type,
        chart=_build_chart_context(
            chart
        ),

        main_theme=main_theme,

        key_factors=key_factors,
        strengths=strengths,
        challenges=challenges,
        contradictions=contradictions,

        composition_plans=composition_context,
        sections=section_context,

        narratives=narrative_context,

        evidence=evidence_context,

        themes=[
            _dictify(item)
            for item in theme_list
        ],

        semantics=[
            _dictify(item)
            for item in semantic_list
        ],

        interpretations=[
            _dictify(item)
            for item in interpretation_list
        ],

        dominant_elements=dominant_elements,
        dominant_modes=dominant_modes,
        dominant_houses=dominant_houses,

        data=context_data,
    )


# ==========================================================
# DICT API
# ==========================================================

def build_prompt_context_from_dict(
    data: dict[str, Any],
) -> PromptContext:

    if not isinstance(
        data,
        dict,
    ):
        raise TypeError(
            "data must be dict"
        )

    return build_prompt_context(
        compositions=data.get(
            "compositions",
            data.get(
                "composition_plans",
                [],
            ),
        ),
        narratives=data.get(
            "narratives",
            [],
        ),
        evidence=data.get(
            "evidence",
            [],
        ),
        semantics=data.get(
            "semantics",
            [],
        ),
        interpretations=data.get(
            "interpretations",
            [],
        ),
        themes=data.get(
            "themes",
            [],
        ),
        patterns=data.get(
            "patterns",
            [],
        ),
        relations=data.get(
            "relations",
            [],
        ),
        priorities=data.get(
            "priorities",
            [],
        ),
        chart=data.get(
            "chart",
            {},
        ),
        chart_type=data.get(
            "chart_type",
            None,
        ),
    )


# ==========================================================
# SERIALIZATION
# ==========================================================

def prompt_context_to_dict(
    context: PromptContext,
) -> dict[str, Any]:

    if isinstance(
        context,
        PromptContext,
    ):
        return context.to_dict()

    return _dictify(
        context
    )