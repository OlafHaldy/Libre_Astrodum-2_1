"""
Liber Astrodum

core/semantics.py

Semantic Engine v1.0.

Преобразует структурные Themes в машинное
семантическое представление.

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

Semantic Engine НЕ генерирует текст.
Semantic Engine НЕ использует LLM.
Semantic Engine НЕ формирует окончательную трактовку.

Его задача:

    определить смысловые домены,
    роли планет,
    области домов,
    характер процесса,
    напряжения,
    поддержки,
    степень уверенности.

Основной принцип:

    Структура карты сначала превращается
    в набор семантических утверждений.

    Литературная интерпретация появляется
    только на следующем слое.

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

MIN_SEMANTIC_CONFIDENCE = 0.35


# ==========================================================
# СЕМАНТИКА ПЛАНЕТ
# ==========================================================

PLANET_SEMANTICS = {
    "Sun": {
        "primary": {
            "identity",
            "agency",
            "vitality",
            "self_expression",
        },
        "roles": {
            "center",
            "will",
            "visibility",
        },
    },

    "Moon": {
        "primary": {
            "emotion",
            "memory",
            "habit",
            "belonging",
            "response",
        },
        "roles": {
            "emotional",
            "adaptive",
            "subjective",
        },
    },

    "Mercury": {
        "primary": {
            "thought",
            "communication",
            "analysis",
            "learning",
            "information",
        },
        "roles": {
            "mental",
            "communicative",
            "interpretive",
        },
    },

    "Venus": {
        "primary": {
            "relationship",
            "value",
            "attraction",
            "pleasure",
            "harmony",
        },
        "roles": {
            "relational",
            "aesthetic",
            "evaluative",
        },
    },

    "Mars": {
        "primary": {
            "action",
            "conflict",
            "initiative",
            "desire",
            "assertion",
        },
        "roles": {
            "agent",
            "motor",
            "confrontational",
        },
    },

    "Jupiter": {
        "primary": {
            "expansion",
            "meaning",
            "belief",
            "growth",
            "horizon",
        },
        "roles": {
            "expansive",
            "ideological",
            "interpretive",
        },
    },

    "Saturn": {
        "primary": {
            "structure",
            "limitation",
            "responsibility",
            "time",
            "discipline",
            "authority",
        },
        "roles": {
            "structural",
            "regulatory",
            "restrictive",
        },
    },

    "Uranus": {
        "primary": {
            "change",
            "freedom",
            "innovation",
            "disruption",
        },
        "roles": {
            "disruptive",
            "liberating",
            "inventive",
        },
    },

    "Neptune": {
        "primary": {
            "imagination",
            "dissolution",
            "ideal",
            "mystery",
            "empathy",
        },
        "roles": {
            "diffusive",
            "symbolic",
            "idealizing",
        },
    },

    "Pluto": {
        "primary": {
            "transformation",
            "power",
            "depth",
            "crisis",
            "regeneration",
        },
        "roles": {
            "transformative",
            "intensifying",
            "regenerative",
        },
    },
}


# ==========================================================
# СЕМАНТИКА ДОМОВ
# ==========================================================

HOUSE_SEMANTICS = {
    1: {
        "domain": "identity",
        "keywords": {
            "self",
            "body",
            "presence",
            "initiative",
        },
    },

    2: {
        "domain": "resources",
        "keywords": {
            "money",
            "possessions",
            "security",
            "value",
            "self_worth",
        },
    },

    3: {
        "domain": "communication",
        "keywords": {
            "communication",
            "learning",
            "writing",
            "siblings",
            "local_environment",
        },
    },

    4: {
        "domain": "home",
        "keywords": {
            "home",
            "family",
            "roots",
            "origin",
            "private_life",
        },
    },

    5: {
        "domain": "creativity",
        "keywords": {
            "creation",
            "romance",
            "pleasure",
            "children",
            "self_expression",
        },
    },

    6: {
        "domain": "work_health",
        "keywords": {
            "work",
            "routine",
            "service",
            "maintenance",
            "health",
        },
    },

    7: {
        "domain": "partnership",
        "keywords": {
            "relationship",
            "partnership",
            "contracts",
            "others",
            "projection",
        },
    },

    8: {
        "domain": "shared_resources",
        "keywords": {
            "intimacy",
            "shared_resources",
            "dependency",
            "crisis",
            "transformation",
        },
    },

    9: {
        "domain": "meaning",
        "keywords": {
            "meaning",
            "belief",
            "philosophy",
            "higher_learning",
            "travel",
        },
    },

    10: {
        "domain": "career",
        "keywords": {
            "career",
            "status",
            "authority",
            "achievement",
            "public_role",
        },
    },

    11: {
        "domain": "community",
        "keywords": {
            "community",
            "friends",
            "networks",
            "collective",
            "future",
            "social_projects",
        },
    },

    12: {
        "domain": "retreat",
        "keywords": {
            "solitude",
            "hidden",
            "withdrawal",
            "subconscious",
            "sacrifice",
            "closure",
        },
    },
}


# ==========================================================
# СЕМАНТИКА АСПЕКТОВ
# ==========================================================

ASPECT_SEMANTICS = {
    "conjunction": {
        "process": "fusion",
        "keywords": {
            "integration",
            "concentration",
            "fusion",
        },
    },

    "sextile": {
        "process": "opportunity",
        "keywords": {
            "cooperation",
            "opportunity",
            "facilitation",
        },
    },

    "trine": {
        "process": "flow",
        "keywords": {
            "support",
            "fluency",
            "natural_expression",
        },
    },

    "square": {
        "process": "friction",
        "keywords": {
            "conflict",
            "friction",
            "pressure",
        },
    },

    "opposition": {
        "process": "polarization",
        "keywords": {
            "tension",
            "projection",
            "polarization",
            "integration_required",
        },
    },
}


# ==========================================================
# РОЛИ ДОМОВ
# ==========================================================

HOUSE_ROLE_WEIGHTS = {
    1: "identity",
    2: "material",
    3: "mental",
    4: "private",
    5: "creative",
    6: "functional",
    7: "relational",
    8: "transformative",
    9: "philosophical",
    10: "public",
    11: "collective",
    12: "hidden",
}


# ==========================================================
# SEMANTIC CLAIM
# ==========================================================

@dataclass
class SemanticClaim:
    """
    Одно машинное семантическое утверждение.

    kind:
        Тип утверждения.

    key:
        Семантический ключ.

    strength:
        Сила утверждения 0..100.

    confidence:
        Уверенность 0..1.

    source:
        Откуда получено утверждение.

    data:
        Дополнительные данные.
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
            f"<SemanticClaim "
            f"{self.kind}:{self.key} "
            f"{self.strength:.1f}>"
        )


