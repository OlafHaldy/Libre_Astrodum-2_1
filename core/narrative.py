"""
Liber Astrodum

core/narrative.py

Narrative Blueprint Engine v1.1.

Преобразует:
    Semantics
    Interpretations
    Themes

в структурированный план будущей трактовки.

Narrative Engine НЕ генерирует литературный текст.
Narrative Engine НЕ использует LLM.

Его задача:
    определить центральную тему,
    основной процесс,
    механизмы,
    первичную и вторичную динамику,
    напряжения,
    поддержки,
    возможные проявления,
    направление разрешения.

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

MIN_BLUEPRINT_CONFIDENCE = 0.35


# ==========================================================
# ПОРЯДОК ПРОЦЕССОВ
# ==========================================================

PROCESS_PRIORITY = (
    "polarization",
    "friction",
    "fusion",
    "flow",
    "opportunity",
    "agency",
    "processing",
    "structural_constraint",
)


# ==========================================================
# ПОРЯДОК МЕХАНИЗМОВ
# ==========================================================

MECHANISM_PRIORITY = (
    "structural_constraint",
    "active_agency",
    "mental_component",
    "emotional_component",
    "expansive_component",
    "polarized_process",
    "facilitated_process",
)


# ==========================================================
# ПОРЯДОК ДИНАМИК
# ==========================================================

DYNAMIC_PRIORITY = (
    "polarization",
    "friction",
    "pressure",
    "conflict",
    "agency",
    "action",
    "mental_processing",
    "emotional_processing",
    "resource_management",
    "expansion",
    "expansive_drive",
    "flow",
    "support",
    "facilitation",
    "analysis",
    "effective_action",
)


# ==========================================================
# МЕХАНИЗМ → ДИНАМИКА
# ==========================================================

MECHANISM_DYNAMIC_MAP = {
    "structural_constraint": (
        "pressure",
    ),

    "active_agency": (
        "agency",
        "action",
    ),

    "mental_component": (
        "mental_processing",
        "analysis",
    ),

    "emotional_component": (
        "emotional_processing",
    ),

    "expansive_component": (
        "expansion",
        "expansive_drive",
    ),

    "polarized_process": (
        "polarization",
        "conflict",
    ),

    "facilitated_process": (
        "flow",
        "facilitation",
    ),
}


# ==========================================================
# НАПРЯЖЕНИЕ → ДИНАМИКА
# ==========================================================

TENSION_DYNAMIC_MAP = {
    "action_vs_constraint": (
        "conflict",
        "friction",
    ),

    "thought_vs_response": (
        "conflict",
        "friction",
    ),

    "expansion_vs_limitation": (
        "conflict",
        "polarization",
    ),

    "inner_conflict": (
        "conflict",
        "polarization",
    ),

    "polarization": (
        "polarization",
    ),

    "restriction": (
        "pressure",
    ),
}


# ==========================================================
# ПОДДЕРЖКА → ДИНАМИКА
# ==========================================================

SUPPORT_DYNAMIC_MAP = {
    "clear_execution": (
        "effective_action",
    ),

    "effective_action": (
        "effective_action",
    ),

    "facilitated_development": (
        "flow",
    ),

    "harmonious_flow": (
        "flow",
    ),

    "natural_flow": (
        "flow",
    ),

    "structured_support": (
        "support",
    ),

    "supportive_structure": (
        "support",
    ),
}


# ==========================================================
# МАНИФЕСТАЦИИ
# ==========================================================

MANIFESTATION_DYNAMICS = {
    "public_realization",
    "collective_interaction",
    "emotional_processing",
    "mental_processing",
    "resource_management",
    "creative_expression",
    "expansive_drive",
    "action",
    "agency",
    "analysis",
    "pressure",
    "conflict",
    "polarization",
    "flow",
    "support",
    "facilitation",
    "effective_action",
}


# ==========================================================
# NARRATIVE BLUEPRINT
# ==========================================================

@dataclass
class NarrativeBlueprint:
    """
    Структурированный план будущей интерпретации.

    Это ещё НЕ текст.

    core_theme:
        Центральная смысловая область.

    dominant_process:
        Главный процесс темы.

    mechanisms:
        Какие механизмы формируют тему.

    primary_dynamics:
        Главные способы проявления процесса.

    secondary_dynamics:
        Вторичные способы проявления.

    dynamics:
        Совместимый общий набор динамик.
        Первичные идут раньше вторичных.

    tensions:
        Основные внутренние противоречия.

    supports:
        Что облегчает развитие темы.

    manifestations:
        Возможные области проявления.

    resolution:
        Структурное направление разрешения.
    """

    theme_key: str

    strength: float
    confidence: float

    core_theme: str = ""

    dominant_process: str | None = None

    mechanisms: tuple[str, ...] = ()

    primary_dynamics: tuple[str, ...] = ()
    secondary_dynamics: tuple[str, ...] = ()
    dynamics: tuple[str, ...] = ()

    tensions: tuple[str, ...] = ()
    supports: tuple[str, ...] = ()

    manifestations: tuple[str, ...] = ()

    resolution: tuple[str, ...] = ()

    domains: tuple[str, ...] = ()
    planets: tuple[str, ...] = ()
    houses: tuple[int, ...] = ()

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
            "mechanisms": list(self.mechanisms),
            "primary_dynamics": list(
                self.primary_dynamics
            ),
            "secondary_dynamics": list(
                self.secondary_dynamics
            ),
            "dynamics": list(self.dynamics),
            "tensions": list(self.tensions),
            "supports": list(self.supports),
            "manifestations": list(self.manifestations),
            "resolution": list(self.resolution),
            "domains": list(self.domains),
            "planets": list(self.planets),
            "houses": list(self.houses),
            "evidence": list(self.evidence),
            "data": dict(self.data),
        }

    def __repr__(self) -> str:
        return (
            f"<NarrativeBlueprint "
            f"{self.theme_key} "
            f"strength={self.strength:.1f} "
            f"confidence={self.confidence:.2f}>"
        )


# ==========================================================
# NARRATIVE REPORT
# ==========================================================

class NarrativeReport:
    """
    Коллекция NarrativeBlueprint.
    """

    def __init__(
        self,
        blueprints: list[NarrativeBlueprint] | None = None,
    ):
        self._blueprints = (
            list(blueprints)
            if blueprints
            else []
        )

        self._blueprints.sort(
            key=lambda item: (
                item.strength,
                item.confidence,
            ),
            reverse=True,
        )

    def all(self) -> list[NarrativeBlueprint]:
        return list(self._blueprints)

    def to_list(self) -> list[dict]:
        return [
            blueprint.to_dict()
            for blueprint in self._blueprints
        ]

    def top(
        self,
        n: int = 5,
    ) -> list[NarrativeBlueprint]:
        return self._blueprints[:n]

    def __len__(self) -> int:
        return len(self._blueprints)

    def __iter__(self):
        return iter(self._blueprints)

    def __getitem__(self, index):
        return self._blueprints[index]

    @property
    def strongest(
        self,
    ) -> NarrativeBlueprint | None:
        return (
            self._blueprints[0]
            if self._blueprints
            else None
        )

    def by_theme(
        self,
        theme_key: str,
    ) -> list[NarrativeBlueprint]:
        return [
            blueprint
            for blueprint in self._blueprints
            if blueprint.theme_key == theme_key
        ]

    def __repr__(self) -> str:
        return (
            f"<NarrativeReport "
            f"blueprints={len(self._blueprints)}>"
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


def _get(item, name: str, default=None):
    """
    Безопасно получает значение как из объекта,
    так и из dict.
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
                value_item
                for value_item in value
                if isinstance(
                    value_item,
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
                value_item
                for value_item in value
                if isinstance(
                    value_item,
                    int,
                )
            }
        )
    )


