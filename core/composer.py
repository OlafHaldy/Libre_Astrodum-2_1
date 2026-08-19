"""
Liber Astrodum

core/composer.py

Narrative Composer Engine v1.1.

Преобразует:

    NarrativeBlueprint
        ↓
    CompositionPlan

Composer НЕ генерирует литературный текст.
Composer НЕ использует LLM.
Composer НЕ трактует карту заново.

Его задача:

    определить композицию будущего текста,
    порядок смысловых блоков,
    приоритет смыслов,
    какие элементы карты следует раскрыть,
    где показать центральную тему,
    где раскрыть механизм,
    где показать проявления,
    где показать напряжение,
    где показать поддержку,
    куда вести разрешение.

Поток:

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
    Narrative Blueprint
      ↓
    Composition Plan
      ↓
    LLM

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum / Astrodum Engine

Версия:
    1.1
"""

from dataclasses import dataclass, field
from typing import Any


# ==========================================================
# КОНСТАНТЫ
# ==========================================================

MIN_COMPOSITION_CONFIDENCE = 0.35


# ==========================================================
# SECTION PRIORITIES
# ==========================================================

SECTION_PRIORITY = {
    "opening": 100.0,
    "central_theme": 95.0,
    "mechanism": 90.0,
    "tension": 90.0,
    "resolution": 88.0,
    "manifestation": 85.0,
    "development": 80.0,
    "support": 75.0,
    "conclusion": 70.0,
}


# ==========================================================
# COMPOSITION SECTION
# ==========================================================

@dataclass
class CompositionSection:
    """
    Один смысловой блок будущего текста.

    section_type:
        Машинный тип блока.

    title:
        Машинное или условное название.

    purpose:
        Задача блока.

    priority:
        Значимость блока 0..100.

    sources:
        Какие поля Narrative/Composition
        использовать в этом блоке.

    instructions:
        Структурные указания будущему генератору.

    data:
        Дополнительные данные,
        в том числе фактический фокус.
    """

    section_type: str
    title: str
    purpose: str
    priority: float

    sources: tuple[str, ...] = ()
    instructions: tuple[str, ...] = ()

    data: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict:
        return {
            "section_type": self.section_type,
            "title": self.title,
            "purpose": self.purpose,
            "priority": self.priority,
            "sources": list(self.sources),
            "instructions": list(self.instructions),
            "data": dict(self.data),
        }

    def __repr__(self) -> str:
        return (
            f"<CompositionSection "
            f"{self.section_type} "
            f"priority={self.priority:.1f}>"
        )


# ==========================================================
# COMPOSITION PLAN
# ==========================================================

@dataclass
class CompositionPlan:
    """
    Полный план будущего текста по одной теме.
    """

    theme_key: str

    strength: float
    confidence: float

    core_theme: str = ""

    dominant_process: str | None = None

    domains: tuple[str, ...] = ()
    planets: tuple[str, ...] = ()
    houses: tuple[int, ...] = ()

    fact_focus: tuple[str, ...] = ()

    central_claims: tuple[str, ...] = ()

    sections: tuple[CompositionSection, ...] = ()

    tensions: tuple[str, ...] = ()
    supports: tuple[str, ...] = ()
    resolutions: tuple[str, ...] = ()

    evidence: tuple[dict, ...] = ()

    data: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict:
        return {
            "theme_key": self.theme_key,
            "strength": self.strength,
            "confidence": self.confidence,
            "core_theme": self.core_theme,
            "dominant_process": self.dominant_process,
            "domains": list(self.domains),
            "planets": list(self.planets),
            "houses": list(self.houses),
            "fact_focus": list(self.fact_focus),
            "central_claims": list(self.central_claims),
            "sections": [
                section.to_dict()
                for section in self.sections
            ],
            "tensions": list(self.tensions),
            "supports": list(self.supports),
            "resolutions": list(self.resolutions),
            "evidence": list(self.evidence),
            "data": dict(self.data),
        }

    def __repr__(self) -> str:
        return (
            f"<CompositionPlan "
            f"{self.theme_key} "
            f"sections={len(self.sections)} "
            f"confidence={self.confidence:.2f}>"
        )


# ==========================================================
# COMPOSITION REPORT
# ==========================================================

