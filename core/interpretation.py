"""
Liber Astrodum

core/interpretation.py

Interpretation Engine v1.0.

Преобразует Semantic Profiles в структурированные
машинные интерпретационные модели.

Поток:

    Chart
      ↓
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
    Interpretation

Interpretation Engine НЕ генерирует литературный текст.
Interpretation Engine НЕ использует LLM.

Его задача:

    объединить семантические claims,
    определить действующие механизмы,
    выделить контексты,
    определить характер динамики,
    зафиксировать ограничения,
    определить поддерживающие факторы,
    сформировать структурированный материал
    для следующего Narrative / LLM слоя.

Основной принцип:

    Семантика описывает ЗНАЧЕНИЯ.

    Interpretation описывает,
    КАК ЭТИ ЗНАЧЕНИЯ ВЗАИМОДЕЙСТВУЮТ.

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

MIN_INTERPRETATION_CONFIDENCE = 0.35

MECHANISM_WEIGHTS = {
    "structural_constraint": 1.00,
    "active_agency": 1.00,
    "mental_component": 0.95,
    "emotional_component": 0.95,
    "expansive_component": 0.95,
    "polarized_process": 1.10,
    "facilitated_process": 0.95,
    "tension_with_internal_support": 1.15,
}


# ==========================================================
# SEMANTIC HELPERS
# ==========================================================

def _as_list(collection) -> list:
    if collection is None:
        return []

    if hasattr(collection, "all"):
        return collection.all()

    return list(collection)


def _get_value(obj, name: str, default=None):
    return getattr(obj, name, default)


def _claim_kind(claim) -> str:
    return getattr(claim, "kind", "")


def _claim_key(claim) -> str:
    return getattr(claim, "key", "")


def _claim_strength(claim) -> float:
    try:
        return float(
            getattr(
                claim,
                "strength",
                0.0,
            )
        )
    except (TypeError, ValueError):
        return 0.0


def _claim_confidence(claim) -> float:
    try:
        return float(
            getattr(
                claim,
                "confidence",
                0.0,
            )
        )
    except (TypeError, ValueError):
        return 0.0


def _claim_data(claim) -> dict:
    data = getattr(
        claim,
        "data",
        {},
    )

    return (
        dict(data)
        if isinstance(data, dict)
        else {}
    )


# ==========================================================
# INTERPRETATION CLAIM
# ==========================================================

@dataclass
class InterpretationClaim:
    """
    Одно машинное интерпретационное утверждение.

    kind:
        Категория механизма.

    key:
        Машинный ключ утверждения.

    strength:
        Сила утверждения 0..100.

    confidence:
        Уверенность 0..1.

    source:
        Источник утверждения.

    data:
        Дополнительные сведения.
    """

    kind: str
    key: str
    strength: float
    confidence: float
    source: str

    data: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "key": self.key,
            "strength": self.strength,
            "confidence": self.confidence,
            "source": self.source,
            "data": dict(self.data),
        }

    def __repr__(self) -> str:
        return (
            f"<InterpretationClaim "
            f"{self.kind}:{self.key} "
            f"{self.strength:.1f}>"
        )


# ==========================================================
# INTERPRETATION PROFILE
# ==========================================================

@dataclass
class InterpretationProfile:
    """
    Машинная интерпретация одной Semantic Profile.
    """

    theme_key: str

    strength: float
    coherence: float
    confidence: float

    domains: tuple[str, ...] = ()
    planets: tuple[str, ...] = ()
    houses: tuple[int, ...] = ()

    mechanisms: tuple[str, ...] = ()

    active_dynamics: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    supports: tuple[str, ...] = ()
    tensions: tuple[str, ...] = ()

    claims: tuple[InterpretationClaim, ...] = ()

    data: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict:
        return {
            "theme_key": self.theme_key,
            "strength": self.strength,
            "coherence": self.coherence,
            "confidence": self.confidence,
            "domains": list(self.domains),
            "planets": list(self.planets),
            "houses": list(self.houses),
            "mechanisms": list(self.mechanisms),
            "active_dynamics": list(
                self.active_dynamics
            ),
            "constraints": list(
                self.constraints
            ),
            "supports": list(
                self.supports
            ),
            "tensions": list(
                self.tensions
            ),
            "claims": [
                claim.to_dict()
                for claim in self.claims
            ],
            "data": dict(self.data),
        }

    def __repr__(self) -> str:
        return (
            f"<InterpretationProfile "
            f"{self.theme_key} "
            f"confidence={self.confidence:.2f}>"
        )


# ==========================================================
# INTERPRETATION REPORT
# ==========================================================

class InterpretationReport:
    """
    Коллекция интерпретационных профилей.
    """

    def __init__(
        self,
        profiles: list[InterpretationProfile] | None = None,
    ):
        self._profiles = (
            list(profiles)
            if profiles
            else []
        )

        self._profiles.sort(
            key=lambda profile: (
                profile.strength,
                profile.confidence,
                profile.coherence,
            ),
            reverse=True,
        )

    def all(self) -> list[InterpretationProfile]:
        return list(self._profiles)

    def to_list(self) -> list[dict]:
        return [
            profile.to_dict()
            for profile in self._profiles
        ]

    def __len__(self) -> int:
        return len(self._profiles)

    def __iter__(self):
        return iter(self._profiles)

    def __getitem__(self, index):
        return self._profiles[index]

    def top(
        self,
        n: int = 10,
    ) -> list[InterpretationProfile]:
        return self._profiles[:n]

    @property
    def strongest(
        self,
    ) -> InterpretationProfile | None:
        return (
            self._profiles[0]
            if self._profiles
            else None
        )

    def by_theme(
        self,
        theme_key: str,
    ) -> list[InterpretationProfile]:
        return [
            profile
            for profile in self._profiles
            if profile.theme_key == theme_key
        ]

    def by_domain(
        self,
        domain: str,
    ) -> list[InterpretationProfile]:
        return [
            profile
            for profile in self._profiles
            if domain in profile.domains
        ]

    def by_mechanism(
        self,
        mechanism: str,
    ) -> list[InterpretationProfile]:
        return [
            profile
            for profile in self._profiles
            if mechanism in profile.mechanisms
        ]

    def __repr__(self) -> str:
        return (
            f"<InterpretationReport "
            f"profiles={len(self._profiles)}>"
        )


# ==========================================================
# УНИКАЛИЗАЦИЯ
# ==========================================================

def _unique(values) -> tuple:
    result = []

    for value in values:
        if value not in result:
            result.append(value)

    return tuple(result)


# ==========================================================
# ИЗВЛЕЧЕНИЕ SEMANTIC ДАННЫХ
# ==========================================================

def _semantic_domains(profile) -> list[str]:
    value = _get_value(
        profile,
        "domains",
        (),
    )

    return [
        value
        for value in value
        if isinstance(value, str)
    ]


def _semantic_keywords(profile) -> list[str]:
    value = _get_value(
        profile,
        "keywords",
        (),
    )

    return [
        value
        for value in value
        if isinstance(value, str)
    ]


def _semantic_planets(profile) -> list[str]:
    value = _get_value(
        profile,
        "planets",
        (),
    )

    return [
        value
        for value in value
        if isinstance(value, str)
    ]


def _semantic_houses(profile) -> list[int]:
    value = _get_value(
        profile,
        "houses",
        (),
    )

    return [
        value
        for value in value
        if isinstance(value, int)
    ]


def _semantic_processes(profile) -> list[str]:
    value = _get_value(
        profile,
        "processes",
        (),
    )

    return [
        value
        for value in value
        if isinstance(value, str)
    ]


def _semantic_roles(profile) -> list[str]:
    value = _get_value(
        profile,
        "primary_roles",
        (),
    )

    return [
        value
        for value in value
        if isinstance(value, str)
    ]


def _semantic_secondary_roles(profile) -> list[str]:
    value = _get_value(
        profile,
        "secondary_roles",
        (),
    )

    return [
        value
        for value in value
        if isinstance(value, str)
    ]


def _semantic_claims(profile) -> list:
    value = _get_value(
        profile,
        "claims",
        (),
    )

    return list(value) if value else []


# ==========================================================
# КЛАССИФИКАЦИЯ МЕХАНИЗМОВ
# ==========================================================

def _derive_mechanisms(
    profile,
    claims: list,
) -> tuple[
    set[str],
    set[str],
    set[str],
    set[str],
]:
    """
    Возвращает:

        mechanisms
        active_dynamics
        constraints
        supports
    """

    mechanisms = set()
    active_dynamics = set()
    constraints = set()
    supports = set()

    processes = set(
        _semantic_processes(profile)
    )

    roles = set(
        _semantic_roles(profile)
    )

    secondary_roles = set(
        _semantic_secondary_roles(profile)
    )

    domains = set(
        _semantic_domains(profile)
    )

    for claim in claims:

        key = _claim_key(claim)

        # --------------------------------------------------
        # СТРУКТУРНОЕ ОГРАНИЧЕНИЕ
        # --------------------------------------------------

        if key == "structural_constraint":
            mechanisms.add(
                "structural_constraint"
            )
            constraints.add(
                "restriction"
            )
            active_dynamics.add(
                "pressure"
            )

        # --------------------------------------------------
        # АКТИВНОЕ ДЕЙСТВИЕ
        # --------------------------------------------------

        elif key == "active_agency":
            mechanisms.add(
                "active_agency"
            )
            active_dynamics.add(
                "action"
            )

        # --------------------------------------------------
        # МЫШЛЕНИЕ
        # --------------------------------------------------

        elif key == "mental_component":
            mechanisms.add(
                "mental_component"
            )
            active_dynamics.add(
                "analysis"
            )

        # --------------------------------------------------
        # ЭМОЦИИ
        # --------------------------------------------------

        elif key == "emotional_component":
            mechanisms.add(
                "emotional_component"
            )
            active_dynamics.add(
                "response"
            )

        # --------------------------------------------------
        # РАСШИРЕНИЕ
        # --------------------------------------------------

        elif key == "expansive_component":
            mechanisms.add(
                "expansive_component"
            )
            active_dynamics.add(
                "expansion"
            )

        # --------------------------------------------------
        # ПОЛЯРИЗАЦИЯ
        # --------------------------------------------------

        elif key == "polarized_process":
            mechanisms.add(
                "polarized_process"
            )
            active_dynamics.add(
                "polarization"
            )
            constraints.add(
                "inner_conflict"
            )

        # --------------------------------------------------
        # ПОТОК
        # --------------------------------------------------

        elif key == "facilitated_process":
            mechanisms.add(
                "facilitated_process"
            )
            supports.add(
                "natural_flow"
            )

        # --------------------------------------------------
        # НАПРЯЖЕНИЕ + ПОДДЕРЖКА
        # --------------------------------------------------

        elif key == "tension_with_internal_support":
            mechanisms.add(
                "tension_with_internal_support"
            )
            active_dynamics.add(
                "integration"
            )
            supports.add(
                "internal_support"
            )

    # ======================================================
    # ДОПОЛНИТЕЛЬНЫЕ СВЯЗИ
    # ======================================================

    if "flow" in processes:
        supports.add(
            "facilitated_development"
        )

    if "polarization" in processes:
        constraints.add(
            "polarized_development"
        )

    if "conflict" in roles:
        active_dynamics.add(
            "conflict"
        )

    if "support" in roles:
        supports.add(
            "supportive_structure"
        )

    if "structural_pressure" in secondary_roles:
        constraints.add(
            "structural_pressure"
        )

    if "agency" in secondary_roles:
        active_dynamics.add(
            "agency"
        )

    if "mental_processing" in secondary_roles:
        active_dynamics.add(
            "mental_processing"
        )

    if "emotional_processing" in secondary_roles:
        active_dynamics.add(
            "emotional_processing"
        )

    if "expansion" in secondary_roles:
        active_dynamics.add(
            "expansive_drive"
        )

    # ------------------------------------------------------
    # КОНТЕКСТЫ ДОМА
    # ------------------------------------------------------

    if "career" in domains:
        active_dynamics.add(
            "public_realization"
        )

    if "community" in domains:
        active_dynamics.add(
            "collective_interaction"
        )

    if "retreat" in domains:
        constraints.add(
            "withdrawal"
        )

    if "resources" in domains:
        active_dynamics.add(
            "resource_management"
        )

    if "creativity" in domains:
        active_dynamics.add(
            "creative_expression"
        )

    return (
        mechanisms,
        active_dynamics,
        constraints,
        supports,
    )


# ==========================================================
# ТИП ДИНАМИКИ
# ==========================================================

def _derive_tensions(
    profile,
    mechanisms: set[str],
    constraints: set[str],
) -> set[str]:
    result = set()

    if "polarized_process" in mechanisms:
        result.add(
            "polarization"
        )

    if "structural_constraint" in mechanisms:
        result.add(
            "restriction"
        )

    if (
        "active_agency" in mechanisms
        and "structural_constraint" in mechanisms
    ):
        result.add(
            "action_vs_constraint"
        )

    if (
        "expansive_component" in mechanisms
        and "structural_constraint" in mechanisms
    ):
        result.add(
            "expansion_vs_limitation"
        )

    if (
        "mental_component" in mechanisms
        and "emotional_component" in mechanisms
    ):
        result.add(
            "thought_vs_response"
        )

    if "inner_conflict" in constraints:
        result.add(
            "inner_conflict"
        )

    return result


def _derive_supports(
    mechanisms: set[str],
    supports: set[str],
) -> set[str]:
    result = set(supports)

    if "facilitated_process" in mechanisms:
        result.add(
            "harmonious_flow"
        )

    if (
        "active_agency" in mechanisms
        and "facilitated_process" in mechanisms
    ):
        result.add(
            "effective_action"
        )

    if (
        "mental_component" in mechanisms
        and "facilitated_process" in mechanisms
    ):
        result.add(
            "clear_execution"
        )

    if (
        "structural_constraint" in mechanisms
        and "facilitated_process" in mechanisms
    ):
        result.add(
            "structured_support"
        )

    return result


# ==========================================================
# INTERPRETATION CLAIMS
# ==========================================================

def _build_interpretation_claims(
    profile,
    mechanisms: set[str],
    active_dynamics: set[str],
    constraints: set[str],
    supports: set[str],
    tensions: set[str],
) -> list[InterpretationClaim]:
    """
    Формирует компактные машинные claims.
    """

    claims = []

    strength = float(
        _get_value(
            profile,
            "strength",
            0.0,
        )
    )

    semantic_confidence = float(
        _get_value(
            profile,
            "data",
            {},
        ).get(
            "semantic_confidence",
            0.0,
        )
    )

    # ------------------------------------------------------
    # МЕХАНИЗМЫ
    # ------------------------------------------------------

    for mechanism in sorted(
        mechanisms
    ):

        weight = MECHANISM_WEIGHTS.get(
            mechanism,
            0.75,
        )

        claim_strength = min(
            100.0,
            strength * weight,
        )

        claims.append(
            InterpretationClaim(
                kind="mechanism",
                key=mechanism,
                strength=round(
                    claim_strength,
                    2,
                ),
                confidence=semantic_confidence,
                source="semantic_profile",
                data={
                    "mechanism": mechanism,
                },
            )
        )

    # ------------------------------------------------------
    # ДИНАМИКА
    # ------------------------------------------------------

    for dynamic in sorted(
        active_dynamics
    ):

        claims.append(
            InterpretationClaim(
                kind="dynamic",
                key=dynamic,
                strength=round(
                    strength,
                    2,
                ),
                confidence=semantic_confidence,
                source="derived_dynamics",
                data={
                    "dynamic": dynamic,
                },
            )
        )

    # ------------------------------------------------------
    # ОГРАНИЧЕНИЯ
    # ------------------------------------------------------

    for constraint in sorted(
        constraints
    ):

        claims.append(
            InterpretationClaim(
                kind="constraint",
                key=constraint,
                strength=round(
                    strength,
                    2,
                ),
                confidence=semantic_confidence,
                source="derived_constraints",
                data={
                    "constraint": constraint,
                },
            )
        )

    # ------------------------------------------------------
    # ПОДДЕРЖКА
    # ------------------------------------------------------

    for support in sorted(
        supports
    ):

        claims.append(
            InterpretationClaim(
                kind="support",
                key=support,
                strength=round(
                    strength,
                    2,
                ),
                confidence=semantic_confidence,
                source="derived_supports",
                data={
                    "support": support,
                },
            )
        )

    # ------------------------------------------------------
    # НАПРЯЖЕНИЯ
    # ------------------------------------------------------

    for tension in sorted(
        tensions
    ):

        claims.append(
            InterpretationClaim(
                kind="tension",
                key=tension,
                strength=round(
                    strength,
                    2,
                ),
                confidence=semantic_confidence,
                source="derived_tensions",
                data={
                    "tension": tension,
                },
            )
        )

    return claims


# ==========================================================
# ФИНАЛЬНАЯ УВЕРЕННОСТЬ
# ==========================================================

def _interpretation_confidence(
    profile,
    claims: list[InterpretationClaim],
) -> float:
    """
    Рассчитывает итоговую уверенность.
    """

    if not claims:
        return 0.0

    strength = float(
        _get_value(
            profile,
            "strength",
            0.0,
        )
    )

    coherence = float(
        _get_value(
            profile,
            "coherence",
            0.0,
        )
    )

    semantic_confidence = float(
        _get_value(
            profile,
            "data",
            {},
        ).get(
            "semantic_confidence",
            0.0,
        )
    )

    claim_confidence = (
        sum(
            claim.confidence
            for claim in claims
        )
        / len(claims)
    )

    structural = (
        (strength / 100.0)
        * 0.30
        + (coherence / 100.0)
        * 0.25
        + semantic_confidence
        * 0.25
        + claim_confidence
        * 0.20
    )

    return round(
        min(
            1.0,
            structural,
        ),
        3,
    )


# ==========================================================
# BUILD INTERPRETATION PROFILE
# ==========================================================

def _build_interpretation_profile(
    profile,
) -> InterpretationProfile:

    domains = _semantic_domains(
        profile
    )

    planets = _semantic_planets(
        profile
    )

    houses = _semantic_houses(
        profile
    )

    claims = _semantic_claims(
        profile
    )

    (
        mechanisms,
        active_dynamics,
        constraints,
        support_set,
    ) = _derive_mechanisms(
        profile,
        claims,
    )

    tension_set = _derive_tensions(
        profile,
        mechanisms,
        constraints,
    )

    support_set = _derive_supports(
        mechanisms,
        support_set,
    )

    interpretation_claims = (
        _build_interpretation_claims(
            profile,
            mechanisms,
            active_dynamics,
            constraints,
            support_set,
            tension_set,
        )
    )

    interpretation_claims = [
        claim
        for claim in interpretation_claims
        if claim.confidence
        >= MIN_INTERPRETATION_CONFIDENCE
    ]

    confidence = _interpretation_confidence(
        profile,
        interpretation_claims,
    )

    return InterpretationProfile(
        theme_key=_get_value(
            profile,
            "theme_key",
            "unknown",
        ),
        strength=float(
            _get_value(
                profile,
                "strength",
                0.0,
            )
        ),
        coherence=float(
            _get_value(
                profile,
                "coherence",
                0.0,
            )
        ),
        confidence=confidence,
        domains=tuple(
            sorted(domains)
        ),
        planets=tuple(
            sorted(planets)
        ),
        houses=tuple(
            sorted(houses)
        ),
        mechanisms=tuple(
            sorted(mechanisms)
        ),
        active_dynamics=tuple(
            sorted(active_dynamics)
        ),
        constraints=tuple(
            sorted(constraints)
        ),
        supports=tuple(
            sorted(support_set)
        ),
        tensions=tuple(
            sorted(tension_set)
        ),
        claims=tuple(
            interpretation_claims
        ),
        data={
            "semantic_confidence": float(
                _get_value(
                    profile,
                    "data",
                    {},
                ).get(
                    "semantic_confidence",
                    0.0,
                )
            ),
            "claim_count": len(
                interpretation_claims
            ),
            "mechanism_count": len(
                mechanisms
            ),
            "constraint_count": len(
                constraints
            ),
            "support_count": len(
                support_set
            ),
            "tension_count": len(
                tension_set
            ),
        },
    )


# ==========================================================
# BUILD REPORT
# ==========================================================

def build_interpretations(
    semantics,
    chart=None,
    themes=None,
    patterns=None,
    relations=None,
    priorities=None,
) -> InterpretationReport:
    """
    Строит InterpretationReport.

    Parameters
    ----------
    semantics:
        SemanticReport или список SemanticProfile.

    chart:
        Chart.
        Пока зарезервирован для дальнейших
        интерпретационных правил.

    themes:
        ThemeReport.
        Зарезервирован для будущего контекстного
        усиления.

    patterns:
        PatternReport.
        Зарезервирован для будущих правил.

    relations:
        RelationReport.
        Зарезервирован для будущих правил.

    priorities:
        PriorityCollection.
        Зарезервирован для будущей калибровки.

    Returns
    -------
    InterpretationReport
    """

    semantic_list = _as_list(
        semantics
    )

    if not semantic_list:
        return InterpretationReport()

    profiles = []

    for semantic_profile in semantic_list:

        profile = (
            _build_interpretation_profile(
                semantic_profile
            )
        )

        if (
            profile.confidence
            < MIN_INTERPRETATION_CONFIDENCE
        ):
            continue

        profiles.append(
            profile
        )

    return InterpretationReport(
        profiles
    )


# ==========================================================
# УДОБНЫЕ ФУНКЦИИ
# ==========================================================

def strongest_interpretations(
    report: InterpretationReport,
    n: int = 5,
) -> list[InterpretationProfile]:
    """
    Возвращает наиболее сильные интерпретации.
    """
    return report.top(n)


def interpretations_for_theme(
    report: InterpretationReport,
    theme_key: str,
) -> list[InterpretationProfile]:
    """
    Возвращает интерпретации определённой темы.
    """
    return report.by_theme(
        theme_key
    )


def interpretations_for_domain(
    report: InterpretationReport,
    domain: str,
) -> list[InterpretationProfile]:
    """
    Возвращает интерпретации определённого домена.
    """
    return report.by_domain(
        domain
    )


def interpretations_for_mechanism(
    report: InterpretationReport,
    mechanism: str,
) -> list[InterpretationProfile]:
    """
    Возвращает интерпретации определённого механизма.
    """
    return report.by_mechanism(
        mechanism
    )