def _unique(values) -> tuple:
    result = []

    for value in values:

        if (
            value
            and value not in result
        ):
            result.append(value)

    return tuple(result)


def _ordered_unique(
    values,
    priority: tuple[str, ...],
) -> tuple[str, ...]:
    """
    Уникальные строковые значения,
    отсортированные по смысловому приоритету.
    """

    values = {
        value
        for value in values
        if isinstance(
            value,
            str,
        )
    }

    priority_index = {
        value: index
        for index, value in enumerate(
            priority
        )
    }

    return tuple(
        sorted(
            values,
            key=lambda value: (
                priority_index.get(
                    value,
                    9999,
                ),
                value,
            ),
        )
    )


# ==========================================================
# МЕХАНИЗМЫ
# ==========================================================

def _derive_mechanisms(
    interpretation,
    semantics,
) -> tuple[str, ...]:

    mechanisms = []

    interpretation_mechanisms = _get(
        interpretation,
        "mechanisms",
        (),
    ) or ()

    semantic_claims = _get(
        semantics,
        "claims",
        (),
    ) or ()

    for key in MECHANISM_PRIORITY:

        if key in interpretation_mechanisms:
            mechanisms.append(key)
            continue

        for claim in semantic_claims:

            claim_key = _get(
                claim,
                "key",
                "",
            )

            if claim_key == key:
                mechanisms.append(key)
                break

    return tuple(mechanisms)