class CompositionReport:
    """
    Коллекция CompositionPlan.
    """

    def __init__(
        self,
        plans: list[CompositionPlan] | None = None,
    ):
        self._plans = (
            list(plans)
            if plans
            else []
        )

        self._plans.sort(
            key=lambda plan: (
                plan.strength,
                plan.confidence,
            ),
            reverse=True,
        )

    def all(self) -> list[CompositionPlan]:
        return list(self._plans)

    def to_list(self) -> list[dict]:
        return [
            plan.to_dict()
            for plan in self._plans
        ]

    def top(
        self,
        n: int = 5,
    ) -> list[CompositionPlan]:
        return self._plans[:n]

    def by_theme(
        self,
        theme_key: str,
    ) -> list[CompositionPlan]:
        return [
            plan
            for plan in self._plans
            if plan.theme_key == theme_key
        ]

    @property
    def strongest(
        self,
    ) -> CompositionPlan | None:
        return (
            self._plans[0]
            if self._plans
            else None
        )

    def __len__(self) -> int:
        return len(self._plans)

    def __iter__(self):
        return iter(self._plans)

    def __getitem__(self, index):
        return self._plans[index]

    def __repr__(self) -> str:
        return (
            f"<CompositionReport "
            f"plans={len(self._plans)}>"
        )


# ==========================================================
# ВСПОМОГАТЕЛЬНЫЕ
# ==========================================================

def _as_list(collection) -> list:
    if collection is None:
        return []

    if hasattr(collection, "all"):
        return collection.all()

    return list(collection)


def _get(
    item,
    name: str,
    default=None,
):
    """
    Безопасно получает значение
    из объекта или dict.
    """

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


def _unique(values) -> tuple:
    result = []

    for value in values:

        if not value:
            continue

        if value not in result:
            result.append(value)

    return tuple(result)


# ==========================================================
# FACT FOCUS
# ==========================================================

def _derive_fact_focus(
    blueprint,
) -> tuple[str, ...]:
    """
    Определяет, какие элементы структурной карты
    наиболее уместно раскрывать в будущем тексте.

    Это НЕ извлечение новых фактов.
    Используются только данные Narrative Blueprint.
    """

    result = []

    planets = _tuple_strings(
        _get(
            blueprint,
            "planets",
            (),
        )
    )

    houses = _tuple_ints(
        _get(
            blueprint,
            "houses",
            (),
        )
    )

    domains = _tuple_strings(
        _get(
            blueprint,
            "domains",
            (),
        )
    )

    mechanisms = _tuple_strings(
        _get(
            blueprint,
            "mechanisms",
            (),
        )
    )

    tensions = _tuple_strings(
        _get(
            blueprint,
            "tensions",
            (),
        )
    )

    supports = _tuple_strings(
        _get(
            blueprint,
            "supports",
            (),
        )
    )

    for planet in planets:
        result.append(
            f"planet:{planet}"
        )

    for house in houses:
        result.append(
            f"house:{house}"
        )

    for domain in domains:
        result.append(
            f"domain:{domain}"
        )

    for mechanism in mechanisms:
        result.append(
            f"mechanism:{mechanism}"
        )

    for tension in tensions:
        result.append(
            f"tension:{tension}"
        )

    for support in supports:
        result.append(
            f"support:{support}"
        )

    return _unique(result)


# ==========================================================
# CLAIM EXTRACTION
# ==========================================================

def _derive_central_claims(
    blueprint,
) -> tuple[str, ...]:
    """
    Формирует короткий список центральных
    структурных утверждений.

    Это НЕ литературные фразы.
    """

    claims = []

    core_theme = _get(
        blueprint,
        "core_theme",
        "",
    )

    dominant_process = _get(
        blueprint,
        "dominant_process",
        None,
    )

    mechanisms = _get(
        blueprint,
        "mechanisms",
        (),
    ) or ()

    tensions = _get(
        blueprint,
        "tensions",
        (),
    ) or ()

    supports = _get(
        blueprint,
        "supports",
        (),
    ) or ()

    resolutions = _get(
        blueprint,
        "resolution",
        (),
    ) or ()

    if core_theme:
        claims.append(
            f"central_theme:{core_theme}"
        )

    if dominant_process:
        claims.append(
            f"dominant_process:{dominant_process}"
        )

    for mechanism in mechanisms:
        claims.append(
            f"mechanism:{mechanism}"
        )

    for tension in tensions:
        claims.append(
            f"tension:{tension}"
        )

    for support in supports:
        claims.append(
            f"support:{support}"
        )

    for resolution in resolutions:
        claims.append(
            f"resolution:{resolution}"
        )

    return _unique(claims)


# ==========================================================
# EVIDENCE
# ==========================================================