# ==========================================================
# SEMANTIC PROFILE
# ==========================================================

@dataclass
class SemanticProfile:
    """
    Полный семантический профиль одной темы.
    """

    theme_key: str

    strength: float
    coherence: float

    domains: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    planets: tuple[str, ...] = ()
    houses: tuple[int, ...] = ()

    primary_roles: tuple[str, ...] = ()
    secondary_roles: tuple[str, ...] = ()

    processes: tuple[str, ...] = ()

    tensions: tuple[dict, ...] = ()
    supports: tuple[dict, ...] = ()

    claims: tuple[SemanticClaim, ...] = ()

    data: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict:
        return {
            "theme_key": self.theme_key,
            "strength": self.strength,
            "coherence": self.coherence,
            "domains": list(self.domains),
            "keywords": list(self.keywords),
            "planets": list(self.planets),
            "houses": list(self.houses),
            "primary_roles": list(self.primary_roles),
            "secondary_roles": list(self.secondary_roles),
            "processes": list(self.processes),
            "tensions": list(self.tensions),
            "supports": list(self.supports),
            "claims": [
                claim.to_dict()
                for claim in self.claims
            ],
            "data": dict(self.data),
        }

    def __repr__(self) -> str:
        return (
            f"<SemanticProfile "
            f"{self.theme_key} "
            f"domains={self.domains}>"
        )


# ==========================================================
# SEMANTIC REPORT
# ==========================================================