# ==========================================================
# ДОМІНИРУЮЩИЙ ПРОЦЕСС
# ==========================================================

def _derive_dominant_process(
    interpretation,
    semantics,
) -> str | None:

    semantic_processes = set(
        _get(
            semantics,
            "processes",
            (),
        )
        or ()
    )

    explicit_process = _get(
        interpretation,
        "dominant_process",
        None,
    )

    tensions = set(
        _get(
            interpretation,
            "tensions",
            (),
        )
        or ()
    )

    mechanisms = set(
        _get(
            interpretation,
            "mechanisms",
            (),
        )
        or ()
    )

    # ------------------------------------------------------
    # 1. Явный процесс предыдущего слоя
    # ------------------------------------------------------

    if (
        isinstance(
            explicit_process,
            str,
        )
        and explicit_process
    ):
        return explicit_process

    # ------------------------------------------------------
    # 2. Явный процесс Semantics
    # ------------------------------------------------------

    for process in PROCESS_PRIORITY:

        if process in semantic_processes:
            return process

    # ------------------------------------------------------
    # 3. Механизмы
    # ------------------------------------------------------

    if "polarized_process" in mechanisms:
        return "polarization"

    if "facilitated_process" in mechanisms:
        return "flow"

    # ------------------------------------------------------
    # 4. Напряжения
    # ------------------------------------------------------

    if any(
        value in tensions
        for value in {
            "expansion_vs_limitation",
            "inner_conflict",
            "polarization",
        }
    ):
        return "polarization"

    if any(
        value in tensions
        for value in {
            "action_vs_constraint",
            "thought_vs_response",
        }
    ):
        return "friction"

    if "restriction" in tensions:
        return "friction"

    # ------------------------------------------------------
    # 5. Механическая реконструкция
    # ------------------------------------------------------

    if "structural_constraint" in mechanisms:
        return "friction"

    if "active_agency" in mechanisms:
        return "agency"

    if "mental_component" in mechanisms:
        return "processing"

    return None


# ==========================================================
# НАПРЯЖЕНИЯ
# ==========================================================

def _derive_tensions(
    interpretation,
    semantics,
) -> tuple[str, ...]:

    result = []

    values = []

    values.extend(
        _get(
            interpretation,
            "tensions",
            (),
        )
        or ()
    )

    values.extend(
        _get(
            semantics,
            "tensions",
            (),
        )
        or ()
    )

    for value in values:

        if isinstance(
            value,
            str,
        ):
            result.append(value)

    return _unique(result)


# ==========================================================
# ПОДДЕРЖКИ
# ==========================================================

def _derive_supports(
    interpretation,
    semantics,
) -> tuple[str, ...]:

    result = []

    values = []

    values.extend(
        _get(
            interpretation,
            "supports",
            (),
        )
        or ()
    )

    values.extend(
        _get(
            semantics,
            "supports",
            (),
        )
        or ()
    )

    for value in values:

        if isinstance(
            value,
            str,
        ):
            result.append(value)

    return _unique(result)