def _derive_evidence(
    blueprint,
) -> tuple[dict, ...]:
    """
    Переносит evidence Narrative
    в Composition Plan.
    """

    evidence = _get(
        blueprint,
        "evidence",
        (),
    ) or ()

    result = []

    for item in evidence:

        if isinstance(
            item,
            dict,
        ):
            result.append(
                {
                    "source": item.get(
                        "source",
                        "",
                    ),
                    "kind": item.get(
                        "kind",
                        "",
                    ),
                    "key": item.get(
                        "key",
                        "",
                    ),
                    "confidence": item.get(
                        "confidence",
                        0.0,
                    ),
                }
            )

    return tuple(result)


# ==========================================================
# SECTION BUILDERS
# ==========================================================

def _build_opening_section(
    blueprint,
) -> CompositionSection:

    domains = _tuple_strings(
        _get(
            blueprint,
            "domains",
            (),
        )
    )

    planets = _tuple_strings(
        _get(
            blueprint,
            "planets",
            (),
        )
    )

    houses = _tuple_ints(
        _get(
            blueprint,
            "houses",
            (),
        )
    )

    core_theme = _get(
        blueprint,
        "core_theme",
        "general_theme",
    )

    instructions = [
        "introduce the dominant theme without overexplaining",
        "establish the strongest area of life affected",
        "do not list every astrological factor",
        "begin from synthesis rather than enumeration",
    ]

    if domains:
        instructions.append(
            "anchor the opening in the strongest domain"
        )

    if planets:
        instructions.append(
            "use the strongest thematic planets as evidence"
        )

    return CompositionSection(
        section_type="opening",
        title="Opening",
        purpose=(
            "Introduce the central condition "
            "of the theme."
        ),
        priority=SECTION_PRIORITY["opening"],
        sources=(
            "core_theme",
            "domains",
            "planets",
            "strength",
        ),
        instructions=tuple(
            instructions
        ),
        data={
            "core_theme": core_theme,
            "domains": domains,
            "planets": planets,
            "houses": houses,
        },
    )


def _build_central_theme_section(
    blueprint,
) -> CompositionSection:

    core_theme = _get(
        blueprint,
        "core_theme",
        "",
    )

    dominant_process = _get(
        blueprint,
        "dominant_process",
        None,
    )

    domains = _tuple_strings(
        _get(
            blueprint,
            "domains",
            (),
        )
    )

    instructions = [
        "state what the theme is fundamentally about",
        "connect the theme with the dominant process",
        "define the main structural pattern before discussing details",
        "keep the formulation structural rather than predictive",
    ]

    return CompositionSection(
        section_type="central_theme",
        title="Central Theme",
        purpose=(
            "Explain the main structural meaning."
        ),
        priority=SECTION_PRIORITY["central_theme"],
        sources=(
            "core_theme",
            "dominant_process",
            "domains",
            "central_claims",
        ),
        instructions=tuple(
            instructions
        ),
        data={
            "core_theme": core_theme,
            "dominant_process": dominant_process,
            "domains": domains,
        },
    )


def _build_mechanism_section(
    blueprint,
) -> CompositionSection:

    mechanisms = _tuple_strings(
        _get(
            blueprint,
            "mechanisms",
            (),
        )
    )

    planets = _tuple_strings(
        _get(
            blueprint,
            "planets",
            (),
        )
    )

    houses = _tuple_ints(
        _get(
            blueprint,
            "houses",
            (),
        )
    )

    instructions = [
        "explain how the central theme operates",
        "connect mechanisms into one causal structure",
        "avoid explaining each mechanism as an isolated horoscope item",
        "prioritize relationships between mechanisms",
    ]

    if "mental_component" in mechanisms:
        instructions.append(
            "include the cognitive component"
        )

    if "emotional_component" in mechanisms:
        instructions.append(
            "include the emotional component"
        )

    if "active_agency" in mechanisms:
        instructions.append(
            "include the role of action or agency"
        )

    if "structural_constraint" in mechanisms:
        instructions.append(
            "show the role of structure, limits, or pressure"
        )

    if "expansive_component" in mechanisms:
        instructions.append(
            "show where expansion exceeds or challenges existing structure"
        )

    return CompositionSection(
        section_type="mechanism",
        title="Mechanism",
        purpose=(
            "Explain the internal machinery "
            "of the theme."
        ),
        priority=SECTION_PRIORITY["mechanism"],
        sources=(
            "mechanisms",
            "planets",
            "houses",
            "evidence",
        ),
        instructions=tuple(
            instructions
        ),
        data={
            "mechanisms": mechanisms,
            "planets": planets,
            "houses": houses,
        },
    )