class SemanticReport:
    """
    Коллекция семантических профилей.
    """

    def __init__(
        self,
        profiles: list[SemanticProfile] | None = None,
    ):
        self._profiles = (
            list(profiles)
            if profiles
            else []
        )

        self._profiles.sort(
            key=lambda profile: (
                profile.strength,
                profile.coherence,
            ),
            reverse=True,
        )

    def all(self) -> list[SemanticProfile]:
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
    ) -> list[SemanticProfile]:
        return self._profiles[:n]

    @property
    def strongest(
        self,
    ) -> SemanticProfile | None:
        return (
            self._profiles[0]
            if self._profiles
            else None
        )

    def by_domain(
        self,
        domain: str,
    ) -> list[SemanticProfile]:
        return [
            profile
            for profile in self._profiles
            if domain in profile.domains
        ]

    def by_planet(
        self,
        planet: str,
    ) -> list[SemanticProfile]:
        return [
            profile
            for profile in self._profiles
            if planet in profile.planets
        ]

    def __repr__(self) -> str:
        return (
            f"<SemanticReport "
            f"profiles={len(self._profiles)}>"
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


def _unique(values) -> tuple:
    result = []

    for value in values:
        if value not in result:
            result.append(value)

    return tuple(result)


def _get_theme_value(
    theme,
    name: str,
    default=None,
):
    return getattr(
        theme,
        name,
        default,
    )


def _theme_planets(theme) -> list[str]:
    value = _get_theme_value(
        theme,
        "planets",
        (),
    )

    return [
        planet
        for planet in value
        if isinstance(planet, str)
    ]


def _theme_houses(theme) -> list[int]:
    value = _get_theme_value(
        theme,
        "houses",
        (),
    )

    return [
        house
        for house in value
        if isinstance(house, int)
    ]



def _chart_planet_houses(
    chart,
    planets: list[str],
) -> set[int]:
    """
    Возвращает дома планет из Chart.
    """

    result = set()

    if chart is None:
        return result

    try:
        chart_planets = chart.planets
    except AttributeError:
        return result

    for planet in planets:

        data = chart_planets.get(
            planet,
            {},
        )

        house = data.get("house")

        if isinstance(house, int):
            result.add(house)

    return result


# ==========================================================
# СЕМАНТИКА ПЛАНЕТ
# ==========================================================

def _planet_keywords(
    planets: list[str],
) -> set[str]:
    result = set()

    for planet in planets:

        semantic = PLANET_SEMANTICS.get(
            planet
        )

        if not semantic:
            continue

        result.update(
            semantic.get(
                "primary",
                set(),
            )
        )

    return result


def _planet_roles(
    planets: list[str],
) -> tuple[set[str], set[str]]:
    """
    Возвращает именно роли планет.

    primary:
        семантические функции / роли.

    secondary:
        дополнительные характеристики роли.
    """

    primary = set()
    secondary = set()

    for planet in planets:

        semantic = PLANET_SEMANTICS.get(
            planet
        )

        if not semantic:
            continue

        primary.update(
            semantic.get(
                "roles",
                set(),
            )
        )

        # Primary semantic keywords остаются
        # keywords профиля, а не roles.
        secondary.update(
            semantic.get(
                "primary",
                set(),
            )
        )

    return primary, secondary


# ==========================================================
# СЕМАНТИКА ДОМОВ
# ==========================================================

def _house_domains(
    houses: list[int],
) -> set[str]:
    domains = set()

    for house in houses:

        semantic = HOUSE_SEMANTICS.get(
            house
        )

        if not semantic:
            continue

        domain = semantic.get(
            "domain"
        )

        if domain:
            domains.add(domain)

    return domains


def _house_keywords(
    houses: list[int],
) -> set[str]:
    result = set()

    for house in houses:

        semantic = HOUSE_SEMANTICS.get(
            house
        )

        if not semantic:
            continue

        result.update(
            semantic.get(
                "keywords",
                set(),
            )
        )

    return result


# ==========================================================
# СЕМАНТИКА RELATION PATTERNS
# ==========================================================

def _extract_aspect_processes(
    theme,
) -> tuple[set[str], set[str], set[str]]:
    """
    Возвращает:

        processes
        tension keywords
        support keywords
    """

    processes = set()
    tension_keywords = set()
    support_keywords = set()

    tensions = _get_theme_value(
        theme,
        "tensions",
        (),
    )

    supports = _get_theme_value(
        theme,
        "supports",
        (),
    )

    for tension in tensions:

        aspect = tension.get(
            "aspect",
            tension.get(
                "type",
                "",
            ),
        )

        semantic = ASPECT_SEMANTICS.get(
            aspect
        )

        if not semantic:
            continue

        process = semantic.get(
            "process"
        )

        if process:
            processes.add(process)

        tension_keywords.update(
            semantic.get(
                "keywords",
                set(),
            )
        )

    for support in supports:

        aspect = support.get(
            "aspect",
            support.get(
                "type",
                "",
            ),
        )

        semantic = ASPECT_SEMANTICS.get(
            aspect
        )

        if not semantic:
            continue

        process = semantic.get(
            "process"
        )

        if process:
            processes.add(process)

        support_keywords.update(
            semantic.get(
                "keywords",
                set(),
            )
        )

    return (
        processes,
        tension_keywords,
        support_keywords,
    )


# ==========================================================
# РОЛИ ВНУТРИ ТЕМЫ
# ==========================================================

def _derive_roles(
    planets: list[str],
    houses: list[int],
    tensions: tuple[dict, ...],
    supports: tuple[dict, ...],
) -> tuple[set[str], set[str]]:
    """
    Определяет семантические роли темы.

    Здесь пока только машинная классификация.
    """

    primary = set()
    secondary = set()

    planet_primary, planet_secondary = (
        _planet_roles(planets)
    )

    primary.update(
        planet_primary
    )

    secondary.update(
        planet_secondary
    )

    # Домовые роли.
    for house in houses:

        role = HOUSE_ROLE_WEIGHTS.get(
            house
        )

        if role:
            secondary.add(role)

    # Наличие напряжения.
    if tensions:
        primary.add("conflict")

    # Наличие поддержки.
    if supports:
        primary.add("support")

    # Одновременное наличие обеих сторон.
    if tensions and supports:
        primary.add(
            "conflict_with_support"
        )

    # Сильное присутствие Saturn.
    if "Saturn" in planets:
        secondary.add(
            "structural_pressure"
        )

    # Сильное присутствие Mars.
    if "Mars" in planets:
        secondary.add(
            "agency"
        )

    # Сильное присутствие Mercury.
    if "Mercury" in planets:
        secondary.add(
            "mental_processing"
        )

    # Сильное присутствие Moon.
    if "Moon" in planets:
        secondary.add(
            "emotional_processing"
        )

    # Сильное присутствие Jupiter.
    if "Jupiter" in planets:
        secondary.add(
            "expansion"
        )

    return primary, secondary


# ==========================================================
# ДОПОЛНИТЕЛЬНЫЕ СЕМАНТИЧЕСКИЕ ПРАВИЛА
# ==========================================================

def _derive_structural_claims(
    theme,
    planets: list[str],
    houses: list[int],
    domains: set[str],
    processes: set[str],
) -> list[SemanticClaim]:
    """
    Строит более конкретные машинные утверждения.

    Пока без литературного текста.
    """

    claims = []

    theme_strength = float(
        _get_theme_value(
            theme,
            "strength",
            0.0,
        )
    )

    theme_coherence = float(
        _get_theme_value(
            theme,
            "coherence",
            0.0,
        )
    )

    base_confidence = (
        min(
            theme_strength / 100.0,
            theme_coherence / 100.0,
        )
    )

    # ------------------------------------------------------
    # ПУБЛИЧНОЕ / КОЛЛЕКТИВНОЕ
    # ------------------------------------------------------

    public = 10 in houses
    collective = 11 in houses

    if public:

        claims.append(
            SemanticClaim(
                kind="domain",
                key="public_expression",
                strength=theme_strength,
                confidence=base_confidence,
                source="houses",
                data={
                    "houses": [
                        house
                        for house in houses
                        if house in {10, 11}
                    ],
                },
            )
        )

    if collective:

        claims.append(
            SemanticClaim(
                kind="domain",
                key="collective_context",
                strength=theme_strength,
                confidence=base_confidence,
                source="house_11",
                data={
                    "house": 11,
                },
            )
        )

    # ------------------------------------------------------
    # СКРЫТАЯ / ВНУТРЕННЯЯ ОБЛАСТЬ
    # ------------------------------------------------------

    if 12 in houses:

        claims.append(
            SemanticClaim(
                kind="domain",
                key="hidden_process",
                strength=theme_strength,
                confidence=base_confidence,
                source="house_12",
                data={
                    "house": 12,
                },
            )
        )

    # ------------------------------------------------------
    # СТРУКТУРНОЕ ДАВЛЕНИЕ
    # ------------------------------------------------------

    if "Saturn" in planets:

        claims.append(
            SemanticClaim(
                kind="process",
                key="structural_constraint",
                strength=theme_strength,
                confidence=base_confidence,
                source="Saturn",
                data={
                    "planet": "Saturn",
                },
            )
        )

    # ------------------------------------------------------
    # ДЕЙСТВИЕ
    # ------------------------------------------------------

    if "Mars" in planets:

        claims.append(
            SemanticClaim(
                kind="agency",
                key="active_agency",
                strength=theme_strength,
                confidence=base_confidence,
                source="Mars",
                data={
                    "planet": "Mars",
                },
            )
        )

    # ------------------------------------------------------
    # МЫШЛЕНИЕ
    # ------------------------------------------------------

    if "Mercury" in planets:

        claims.append(
            SemanticClaim(
                kind="cognition",
                key="mental_component",
                strength=theme_strength,
                confidence=base_confidence,
                source="Mercury",
                data={
                    "planet": "Mercury",
                },
            )
        )

    # ------------------------------------------------------
    # ЭМОЦИОНАЛЬНЫЙ КОМПОНЕНТ
    # ------------------------------------------------------

    if "Moon" in planets:

        claims.append(
            SemanticClaim(
                kind="emotion",
                key="emotional_component",
                strength=theme_strength,
                confidence=base_confidence,
                source="Moon",
                data={
                    "planet": "Moon",
                },
            )
        )

    # ------------------------------------------------------
    # РАСШИРЕНИЕ
    # ------------------------------------------------------

    if "Jupiter" in planets:

        claims.append(
            SemanticClaim(
                kind="process",
                key="expansive_component",
                strength=theme_strength,
                confidence=base_confidence,
                source="Jupiter",
                data={
                    "planet": "Jupiter",
                },
            )
        )

    # ------------------------------------------------------
    # ПРОЦЕСС ПОЛЯРИЗАЦИИ
    # ------------------------------------------------------

    if "polarization" in processes:

        claims.append(
            SemanticClaim(
                kind="tension",
                key="polarized_process",
                strength=theme_strength,
                confidence=base_confidence,
                source="aspect",
                data={
                    "process": "polarization",
                },
            )
        )

    # ------------------------------------------------------
    # ПРОЦЕСС ПОТОКА
    # ------------------------------------------------------

    if "flow" in processes:

        claims.append(
            SemanticClaim(
                kind="support",
                key="facilitated_process",
                strength=theme_strength,
                confidence=base_confidence,
                source="aspect",
                data={
                    "process": "flow",
                },
            )
        )

    # ------------------------------------------------------
    # СМЕШЕНИЕ НАПРЯЖЕНИЯ И ПОДДЕРЖКИ
    # ------------------------------------------------------

    if (
        "polarization" in processes
        and "flow" in processes
    ):

        claims.append(
            SemanticClaim(
                kind="structure",
                key="tension_with_internal_support",
                strength=theme_strength,
                confidence=base_confidence,
                source="aspects",
                data={
                    "processes": [
                        "polarization",
                        "flow",
                    ],
                },
            )
        )

    return claims


# ==========================================================
# РАСЧЁТ СЕМАНТИЧЕСКОЙ УВЕРЕННОСТИ
# ==========================================================

def _semantic_confidence(
    theme,
    claims: list[SemanticClaim],
) -> float:
    """
    Общая уверенность семантического профиля.
    """

    strength = float(
        _get_theme_value(
            theme,
            "strength",
            0.0,
        )
    )

    coherence = float(
        _get_theme_value(
            theme,
            "coherence",
            0.0,
        )
    )

    if not claims:
        return 0.0

    base = (
        (strength / 100.0)
        + (coherence / 100.0)
    ) / 2.0

    claim_confidence = sum(
        claim.confidence
        for claim in claims
    ) / len(claims)

    return round(
        min(
            1.0,
            (
                base * 0.55
                + claim_confidence * 0.45
            ),
        ),
        3,
    )


# ==========================================================
# BUILD SEMANTIC PROFILE
# ==========================================================

def _build_semantic_profile(
    theme,
    chart=None,
) -> SemanticProfile:


    planets = _theme_planets(theme)

    theme_houses = _theme_houses(theme)

    chart_houses = _chart_planet_houses(
        chart,
        planets,
    )

    houses = sorted(
        set(theme_houses)
        | set(chart_houses)
    )

    domains = _house_domains(
        houses
    )

    keywords = (
        _house_keywords(houses)
        | _planet_keywords(planets)
    )

    tensions = tuple(
        _get_theme_value(
            theme,
            "tensions",
            (),
        )
    )

    supports = tuple(
        _get_theme_value(
            theme,
            "supports",
            (),
        )
    )

    processes, tension_keywords, support_keywords = (
        _extract_aspect_processes(theme)
    )

    keywords.update(
        tension_keywords
    )

    keywords.update(
        support_keywords
    )

    primary_roles, secondary_roles = (
        _derive_roles(
            planets,
            houses,
            tensions,
            supports,
        )
    )

    claims = _derive_structural_claims(
        theme,
        planets,
        houses,
        domains,
        processes,
    )

    confidence = _semantic_confidence(
        theme,
        claims,
    )

    # ------------------------------------------------------
    # Удаляем слабые утверждения.
    # ------------------------------------------------------

    claims = [
        claim
        for claim in claims
        if claim.confidence
        >= MIN_SEMANTIC_CONFIDENCE
    ]

    return SemanticProfile(
        theme_key=_get_theme_value(
            theme,
            "theme_key",
            "unknown",
        ),
        strength=float(
            _get_theme_value(
                theme,
                "strength",
                0.0,
            )
        ),
        coherence=float(
            _get_theme_value(
                theme,
                "coherence",
                0.0,
            )
        ),
        domains=tuple(
            sorted(domains)
        ),
        keywords=tuple(
            sorted(keywords)
        ),
        planets=tuple(
            sorted(planets)
        ),
        houses=tuple(
            sorted(houses)
        ),
        primary_roles=tuple(
            sorted(primary_roles)
        ),
        secondary_roles=tuple(
            sorted(secondary_roles)
        ),
        processes=tuple(
            sorted(processes)
        ),
        tensions=tensions,
        supports=supports,
        claims=tuple(claims),
        data={
            "semantic_confidence": confidence,
            "keyword_count": len(keywords),
            "domain_count": len(domains),
            "claim_count": len(claims),
        },
    )


# ==========================================================
# BUILD REPORT
# ==========================================================

def build_semantics(
    themes,
    chart=None,
    patterns=None,
    relations=None,
    priorities=None,
) -> SemanticReport:
    """
    Строит SemanticReport.

    Parameters
    ----------
    themes:
        ThemeReport или список ThemeCandidate.

    chart:
        Chart.
        Пока зарезервирован для будущих правил,
        использующих знак, положение и дополнительные
        свойства карты.

    patterns:
        PatternReport.
        Зарезервирован для более глубокого вывода.

    relations:
        RelationReport.
        Зарезервирован для будущего анализа.

    priorities:
        PriorityCollection.
        Зарезервирован для калибровки силы.

    Returns
    -------
    SemanticReport
    """

    theme_list = _as_list(themes)

    if not theme_list:
        return SemanticReport()

    profiles = []

    for theme in theme_list:

        profile = _build_semantic_profile(
        theme,
        chart=chart,
    )

        if profile.data.get(
            "semantic_confidence",
            0.0,
        ) < MIN_SEMANTIC_CONFIDENCE:
            continue

        profiles.append(profile)

    return SemanticReport(
        profiles
    )


# ==========================================================
# УДОБНЫЕ ФУНКЦИИ
# ==========================================================

def strongest_semantics(
    report: SemanticReport,
    n: int = 5,
) -> list[SemanticProfile]:
    return report.top(n)


def semantics_for_domain(
    report: SemanticReport,
    domain: str,
) -> list[SemanticProfile]:
    return report.by_domain(
        domain
    )


def semantics_for_planet(
    report: SemanticReport,
    planet: str,
) -> list[SemanticProfile]:
    return report.by_planet(
        planet
    )