# ==========================================================
# ДИНАМИКА
# ==========================================================

def _derive_dynamics(
    interpretation,
    mechanisms: tuple[str, ...],
    tensions: tuple[str, ...],
    supports: tuple[str, ...],
    dominant_process: str | None,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
]:
    """
    Формирует три уровня динамики:

        primary:
            главное развитие темы;

        secondary:
            вторичные проявления;

        dynamics:
            объединённый совместимый набор.

    Правило:

        Interpretation
            ↓
        mechanisms
            ↓
        tensions
            ↓
        supports
            ↓
        dominant_process
    """

    primary = []
    secondary = []

    interpretation_dynamics = _get(
        interpretation,
        "dynamics",
        (),
    ) or ()

    # ------------------------------------------------------
    # 1. Реальные dynamics Interpretation
    #
    # Они имеют высший вес, потому что были
    # выведены предыдущим уровнем.
    # ------------------------------------------------------

    for value in interpretation_dynamics:

        if not isinstance(
            value,
            str,
        ):
            continue

        if (
            dominant_process
            and value == dominant_process
        ):
            primary.append(value)
            continue

        if value in {
            "polarization",
            "friction",
            "pressure",
            "conflict",
        }:
            primary.append(value)
            continue

        secondary.append(value)

    # ------------------------------------------------------
    # 2. Механизмы
    # ------------------------------------------------------

    for mechanism in mechanisms:

        generated = (
            MECHANISM_DYNAMIC_MAP.get(
                mechanism,
                (),
            )
        )

        for value in generated:

            if value in {
                "polarization",
                "friction",
                "pressure",
                "conflict",
            }:
                primary.append(value)
            else:
                secondary.append(value)

    # ------------------------------------------------------
    # 3. Напряжения
    # ------------------------------------------------------

    for tension in tensions:

        generated = (
            TENSION_DYNAMIC_MAP.get(
                tension,
                (),
            )
        )

        for value in generated:
            primary.append(value)

    # ------------------------------------------------------
    # 4. Поддержки
    # ------------------------------------------------------

    for support in supports:

        generated = (
            SUPPORT_DYNAMIC_MAP.get(
                support,
                (),
            )
        )

        for value in generated:
            secondary.append(value)

    # ------------------------------------------------------
    # 5. Доминирующий процесс
    # ------------------------------------------------------

    if dominant_process:
        primary.append(
            dominant_process
        )

    # ------------------------------------------------------
    # Ранжирование
    # ------------------------------------------------------

    primary = list(
        _ordered_unique(
            primary,
            DYNAMIC_PRIORITY,
        )
    )

    secondary = list(
        _ordered_unique(
            secondary,
            DYNAMIC_PRIORITY,
        )
    )

    # ------------------------------------------------------
    # Убираем из secondary то,
    # что уже стало primary.
    # ------------------------------------------------------

    primary_set = set(primary)

    secondary = [
        value
        for value in secondary
        if value not in primary_set
    ]

    # ------------------------------------------------------
    # Объединённый поток.
    # Primary всегда раньше Secondary.
    # ------------------------------------------------------

    dynamics = tuple(
        primary
        + secondary
    )

    return (
        tuple(primary),
        tuple(secondary),
        dynamics,
    )


# ==========================================================
# ПРОЯВЛЕНИЯ
# ==========================================================