def _build_manifestation_section(
    blueprint,
) -> CompositionSection:

    manifestations = _tuple_strings(
        _get(
            blueprint,
            "manifestations",
            (),
        )
    )

    domains = _tuple_strings(
        _get(
            blueprint,
            "domains",
            (),
        )
    )

    houses = _tuple_ints(
        _get(
            blueprint,
            "houses",
            (),
        )
    )

    instructions = [
        "translate the structure into possible areas of manifestation",
        "move from abstract mechanism toward lived experience",
        "use the domains and house areas as context",
        "do not turn possibilities into deterministic predictions",
        "prefer conditional formulations over certainty",
    ]

    return CompositionSection(
        section_type="manifestation",
        title="Manifestation",
        purpose=(
            "Show where and how the theme may appear."
        ),
        priority=SECTION_PRIORITY["manifestation"],
        sources=(
            "manifestations",
            "domains",
            "houses",
            "fact_focus",
        ),
        instructions=tuple(
            instructions
        ),
        data={
            "manifestations": manifestations,
            "domains": domains,
            "houses": houses,
        },
    )


def _build_tension_section(
    blueprint,
) -> CompositionSection | None:

    tensions = _tuple_strings(
        _get(
            blueprint,
            "tensions",
            (),
        )
    )

    if not tensions:
        return None

    mechanisms = _tuple_strings(
        _get(
            blueprint,
            "mechanisms",
            (),
        )
    )

    dominant_process = _get(
        blueprint,
        "dominant_process",
        None,
    )

    instructions = [
        "identify the main contradiction without exaggeration",
        "show both sides of the conflict",
        "explain what creates pressure or polarization",
        "connect tension to the underlying mechanism",
        "do not resolve the conflict prematurely",
    ]

    if dominant_process:
        instructions.append(
            f"keep {dominant_process} as the organizing tension process"
        )

    return CompositionSection(
        section_type="tension",
        title="Tension",
        purpose=(
            "Expose the central contradiction "
            "of the theme."
        ),
        priority=SECTION_PRIORITY["tension"],
        sources=(
            "tensions",
            "dominant_process",
            "mechanisms",
            "evidence",
        ),
        instructions=tuple(
            instructions
        ),
        data={
            "tensions": tensions,
            "mechanisms": mechanisms,
            "dominant_process": dominant_process,
        },
    )


def _build_support_section(
    blueprint,
) -> CompositionSection | None:

    supports = _tuple_strings(
        _get(
            blueprint,
            "supports",
            (),
        )
    )

    if not supports:
        return None

    mechanisms = _tuple_strings(
        _get(
            blueprint,
            "mechanisms",
            (),
        )
    )

    instructions = [
        "show what helps the theme develop constructively",
        "treat support as an existing structural resource",
        "connect support to the tension it helps regulate",
        "do not turn support into empty optimism",
    ]

    return CompositionSection(
        section_type="support",
        title="Support",
        purpose=(
            "Show what facilitates the process."
        ),
        priority=SECTION_PRIORITY["support"],
        sources=(
            "supports",
            "mechanisms",
            "tensions",
        ),
        instructions=tuple(
            instructions
        ),
        data={
            "supports": supports,
            "mechanisms": mechanisms,
        },
    )


def _build_development_section(
    blueprint,
) -> CompositionSection:

    dominant_process = _get(
        blueprint,
        "dominant_process",
        None,
    )

    dynamics = _tuple_strings(
        _get(
            blueprint,
            "dynamics",
            (),
        )
    )

    manifestations = _tuple_strings(
        _get(
            blueprint,
            "manifestations",
            (),
        )
    )

    instructions = [
        "describe how the theme unfolds through experience",
        "connect the dynamics into a single process",
        "show movement from mechanism toward manifestation",
        "avoid repetitive restatement of the mechanism",
    ]

    if dominant_process:
        instructions.append(
            f"keep {dominant_process} as the organizing process"
        )

    return CompositionSection(
        section_type="development",
        title="Development",
        purpose=(
            "Describe the movement of the theme."
        ),
        priority=SECTION_PRIORITY["development"],
        sources=(
            "dominant_process",
            "dynamics",
            "manifestations",
        ),
        instructions=tuple(
            instructions
        ),
        data={
            "dominant_process": dominant_process,
            "dynamics": dynamics,
            "manifestations": manifestations,
        },
    )