def _derive_manifestations(
    semantics,
    primary_dynamics: tuple[str, ...],
    secondary_dynamics: tuple[str, ...],
) -> tuple[str, ...]:

    manifestations = []

    domains = _get(
        semantics,
        "domains",
        (),
    ) or ()

    keywords = _get(
        semantics,
        "keywords",
        (),
    ) or ()

    # ------------------------------------------------------
    # 1. ДОМЕНЫ
    # ------------------------------------------------------

    for domain in domains:

        if isinstance(
            domain,
            str,
        ):
            manifestations.append(
                f"domain:{domain}"
            )

    # ------------------------------------------------------
    # 2. ОБЛАСТИ ИЗ КЛЮЧЕВЫХ СЛОВ
    # ------------------------------------------------------

    area_keywords = {
        "career",
        "community",
        "retreat",
        "resources",
        "creativity",
        "partnership",
        "identity",
        "meaning",
        "communication",
        "home",
        "work_health",
        "shared_resources",
    }

    for keyword in keywords:

        if keyword in area_keywords:
            manifestations.append(
                f"area:{keyword}"
            )

    # ------------------------------------------------------
    # 3. PRIMARY PROCESS
    #
    # Главные динамики важнее вторичных.
    # ------------------------------------------------------

    for dynamic in primary_dynamics:

        if dynamic in MANIFESTATION_DYNAMICS:
            manifestations.append(
                f"process:{dynamic}"
            )

    # ------------------------------------------------------
    # 4. SECONDARY PROCESS
    #
    # Берём только ограниченный набор,
    # чтобы blueprint не превращался
    # в список из двадцати признаков.
    # ------------------------------------------------------

    secondary_limit = 4

    count = 0

    for dynamic in secondary_dynamics:

        if count >= secondary_limit:
            break

        if dynamic not in MANIFESTATION_DYNAMICS:
            continue

        manifestations.append(
            f"process:{dynamic}"
        )

        count += 1

    return _unique(
        manifestations
    )


# ==========================================================
# РАЗРЕШЕНИЕ
# ==========================================================

def _derive_resolution(
    tensions,
    supports,
    mechanisms,
) -> tuple[str, ...]:

    result = []

    tension_set = set(
        tensions
    )

    support_set = set(
        supports
    )

    mechanism_set = set(
        mechanisms
    )

    # ------------------------------------------------------
    # 1. ПОДДЕРЖКА
    # ------------------------------------------------------

    if support_set:
        result.append(
            "use_available_support"
        )

    # ------------------------------------------------------
    # 2. СТРУКТУРА
    # ------------------------------------------------------

    if (
        "structural_constraint"
        in mechanism_set
    ):
        result.append(
            "integrate_structure"
        )

    # ------------------------------------------------------
    # 3. ДЕЙСТВИЕ
    # ------------------------------------------------------

    if (
        "active_agency"
        in mechanism_set
    ):
        result.append(
            "direct_action"
        )

    # ------------------------------------------------------
    # 4. РАЗУМ / ЭМОЦИЯ
    # ------------------------------------------------------

    if (
        "mental_component"
        in mechanism_set
        and "emotional_component"
        in mechanism_set
    ):
        result.append(
            "integrate_thought_and_response"
        )

    # ------------------------------------------------------
    # 5. ПОЛЯРИЗАЦИЯ
    # ------------------------------------------------------

    if (
        "polarized_process"
        in mechanism_set
        or "polarization" in tension_set
        or "expansion_vs_limitation"
        in tension_set
    ):
        result.append(
            "reconcile_polarity"
        )

    # ------------------------------------------------------
    # 6. НЕТ ПОЗИТИВНОГО КОНТУРА
    # ------------------------------------------------------

    if (
        not support_set
        and tension_set
        and not result
    ):
        result.append(
            "contain_and_observe"
        )

    return _unique(result)


# ==========================================================
# CORE THEME
# ==========================================================