def _build_resolution_section(
    blueprint,
) -> CompositionSection:

    resolutions = _tuple_strings(
        _get(
            blueprint,
            "resolution",
            (),
        )
    )

    tensions = _tuple_strings(
        _get(
            blueprint,
            "tensions",
            (),
        )
    )

    supports = _tuple_strings(
        _get(
            blueprint,
            "supports",
            (),
        )
    )

    instructions = [
        "show the structural direction of resolution",
        "frame resolution as integration rather than a magical fix",
        "connect the resolution directly to the tensions",
        "use available supports where appropriate",
        "do not introduce a new theme at the end",
    ]

    return CompositionSection(
        section_type="resolution",
        title="Resolution",
        purpose=(
            "Show how the identified tension "
            "can be integrated."
        ),
        priority=SECTION_PRIORITY["resolution"],
        sources=(
            "resolution",
            "tensions",
            "supports",
        ),
        instructions=tuple(
            instructions
        ),
        data={
            "resolution": resolutions,
            "tensions": tensions,
            "supports": supports,
        },
    )


def _build_conclusion_section(
    blueprint,
) -> CompositionSection:

    core_theme = _get(
        blueprint,
        "core_theme",
        "general_theme",
    )

    dominant_process = _get(
        blueprint,
        "dominant_process",
        None,
    )

    resolution = _tuple_strings(
        _get(
            blueprint,
            "resolution",
            (),
        )
    )

    instructions = [
        "return to the central theme",
        "synthesize rather than introduce new information",
        "leave the reader with the essential structural insight",
        "end on integration rather than prediction",
    ]

    return CompositionSection(
        section_type="conclusion",
        title="Conclusion",
        purpose=(
            "Close the interpretation around "
            "the central insight."
        ),
        priority=SECTION_PRIORITY["conclusion"],
        sources=(
            "core_theme",
            "dominant_process",
            "resolution",
        ),
        instructions=tuple(
            instructions
        ),
        data={
            "core_theme": core_theme,
            "dominant_process": dominant_process,
            "resolution": resolution,
        },
    )


# ==========================================================
# SECTION ORDER
# ==========================================================

def _build_sections(
    blueprint,
) -> tuple[CompositionSection, ...]:

    sections = []

    # ------------------------------------------------------
    # 1. OPENING
    # ------------------------------------------------------

    sections.append(
        _build_opening_section(
            blueprint
        )
    )

    # ------------------------------------------------------
    # 2. CENTRAL THEME
    # ------------------------------------------------------

    sections.append(
        _build_central_theme_section(
            blueprint
        )
    )

    # ------------------------------------------------------
    # 3. MECHANISM
    # ------------------------------------------------------

    sections.append(
        _build_mechanism_section(
            blueprint
        )
    )

    # ------------------------------------------------------
    # 4. MANIFESTATION
    # ------------------------------------------------------

    sections.append(
        _build_manifestation_section(
            blueprint
        )
    )

    # ------------------------------------------------------
    # 5. TENSION
    # ------------------------------------------------------

    tension_section = _build_tension_section(
        blueprint
    )

    if tension_section is not None:
        sections.append(
            tension_section
        )

    # ------------------------------------------------------
    # 6. SUPPORT
    # ------------------------------------------------------

    support_section = _build_support_section(
        blueprint
    )

    if support_section is not None:
        sections.append(
            support_section
        )

    # ------------------------------------------------------
    # 7. DEVELOPMENT
    # ------------------------------------------------------

    sections.append(
        _build_development_section(
            blueprint
        )
    )

    # ------------------------------------------------------
    # 8. RESOLUTION
    # ------------------------------------------------------

    sections.append(
        _build_resolution_section(
            blueprint
        )
    )

    # ------------------------------------------------------
    # 9. CONCLUSION
    # ------------------------------------------------------

    sections.append(
        _build_conclusion_section(
            blueprint
        )
    )

    return tuple(
        sections
    )


# ==========================================================
# CONFIDENCE
# ==========================================================

def _calculate_confidence(
    blueprint,
) -> float:

    blueprint_confidence = float(
        _get(
            blueprint,
            "confidence",
            0.0,
        )
    )

    blueprint_data = _get(
        blueprint,
        "data",
        {},
    ) or {}

    semantic_confidence = float(
        blueprint_data.get(
            "semantic_confidence",
            0.0,
        )
    )

    interpretation_confidence = float(
        blueprint_data.get(
            "interpretation_confidence",
            0.0,
        )
    )

    evidence = _get(
        blueprint,
        "evidence",
        (),
    ) or ()

    evidence_confidence = 0.0

    if evidence:
        values = []

        for item in evidence:

            if not isinstance(
                item,
                dict,
            ):
                continue

            value = item.get(
                "confidence",
                0.0,
            )

            try:
                values.append(
                    float(value)
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

        if values:
            evidence_confidence = (
                sum(values)
                / len(values)
            )

    confidence = (
        blueprint_confidence * 0.50
        + semantic_confidence * 0.20
        + interpretation_confidence * 0.20
        + evidence_confidence * 0.10
    )

    return round(
        min(
            1.0,
            confidence,
        ),
        3,
    )


# ==========================================================
# BUILD ONE PLAN
# ==========================================================

def _build_composition_plan(
    blueprint,
) -> CompositionPlan:

    theme_key = _get(
        blueprint,
        "theme_key",
        "unknown",
    )

    strength = float(
        _get(
            blueprint,
            "strength",
            0.0,
        )
    )

    confidence = _calculate_confidence(
        blueprint
    )

    core_theme = _get(
        blueprint,
        "core_theme",
        "",
    )

    dominant_process = _get(
        blueprint,
        "dominant_process",
        None,
    )

    domains = _tuple_strings(
        _get(
            blueprint,
            "domains",
            (),
        )
    )

    planets = _tuple_strings(
        _get(
            blueprint,
            "planets",
            (),
        )
    )

    houses = _tuple_ints(
        _get(
            blueprint,
            "houses",
            (),
        )
    )

    tensions = _tuple_strings(
        _get(
            blueprint,
            "tensions",
            (),
        )
    )

    supports = _tuple_strings(
        _get(
            blueprint,
            "supports",
            (),
        )
    )

    resolutions = _tuple_strings(
        _get(
            blueprint,
            "resolution",
            (),
        )
    )

    fact_focus = _derive_fact_focus(
        blueprint
    )

    claims = _derive_central_claims(
        blueprint
    )

    evidence = _derive_evidence(
        blueprint
    )

    sections = _build_sections(
        blueprint
    )

    return CompositionPlan(
        theme_key=theme_key,
        strength=strength,
        confidence=confidence,
        core_theme=core_theme,
        dominant_process=dominant_process,
        domains=domains,
        planets=planets,
        houses=houses,
        fact_focus=fact_focus,
        central_claims=claims,
        sections=sections,
        tensions=tensions,
        supports=supports,
        resolutions=resolutions,
        evidence=evidence,
        data={
            "section_count": len(
                sections
            ),
            "claim_count": len(
                claims
            ),
            "fact_focus_count": len(
                fact_focus
            ),
            "evidence_count": len(
                evidence
            ),
            "semantic_confidence": _get(
                blueprint,
                "data",
                {},
            ).get(
                "semantic_confidence",
                0.0,
            ),
            "interpretation_confidence": _get(
                blueprint,
                "data",
                {},
            ).get(
                "interpretation_confidence",
                0.0,
            ),
            "composition_confidence": confidence,
        },
    )


# ==========================================================
# BUILD REPORT
# ==========================================================

def build_compositions(
    narratives,
    semantics=None,
    interpretations=None,
    themes=None,
    patterns=None,
    relations=None,
    priorities=None,
    chart=None,
) -> CompositionReport:
    """
    Строит CompositionReport.

    Основным источником является NarrativeReport.

    Остальные параметры сохранены в API
    для дальнейшего расширения Composer.

    Порядок:

        Narrative Blueprint
              ↓
        Composition Plan
    """

    narrative_list = _as_list(
        narratives
    )

    if not narrative_list:
        return CompositionReport()

    plans = []

    for blueprint in narrative_list:

        plan = _build_composition_plan(
            blueprint
        )

        if (
            plan.confidence
            < MIN_COMPOSITION_CONFIDENCE
        ):
            continue

        plans.append(
            plan
        )

    return CompositionReport(
        plans
    )


# ==========================================================
# УДОБНЫЕ ФУНКЦИИ
# ==========================================================

def strongest_compositions(
    report: CompositionReport,
    n: int = 5,
) -> list[CompositionPlan]:

    return report.top(n)


def compositions_for_theme(
    report: CompositionReport,
    theme_key: str,
) -> list[CompositionPlan]:

    return report.by_theme(
        theme_key
    )