def _derive_core_theme(
    semantics,
    interpretation,
) -> str:

    domains = _get(
        semantics,
        "domains",
        (),
    ) or ()

    mechanisms = _get(
        interpretation,
        "mechanisms",
        (),
    ) or ()

    tensions = set(
        _get(
            interpretation,
            "tensions",
            (),
        )
        or ()
    )

    supports = set(
        _get(
            interpretation,
            "supports",
            (),
        )
        or ()
    )

    primary_domain = (
        sorted(domains)[0]
        if domains
        else None
    )

    # ------------------------------------------------------
    # 1. ПОЛЯРИЗАЦИЯ
    # ------------------------------------------------------

    if any(
        value in tensions
        for value in {
            "expansion_vs_limitation",
            "inner_conflict",
            "polarization",
        }
    ):

        if primary_domain:
            return (
                f"{primary_domain}_polarization"
            )

        return "polarized_development"

    # ------------------------------------------------------
    # 2. ОГРАНИЧЕНИЕ
    # ------------------------------------------------------

    if any(
        value in tensions
        for value in {
            "action_vs_constraint",
            "thought_vs_response",
            "restriction",
        }
    ):

        if primary_domain:
            return (
                f"{primary_domain}_under_constraint"
            )

        return "structural_constraint"

    # ------------------------------------------------------
    # 3. ПОДДЕРЖКА
    # ------------------------------------------------------

    if (
        supports
        and primary_domain
    ):
        return (
            f"{primary_domain}_supported_development"
        )

    # ------------------------------------------------------
    # 4. ОБЛАСТЬ
    # ------------------------------------------------------

    if primary_domain:
        return primary_domain

    # ------------------------------------------------------
    # 5. МЕХАНИЗМ
    # ------------------------------------------------------

    if mechanisms:
        return mechanisms[0]

    return "general_theme"


# ==========================================================
# CONFIDENCE
# ==========================================================

def _calculate_confidence(
    semantics,
    interpretation,
) -> float:

    semantic_data = _get(
        semantics,
        "data",
        {},
    ) or {}

    semantic_confidence = float(
        semantic_data.get(
            "semantic_confidence",
            0.0,
        )
    )

    interpretation_confidence = float(
        _get(
            interpretation,
            "confidence",
            0.0,
        )
    )

    confidence = (
        semantic_confidence * 0.45
        + interpretation_confidence * 0.55
    )

    return round(
        min(
            1.0,
            confidence,
        ),
        3,
    )


# ==========================================================
# EVIDENCE
# ==========================================================

def _build_evidence(
    semantics,
    interpretation,
) -> tuple[dict, ...]:

    result = []

    # ------------------------------------------------------
    # SEMANTICS CLAIMS
    # ------------------------------------------------------

    claims = _get(
        semantics,
        "claims",
        (),
    ) or ()

    for claim in claims:

        result.append(
            {
                "source": "semantics",
                "kind": _get(
                    claim,
                    "kind",
                    "",
                ),
                "key": _get(
                    claim,
                    "key",
                    "",
                ),
                "confidence": _get(
                    claim,
                    "confidence",
                    0.0,
                ),
            }
        )

    # ------------------------------------------------------
    # INTERPRETATION CLAIMS
    # ------------------------------------------------------

    interpretation_claims = _get(
        interpretation,
        "claims",
        (),
    ) or ()

    for claim in interpretation_claims:

        result.append(
            {
                "source": "interpretation",
                "kind": _get(
                    claim,
                    "kind",
                    "",
                ),
                "key": _get(
                    claim,
                    "key",
                    "",
                ),
                "confidence": _get(
                    claim,
                    "confidence",
                    0.0,
                ),
            }
        )

    return tuple(result)


# ==========================================================
# BUILD ONE BLUEPRINT
# ==========================================================

def _build_blueprint(
    semantics,
    interpretation,
    theme=None,
) -> NarrativeBlueprint:

    theme_key = _get(
        interpretation,
        "theme_key",
        _get(
            semantics,
            "theme_key",
            "unknown",
        ),
    )

    strength = float(
        _get(
            interpretation,
            "strength",
            _get(
                semantics,
                "strength",
                0.0,
            ),
        )
    )

    confidence = _calculate_confidence(
        semantics,
        interpretation,
    )

    mechanisms = _derive_mechanisms(
        interpretation,
        semantics,
    )

    tensions = _derive_tensions(
        interpretation,
        semantics,
    )

    supports = _derive_supports(
        interpretation,
        semantics,
    )

    dominant_process = _derive_dominant_process(
        interpretation,
        semantics,
    )

    (
        primary_dynamics,
        secondary_dynamics,
        dynamics,
    ) = _derive_dynamics(
        interpretation,
        mechanisms,
        tensions,
        supports,
        dominant_process,
    )

    manifestations = _derive_manifestations(
        semantics,
        primary_dynamics,
        secondary_dynamics,
    )

    resolution = _derive_resolution(
        tensions,
        supports,
        mechanisms,
    )

    core_theme = _derive_core_theme(
        semantics,
        interpretation,
    )

    domains = _tuple_strings(
        _get(
            semantics,
            "domains",
            (),
        )
    )

    planets = _tuple_strings(
        _get(
            semantics,
            "planets",
            (),
        )
    )

    houses = _tuple_ints(
        _get(
            semantics,
            "houses",
            (),
        )
    )

    evidence = _build_evidence(
        semantics,
        interpretation,
    )

    semantic_data = _get(
        semantics,
        "data",
        {},
    ) or {}

    interpretation_confidence = _get(
        interpretation,
        "confidence",
        0.0,
    )

    return NarrativeBlueprint(
        theme_key=theme_key,
        strength=strength,
        confidence=confidence,
        core_theme=core_theme,
        dominant_process=dominant_process,
        mechanisms=mechanisms,
        primary_dynamics=primary_dynamics,
        secondary_dynamics=secondary_dynamics,
        dynamics=dynamics,
        tensions=tensions,
        supports=supports,
        manifestations=manifestations,
        resolution=resolution,
        domains=domains,
        planets=planets,
        houses=houses,
        evidence=evidence,
        data={
            "semantic_confidence": semantic_data.get(
                "semantic_confidence",
                0.0,
            ),
            "interpretation_confidence": (
                interpretation_confidence
            ),
            "evidence_count": len(
                evidence
            ),
            "dynamic_count": len(
                dynamics
            ),
            "primary_dynamic_count": len(
                primary_dynamics
            ),
            "secondary_dynamic_count": len(
                secondary_dynamics
            ),
            "mechanism_count": len(
                mechanisms
            ),
            "tension_count": len(
                tensions
            ),
            "support_count": len(
                supports
            ),
        },
    )


# ==========================================================
# BUILD REPORT
# ==========================================================

def build_narrative(
    semantics,
    interpretations,
    themes=None,
    chart=None,
    patterns=None,
    relations=None,
    priorities=None,
) -> NarrativeReport:
    """
    Строит NarrativeReport.

    Дополнительные параметры:
        chart
        themes
        patterns
        relations
        priorities

    сохраняются в API для совместимости
    и последующего расширения.
    """

    semantic_list = _as_list(
        semantics
    )

    interpretation_list = _as_list(
        interpretations
    )

    if not semantic_list:
        return NarrativeReport()

    if not interpretation_list:
        return NarrativeReport()

    themes_list = _as_list(
        themes
    )

    theme_map = {
        _get(
            theme,
            "theme_key",
            "",
        ): theme
        for theme in themes_list
    }

    semantics_map = {
        _get(
            semantic,
            "theme_key",
            "",
        ): semantic
        for semantic in semantic_list
    }

    blueprints = []

    for interpretation in interpretation_list:

        theme_key = _get(
            interpretation,
            "theme_key",
            "",
        )

        semantics_profile = (
            semantics_map.get(
                theme_key
            )
        )

        if semantics_profile is None:
            continue

        theme = theme_map.get(
            theme_key
        )

        blueprint = _build_blueprint(
            semantics_profile,
            interpretation,
            theme=theme,
        )

        if (
            blueprint.confidence
            < MIN_BLUEPRINT_CONFIDENCE
        ):
            continue

        blueprints.append(
            blueprint
        )

    return NarrativeReport(
        blueprints
    )


# ==========================================================
# УДОБНЫЕ ФУНКЦИИ
# ==========================================================

def strongest_narratives(
    report: NarrativeReport,
    n: int = 5,
) -> list[NarrativeBlueprint]:

    return report.top(n)


def narratives_for_theme(
    report: NarrativeReport,
    theme_key: str,
) -> list[NarrativeBlueprint]:

    return report.by_theme(
        theme_key
    )