"""
Liber Astrodum

core/evidence.py

Evidence Layer v2.4.

Преобразует:

    Facts
    Priorities
    Relations
    Patterns
    Themes
    Semantics
    Interpretations
    NarrativeBlueprints
    CompositionPlans

в структурированный набор доказательств
для каждого смыслового блока будущего текста.

Evidence Engine НЕ:
    - генерирует литературный текст;
    - использует LLM;
    - интерпретирует карту заново;
    - создаёт новые астрологические факты.

Его задача:

    1. получить готовый CompositionPlan;
    2. определить, какие исходные данные поддерживают
       каждый смысловой блок;
    3. ранжировать доказательства;
    4. убрать дубли;
    5. сохранить происхождение;
    6. передать Prompt Builder компактную
       и машиночитаемую доказательную базу.

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
    Evidence Plan
      ↓
    Prompt Builder
      ↓
    LLM

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum / Astrodum Engine

Версия:
    2.4
"""

from dataclasses import dataclass, field
from typing import Any
import logging
import uuid

# ==========================================================
# LOGGING
# ==========================================================

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# ==========================================================
# КОНСТАНТЫ
# ==========================================================

MIN_EVIDENCE_CONFIDENCE = 0.35
MIN_PRIMARY_EVIDENCE = 3

MAX_EVIDENCE_PER_SECTION = 8
MAX_EVIDENCE_PER_PLAN = 36

SOURCE_WEIGHTS = {
    "fact": 1.00,
    "priority": 0.96,
    "relation": 0.92,
    "pattern": 0.88,
    "theme": 0.84,
    "semantic": 0.82,
    "interpretation": 0.80,
    "narrative": 0.78,
}

PRIMARY_SOURCES = {"fact", "relation"}
SECONDARY_SOURCES = {"priority", "pattern"}
DERIVED_SOURCES = {"theme", "semantic", "interpretation", "narrative"}

SOURCE_NAMES_RU = {
    "fact": "Факт",
    "relation": "Отношение",
    "priority": "Приоритет",
    "pattern": "Паттерн",
    "theme": "Тема",
    "semantic": "Семантика",
    "interpretation": "Интерпретация",
    "narrative": "Нарратив",
}

SECTION_SOURCE_PRIORITY = {
    "opening": (
        "fact",
        "priority",
        "theme",
        "semantic",
        "narrative",
    ),
    "central_theme": (
        "fact",
        "theme",
        "semantic",
        "interpretation",
        "pattern",
        "priority",
    ),
    "mechanism": (
        "relation",
        "fact",
        "pattern",
        "priority",
        "semantic",
    ),
    "manifestation": (
        "fact",
        "semantic",
        "relation",
        "theme",
        "pattern",
    ),
    "tension": (
        "relation",
        "fact",
        "pattern",
        "interpretation",
        "theme",
    ),
    "support": (
        "relation",
        "fact",
        "pattern",
        "theme",
    ),
    "development": (
        "relation",
        "pattern",
        "fact",
        "semantic",
        "priority",
    ),
    "resolution": (
        "relation",
        "fact",
        "interpretation",
        "theme",
        "pattern",
    ),
    "conclusion": (
        "theme",
        "narrative",
        "semantic",
        "interpretation",
    ),
}


# ==========================================================
# DATA MODELS
# ==========================================================

@dataclass(frozen=True)
class EvidenceItem:
    """
    Одно доказательство.

    Поля сознательно соответствуют Prompt Builder v4.0.
    """

    source: str
    evidence_type: str
    subject: str
    target: str

    strength: float
    relevance: float

    reason: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    trace_id: str = ""

    natural_language: str = ""
    interpretation_hint: str = ""
    llm_context: str = ""

    # Backward compatibility
    @property
    def kind(self) -> str:
        return self.evidence_type

    @property
    def key(self) -> str:
        if self.subject and self.target:
            return f"{self.evidence_type}:{self.subject}:{self.target}"
        if self.subject:
            return f"{self.evidence_type}:{self.subject}"
        return self.evidence_type

    @property
    def score(self) -> float:
        return self.relevance * 100.0

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "evidence_type": self.evidence_type,
            "subject": self.subject,
            "target": self.target,
            "strength": self.strength,
            "relevance": self.relevance,
            "reason": self.reason,
            "data": dict(self.data),
            "trace_id": self.trace_id,
            "natural_language": self.natural_language,
            "interpretation_hint": self.interpretation_hint,
            "llm_context": self.llm_context,
            "kind": self.kind,
            "key": self.key,
            "score": self.score,
        }

    def __repr__(self) -> str:
        return (
            f"<EvidenceItem "
            f"{self.source}:{self.evidence_type}:{self.subject} "
            f"relevance={self.relevance:.2f}>"
        )


@dataclass(frozen=True)
class EvidenceSection:
    """
    Доказательная база одного CompositionSection.
    """

    section_type: str
    title: str
    priority: float = 0.0

    evidence: tuple[EvidenceItem, ...] = ()
    confidence: float = 0.0

    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "section_type": self.section_type,
            "title": self.title,
            "priority": self.priority,
            "confidence": self.confidence,
            "evidence": [item.to_dict() for item in self.evidence],
            "data": dict(self.data),
        }

    def get_llm_ready_evidence(self) -> list[dict]:
        """Возвращает доказательства в формате для LLM."""
        result = []
        
        for item in self.evidence:
            if not item.natural_language:
                continue
            
            entry = {
                "text": item.natural_language,
                "importance": item.relevance,
                "source_type": item.source,
                "evidence_type": item.evidence_type,
            }
            
            if item.interpretation_hint:
                entry["hint"] = item.interpretation_hint
            if item.llm_context:
                entry["context"] = item.llm_context
            if item.strength > 0:
                entry["strength"] = item.strength
            
            result.append(entry)
        
        return result

    def __repr__(self) -> str:
        return (
            f"<EvidenceSection "
            f"{self.section_type} "
            f"evidence={len(self.evidence)} "
            f"confidence={self.confidence:.2f}>"
        )


@dataclass(frozen=True)
class EvidencePlan:
    """
    Полная доказательная карта одного CompositionPlan.
    """

    theme_key: str
    strength: float
    confidence: float

    sections: tuple[EvidenceSection, ...] = ()
    total_evidence: int = 0
    primary_evidence: int = 0
    unique_sources: tuple[str, ...] = ()

    data: dict[str, Any] = field(default_factory=dict)

    @property
    def all_evidence(self) -> list[EvidenceItem]:
        return [
            item
            for section in self.sections
            for item in section.evidence
        ]

    @property
    def primary_ratio(self) -> float:
        if not self.total_evidence:
            return 0.0
        return self.primary_evidence / self.total_evidence

    def to_dict(self) -> dict:
        return {
            "theme_key": self.theme_key,
            "strength": self.strength,
            "confidence": self.confidence,
            "sections": [section.to_dict() for section in self.sections],
            "total_evidence": self.total_evidence,
            "primary_evidence": self.primary_evidence,
            "primary_ratio": round(self.primary_ratio, 3),
            "unique_sources": list(self.unique_sources),
            "data": dict(self.data),
        }

    def get_llm_ready_plan(self) -> dict:
        """Возвращает план в формате для LLM."""
        return {
            "theme": self.theme_key,
            "strength": self.strength,
            "confidence": self.confidence,
            "sections": [
                {
                    "type": section.section_type,
                    "title": section.title,
                    "priority": section.priority,
                    "evidence": section.get_llm_ready_evidence(),
                }
                for section in self.sections
            ]
        }

    def __repr__(self) -> str:
        return (
            f"<EvidencePlan "
            f"{self.theme_key} "
            f"sections={len(self.sections)} "
            f"evidence={self.total_evidence} "
            f"primary={self.primary_evidence} "
            f"confidence={self.confidence:.2f}>"
        )


class EvidenceReport:
    """Коллекция EvidencePlan."""

    def __init__(self, plans: list[EvidencePlan] | None = None):
        self._plans = list(plans) if plans else []
        self._plans.sort(
            key=lambda plan: (plan.strength, plan.confidence),
            reverse=True,
        )

    def all(self) -> list[EvidencePlan]:
        return list(self._plans)

    def to_list(self) -> list[dict]:
        return [plan.to_dict() for plan in self._plans]

    def top(self, n: int = 5) -> list[EvidencePlan]:
        return self._plans[:n]

    def by_theme(self, theme_key: str) -> list[EvidencePlan]:
        return [plan for plan in self._plans if plan.theme_key == theme_key]

    @property
    def strongest(self) -> EvidencePlan | None:
        return self._plans[0] if self._plans else None

    def get_llm_payload(self, max_themes: int = 3) -> dict:
        """Создаёт готовый payload для LLM."""
        plans = self.top(max_themes)
        return {
            "themes": [plan.get_llm_ready_plan() for plan in plans],
            "metadata": {
                "total_themes": len(plans),
                "strongest_theme": plans[0].theme_key if plans else None,
                "average_confidence": sum(
                    plan.confidence for plan in plans
                ) / len(plans) if plans else 0,
            }
        }

    def __len__(self) -> int:
        return len(self._plans)

    def __iter__(self):
        return iter(self._plans)

    def __getitem__(self, index):
        return self._plans[index]

    def __repr__(self) -> str:
        return f"<EvidenceReport plans={len(self._plans)}>"


# ==========================================================
# HELPERS
# ==========================================================

def _as_list(collection) -> list:
    if collection is None:
        return []
    if hasattr(collection, "all"):
        return collection.all()
    return list(collection)


def _get(item, name: str, default=None):
    if item is None:
        return default
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _data(item) -> dict[str, Any]:
    value = _get(item, "data", {})
    return value if isinstance(value, dict) else {}


def _tuple_strings(value) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(sorted({
        item for item in value
        if isinstance(item, str) and item
    }))


def _tuple_ints(value) -> tuple[int, ...]:
    if not value:
        return ()
    return tuple(sorted({
        item for item in value
        if isinstance(item, int)
    }))


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return round(max(low, min(high, value)), 3)


def _confidence(item, default: float = 0.5) -> float:
    value = _get(item, "confidence", None)
    if value is None:
        value = _data(item).get("confidence", default)
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = default
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))


def _strength(item, default: float = 0.0) -> float:
    value = _get(item, "strength", None)
    if value is None:
        value = _get(item, "importance", None)
    if value is None:
        data = _data(item)
        value = data.get("strength", data.get("importance", default))
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ==========================================================
# TOKEN EXTRACTION
# ==========================================================

def _text_tokens(value) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        normalized = value.replace(":", "_").replace("-", "_").replace(".", "_").lower()
        return {token for token in normalized.split("_") if token}
    if isinstance(value, (list, tuple, set)):
        result = set()
        for item in value:
            result.update(_text_tokens(item))
        return result
    if isinstance(value, dict):
        result = set()
        for key, item in value.items():
            result.update(_text_tokens(key))
            result.update(_text_tokens(item))
        return result
    return set()


def _metadata_tokens(blueprint, section, plan) -> set[str]:
    tokens = set()
    for field_name in (
        "theme_key", "core_theme", "dominant_process",
        "domains", "planets", "houses", "tensions",
        "supports", "resolution", "central_claims",
        "mechanisms", "manifestations", "dynamics",
    ):
        tokens.update(_text_tokens(_get(blueprint, field_name, ())))
    tokens.update(_text_tokens(_get(section, "section_type", "")))
    tokens.update(_text_tokens(_get(section, "sources", ())))
    tokens.update(_text_tokens(_get(plan, "theme_key", "")))
    return tokens


def _source_tokens(source: str, item) -> set[str]:
    tokens = set()
    for field_name in (
        "type", "kind", "theme_key", "theme_hint", "object",
        "source", "target", "planet", "house", "houses",
        "planets", "domains", "keywords", "mechanisms",
        "tensions", "supports", "resolution", "pattern_types",
        "claims", "importance_reasons", "confidence_reasons",
    ):
        tokens.update(_text_tokens(_get(item, field_name, None)))
    tokens.update(_text_tokens(_data(item)))
    tokens.add(source)
    return tokens


# ==========================================================
# SUBJECT / TARGET
# ==========================================================

def _first_string(*values, default="") -> str:
    for value in values:
        if isinstance(value, str) and value:
            return value
        if isinstance(value, (int, float)):
            return str(value)
    return default


def _extract_subject(source: str, item) -> str:
    if source == "fact":
        return _first_string(
            _get(item, "object", None),
            _get(item, "planet", None),
            _get(item, "theme_key", None),
            default="unknown",
        )
    if source == "priority":
        return _first_string(
            _get(item, "object", None),
            _get(item, "planet", None),
            _get(item, "theme_key", None),
            default="unknown",
        )
    if source == "relation":
        return _first_string(
            _get(item, "source", None),
            _get(item, "planet1", None),
            _get(item, "object", None),
            default="unknown",
        )
    if source == "pattern":
        return _first_string(
            _get(item, "planet", None),
            _get(item, "theme_hint", None),
            _get(item, "theme_key", None),
            default="unknown",
        )
    if source in {"theme", "semantic", "interpretation", "narrative"}:
        return _first_string(
            _get(item, "theme_key", None),
            _get(item, "core_theme", None),
            default="unknown",
        )
    return "unknown"


def _extract_target(source: str, item) -> str:
    if source == "relation":
        return _first_string(
            _get(item, "target", None),
            _get(item, "planet2", None),
            default="",
        )
    if source == "fact":
        data = _data(item)
        return _first_string(
            _get(item, "sign", None),
            _get(item, "house", None),
            data.get("sign", None),
            data.get("house", None),
            default="",
        )
    if source == "priority":
        data = _data(item)
        return _first_string(
            data.get("house", None),
            data.get("sign", None),
            default="",
        )
    if source == "pattern":
        data = _data(item)
        return _first_string(
            data.get("house", None),
            data.get("houses", None),
            default="",
        )
    return ""


def _extract_evidence_type(source: str, item, section) -> str:
    value = _first_string(
        _get(item, "evidence_type", None),
        _get(item, "type", None),
        _get(item, "kind", None),
        default="",
    )
    if value:
        return value
    return str(_get(section, "section_type", "evidence"))


# ==========================================================
# PLANET RELEVANCE
# ==========================================================

PLANET_MECHANISM_MAP = {
    "Mercury": {"mental_component", "analysis", "communication", "thought", "learning", "information"},
    "Moon": {"emotional_component", "emotional_processing", "memory", "habit", "response", "subconscious"},
    "Saturn": {"structural_constraint", "restriction", "discipline", "structure", "limitation", "responsibility", "authority"},
    "Mars": {"active_agency", "action", "conflict", "initiative", "assertion", "drive"},
    "Jupiter": {"expansive_component", "expansion", "growth", "belief", "meaning", "opportunity"},
    "Venus": {"harmony", "value", "relationship", "attraction", "pleasure", "aesthetic"},
    "Sun": {"identity", "vitality", "will", "self_expression", "purpose", "visibility"},
}

PLANET_TENSION_MAP = {
    "Saturn": {"restriction", "structural_constraint", "limitation"},
    "Jupiter": {"expansion", "expansive_component", "expansion_vs_limitation"},
    "Mars": {"conflict", "action_vs_constraint"},
    "Mercury": {"thought_vs_response", "mental_component"},
    "Moon": {"inner_conflict", "emotional_component"},
}

PLANET_SUPPORT_MAP = {
    "Venus": {"harmony", "harmonious_flow", "natural_flow"},
    "Jupiter": {"growth", "expansion", "facilitated_development"},
    "Mercury": {"clear_execution", "facilitated_development", "effective_action"},
    "Mars": {"effective_action", "direct_action", "clear_execution"},
    "Saturn": {"structured_support", "supportive_structure"},
}


def _is_planet_relevant_to_blueprint(item_planet: str, blueprint) -> bool:
    if not item_planet:
        return False
    item_planet = str(item_planet).strip()
    
    blueprint_planets = set(_tuple_strings(_get(blueprint, "planets", ())))
    if item_planet in blueprint_planets:
        return True
    
    mechanisms = set(_get(blueprint, "mechanisms", ())) or set()
    blueprint_data = _get(blueprint, "data", {}) or {}
    if isinstance(blueprint_data, dict):
        mechanisms.update(blueprint_data.get("mechanisms", ()) or set())
    
    planet_mechanisms = PLANET_MECHANISM_MAP.get(item_planet, set())
    if planet_mechanisms & mechanisms:
        return True
    
    tensions = set(_get(blueprint, "tensions", ())) or set()
    planet_tensions = PLANET_TENSION_MAP.get(item_planet, set())
    if planet_tensions & tensions:
        return True
    
    supports = set(_get(blueprint, "supports", ())) or set()
    planet_supports = PLANET_SUPPORT_MAP.get(item_planet, set())
    if planet_supports & supports:
        return True
    
    dominant_process = _get(blueprint, "dominant_process", "")
    if dominant_process:
        process_planets = {
            "friction": {"Saturn", "Mars"},
            "flow": {"Jupiter", "Venus", "Mercury"},
            "polarization": {"Jupiter", "Saturn"},
            "agency": {"Mars", "Sun"},
            "processing": {"Mercury", "Moon"},
            "structural_constraint": {"Saturn"},
        }
        if item_planet in process_planets.get(dominant_process, set()):
            return True
    
    return False


def _extract_item_planets(item) -> set[str]:
    planets = set()
    
    for field in ("planet", "planet1", "planet2", "object"):
        value = _get(item, field, None)
        if value and isinstance(value, str) and value in PLANET_MECHANISM_MAP:
            planets.add(value)
    
    data = _data(item)
    for field in ("planet", "planet1", "planet2", "object"):
        value = data.get(field)
        if value and isinstance(value, str) and value in PLANET_MECHANISM_MAP:
            planets.add(value)
    
    subject = _get(item, "source", None)
    if subject and isinstance(subject, str) and subject in PLANET_MECHANISM_MAP:
        planets.add(subject)
    
    target = _get(item, "target", None)
    if target and isinstance(target, str) and target in PLANET_MECHANISM_MAP:
        planets.add(target)
    
    return planets


# ==========================================================
# RELEVANCE
# ==========================================================

def _relevance_score(
    source: str,
    item,
    blueprint,
    section,
    plan,
) -> tuple[float, str]:

    base = SOURCE_WEIGHTS.get(source, 0.5) * 35.0
    reasons = []

    # 1. PRIMARY SOURCES
    if source in PRIMARY_SOURCES:
        base += 8.0
        reasons.append("primary_source_bonus")

    # 2. KEY PLANETS
    item_planets = _extract_item_planets(item)
    blueprint_planets = set(_tuple_strings(_get(blueprint, "planets", ())))
    
    relevant_planets = set()
    irrelevant_planets = set()
    
    for planet in item_planets:
        if _is_planet_relevant_to_blueprint(planet, blueprint):
            relevant_planets.add(planet)
        else:
            irrelevant_planets.add(planet)
    
    if relevant_planets:
        base += 15.0
        reasons.append(f"key_planet:{','.join(sorted(relevant_planets))}")
    elif irrelevant_planets:
        base -= 25.0
        reasons.append(f"non_key_planet:{','.join(sorted(irrelevant_planets))}")
        if source in PRIMARY_SOURCES:
            base -= 10.0
            reasons.append("primary_non_key_penalty")
    
    if blueprint_planets and source in PRIMARY_SOURCES:
        if not (item_planets & blueprint_planets):
            base -= 15.0
            reasons.append("no_blueprint_planet_match")

    # 3. CONTEXT OVERLAP
    blueprint_tokens = _metadata_tokens(blueprint, section, plan)
    item_tokens = _source_tokens(source, item)
    overlap = blueprint_tokens & item_tokens

    if overlap:
        if irrelevant_planets and not relevant_planets:
            overlap_score = min(10.0, len(overlap) * 1.5)
        else:
            overlap_score = min(20.0, len(overlap) * 2.5)
        base += overlap_score
        reasons.append("context_overlap:" + ",".join(sorted(overlap)[:6]))

    # 4. SECTION SOURCE PRIORITY
    section_type = _get(section, "section_type", "")
    source_order = SECTION_SOURCE_PRIORITY.get(section_type, ())

    if source in source_order:
        position = source_order.index(source)
        base += max(0.0, 10.0 - position * 1.5)
        reasons.append("section_source_priority")

    # 5. SECTION-SPECIFIC CHECKS
    if section_type == "mechanism":
        item_type = _get(item, "type", None) or _get(item, "kind", None)
        if item_type in {"aspect", "dispositor", "house_rulership", "ruler_strength"}:
            if relevant_planets:
                base += 15.0
                reasons.append("mechanism_relation")
            else:
                base += 5.0
                reasons.append("mechanism_relation_weak")
        
        item_house = _get(item, "house", None)
        blueprint_houses = set(_tuple_ints(_get(blueprint, "houses", ())))
        if item_house and item_house in blueprint_houses:
            base += 8.0
            reasons.append("mechanism_house")

    elif section_type == "tension":
        item_type = _get(item, "type", None) or _get(item, "kind", None)
        aspect_type = _get(item, "aspect_type", None) or _get(item, "aspect", None)
        if item_type == "aspect" or aspect_type:
            if aspect_type in {"opposition", "square"}:
                if relevant_planets:
                    base += 20.0
                    reasons.append("tension_aspect")
                else:
                    base += 8.0
                    reasons.append("tension_aspect_weak")
            else:
                base += 5.0
                reasons.append("tension_relation")

    elif section_type == "support":
        item_type = _get(item, "type", None) or _get(item, "kind", None)
        aspect_type = _get(item, "aspect_type", None) or _get(item, "aspect", None)
        if item_type == "aspect" or aspect_type:
            if aspect_type in {"trine", "sextile", "conjunction"}:
                if relevant_planets:
                    base += 20.0
                    reasons.append("support_aspect")
                else:
                    base += 8.0
                    reasons.append("support_aspect_weak")
            else:
                base += 5.0
                reasons.append("support_relation")

    # 6. SOURCE STRENGTH
    source_strength = _strength(item, 0.0)
    if source_strength:
        strength_bonus = min(12.0, max(0.0, source_strength) * 0.12)
        if irrelevant_planets and not relevant_planets:
            strength_bonus *= 0.25
        base += strength_bonus
        reasons.append("source_strength")

    # 7. CONFIDENCE
    confidence = _confidence(item, 0.5)
    base += confidence * 8.0
    reasons.append("source_confidence")

    # 8. ADDITIONAL SIGNALS
    if _get(item, "importance_reasons", None):
        base += 4.0
        reasons.append("importance_reasons")

    if _get(item, "theme_hint", None):
        base += 2.0
        reasons.append("theme_hint")

    return (_clamp(base), ";".join(reasons))


# ==========================================================
# NATURAL LANGUAGE GENERATION
# ==========================================================

def _generate_natural_language(
    source: str,
    item,
    evidence_type: str,
    subject: str,
    target: str,
) -> str:
    if source == "fact":
        return _natural_fact(item, evidence_type, subject, target)
    elif source == "relation":
        return _natural_relation(item, evidence_type, subject, target)
    elif source == "priority":
        return _natural_priority(item, evidence_type, subject)
    elif source == "pattern":
        return _natural_pattern(item, evidence_type, subject)
    elif source == "theme":
        return f"Тема: {subject}"
    elif source == "semantic":
        return _natural_semantic(item, subject)
    elif source == "interpretation":
        return _natural_interpretation(item, subject)
    elif source == "narrative":
        return f"Нарратив: {subject}"
    return f"{evidence_type}: {subject}"


def _natural_fact(item, evidence_type: str, subject: str, target: str) -> str:
    if evidence_type == "planet_position":
        sign = _get(item, "sign", "")
        house = _get(item, "house", "")
        retrograde = _get(item, "retrograde", False)
        retro_text = " (ретроградный)" if retrograde else ""
        return f"{subject} находится в знаке {sign} в {house} доме{retro_text}"
    elif evidence_type == "planet_sign":
        sign = _get(item, "sign", "")
        return f"{subject} в знаке {sign}"
    elif evidence_type == "house_position":
        sign = _get(item, "sign", "")
        return f"Куспид {subject} в знаке {sign}"
    elif evidence_type == "house_ruler":
        house = _get(item, "house", "")
        ruler = _get(item, "ruler", subject)
        ruler_sign = _get(item, "ruler_sign", "")
        ruler_house = _get(item, "ruler_house", "")
        return f"{ruler} управляет {house} домом, находясь в {ruler_sign} в {ruler_house} доме"
    elif evidence_type == "ruler_strength":
        planet = _get(item, "planet", subject)
        data = _data(item)
        essential_score = data.get("essential_score", "")
        if essential_score:
            return f"Эссенциальная сила планеты {planet}: {essential_score} баллов"
        return f"Эссенциальная сила планеты {planet}"
    elif evidence_type == "dispositor":
        dispositor = _get(item, "dispositor", "")
        return f"Диспозитор {subject}: {dispositor}"
    return f"{subject} {target}".strip()


def _natural_relation(item, evidence_type: str, subject: str, target: str) -> str:
    if evidence_type == "house_rulership":
        house = _get(item, "house", target)
        return f"{subject} управляет {house} домом"
    elif evidence_type == "aspect":
        aspect_type = _get(item, "type", "")
        planet1 = _get(item, "planet1", subject)
        planet2 = _get(item, "planet2", target)
        return f"Аспект {aspect_type} между {planet1} и {planet2}"
    elif evidence_type == "dispositor":
        dispositor = _get(item, "dispositor", target)
        return f"{subject} в диспозиции {dispositor}"
    elif evidence_type == "planet_house":
        house = _get(item, "house", target)
        return f"{subject} в {house} доме"
    elif evidence_type == "planet_sign":
        sign = _get(item, "sign", target)
        return f"{subject} в знаке {sign}"
    elif evidence_type == "planet_dignity":
        return f"Достоинство планеты {subject}"
    return f"{subject} → {target}"


def _natural_priority(item, evidence_type: str, subject: str) -> str:
    if evidence_type == "house_ruler":
        house = _get(item, "house", "")
        return f"{subject} как управитель {house} дома"
    elif evidence_type == "ruler_strength":
        return f"Сила планеты {subject}"
    elif evidence_type == "planet_position":
        house = _get(item, "house", "")
        return f"{subject} в {house} доме"
    return f"Приоритет: {subject}"


def _natural_pattern(item, evidence_type: str, subject: str) -> str:
    if evidence_type == "planet_cluster":
        house = _get(item, "house", "")
        planets = _get(item, "planets", [])
        return f"Скопление планет {', '.join(map(str, planets))} в {house} доме"
    elif evidence_type == "dispositor_chain":
        chain = _get(item, "chain", [])
        return f"Цепочка диспозиторов: {' → '.join(map(str, chain))}"
    elif evidence_type == "multiple_rulership":
        houses = _get(item, "houses", [])
        if houses:
            return f"{subject} управляет несколькими домами: {', '.join(map(str, houses))}"
        return f"{subject} управляет несколькими домами"
    elif evidence_type == "planet_focus":
        relation_count = _get(item, "relation_count", 0)
        if relation_count:
            return f"{subject} имеет {relation_count} связей с другими планетами"
        return f"Фокус на планете {subject}"
    elif evidence_type == "dignity_reinforcement":
        return f"Усиление достоинства планеты {subject}"
    return f"Паттерн: {subject}"


def _natural_semantic(item, subject: str) -> str:
    domains = _get(item, "domains", [])
    keywords = _get(item, "keywords", [])
    if domains:
        return f"Семантические домены: {', '.join(map(str, domains))}"
    elif keywords:
        return f"Ключевые слова: {', '.join(map(str, keywords[:5]))}"
    return f"Семантика: {subject}"


def _natural_interpretation(item, subject: str) -> str:
    claims = _get(item, "claims", [])
    if claims:
        claim_texts = []
        for claim in claims[:3]:
            if isinstance(claim, str):
                claim_texts.append(claim)
            else:
                claim_key = _get(claim, "key", str(claim))
                claim_kind = _get(claim, "kind", "")
                if claim_kind and claim_key:
                    claim_texts.append(f"{claim_kind}:{claim_key}")
                else:
                    claim_texts.append(str(claim_key))
        if claim_texts:
            return f"Интерпретация: {', '.join(claim_texts)}"
    return f"Интерпретация: {subject}"


def _generate_interpretation_hint(
    source: str,
    item,
    section_type: str,
    subject: str,
    target: str,
) -> str:
    hints = []
    
    if section_type == "opening":
        hints.append("Введение в тему")
    elif section_type == "central_theme":
        hints.append("Центральная тема")
    elif section_type == "mechanism":
        if source == "relation":
            hints.append("Показывает структурную связь")
        elif source == "fact":
            hints.append("Базовый факт механизма")
        hints.append("Как это работает")
    elif section_type == "manifestation":
        hints.append("Где проявляется")
    elif section_type == "tension":
        if source == "relation":
            aspect_type = _get(item, "type", "")
            if aspect_type in {"opposition", "square"}:
                hints.append("Создаёт напряжение")
            elif aspect_type in {"trine", "sextile"}:
                hints.append("Смягчает напряжение")
        hints.append("Противоречие")
    elif section_type == "support":
        hints.append("Поддерживающий фактор")
    elif section_type == "development":
        hints.append("Развитие темы")
    elif section_type == "resolution":
        hints.append("Направление интеграции")
    elif section_type == "conclusion":
        hints.append("Итоговый вывод")
    
    if source == "fact":
        if "ruler" in str(_get(item, "type", "")):
            hints.append("Ключевая планета")
        if "dispositor" in str(_get(item, "type", "")):
            hints.append("Цепочка управления")
    elif source == "pattern":
        if "cluster" in str(_get(item, "type", "")):
            hints.append("Концентрация энергии")
        elif "chain" in str(_get(item, "type", "")):
            hints.append("Структурная последовательность")
    elif source == "theme":
        hints.append("Смысловой центр")
    elif source == "semantic":
        hints.append("Область значений")
    elif source == "interpretation":
        hints.append("Структурный вывод")
    elif source == "narrative":
        hints.append("Нарративная структура")
    
    return "; ".join(dict.fromkeys(hints))


def _generate_llm_context(
    blueprint,
    section,
    item,
    source: str,
) -> str:
    context_parts = []
    
    theme = _get(blueprint, "core_theme", "")
    if theme:
        context_parts.append(f"Тема: {theme}")
    
    process = _get(blueprint, "dominant_process", "")
    if process:
        context_parts.append(f"Процесс: {process}")
    
    section_type = _get(section, "section_type", "")
    if section_type:
        context_parts.append(f"Раздел: {section_type}")
    
    context_parts.append(f"Источник: {SOURCE_NAMES_RU.get(source, source)}")
    
    return " | ".join(context_parts)


# ==========================================================
# ITEM CREATION
# ==========================================================

def _build_payload(item) -> dict[str, Any]:
    payload = {}
    if isinstance(item, dict):
        payload.update(item)
    else:
        payload.update(_data(item))
        for field_name in (
            "type", "kind", "object", "theme_key", "theme_hint",
            "source", "target", "planet", "planet1", "planet2",
            "house", "houses", "planets", "sign",
            "importance", "importance_reasons", "confidence",
            "confidence_reasons", "strength", "domains", "keywords",
            "mechanisms", "tensions", "supports", "resolution",
            "pattern_types", "claims",
        ):
            value = _get(item, field_name, None)
            if value is not None:
                payload[field_name] = value
    return payload


def _make_evidence_item(
    source: str,
    item,
    index: int,
    blueprint,
    section,
    plan,
) -> EvidenceItem:
    score, reason = _relevance_score(source, item, blueprint, section, plan)
    evidence_type = _extract_evidence_type(source, item, section)
    subject = _extract_subject(source, item)
    target = _extract_target(source, item)
    source_strength = _strength(item, 0.0)
    relevance = round(score / 100.0, 3)
    
    natural_language = _generate_natural_language(
        source, item, evidence_type, subject, target
    )
    
    section_type = _get(section, "section_type", "")
    interpretation_hint = _generate_interpretation_hint(
        source, item, section_type, subject, target
    )
    
    llm_context = _generate_llm_context(blueprint, section, item, source)
    
    return EvidenceItem(
        source=source,
        evidence_type=evidence_type,
        subject=subject,
        target=target,
        strength=round(source_strength, 3),
        relevance=relevance,
        reason=reason,
        data=_build_payload(item),
        trace_id=str(uuid.uuid4()),
        natural_language=natural_language,
        interpretation_hint=interpretation_hint,
        llm_context=llm_context,
    )


# ==========================================================
# DEDUPLICATION
# ==========================================================

def _deduplicate(items: list[EvidenceItem]) -> list[EvidenceItem]:
    best: dict[tuple[str, str, str, str], EvidenceItem] = {}
    for item in items:
        key = (item.source, item.evidence_type, item.subject, item.target)
        previous = best.get(key)
        if previous is None or item.relevance > previous.relevance:
            best[key] = item
    return sorted(
        best.values(),
        key=lambda item: (item.relevance, item.strength),
        reverse=True,
    )


# ==========================================================
# DIVERSITY LIMIT
# ==========================================================

def _avoid_overcrowding(items: list[EvidenceItem], limit: int) -> list[EvidenceItem]:
    if len(items) <= limit:
        return items
    
    source_groups = {}
    for item in items:
        if item.source not in source_groups:
            source_groups[item.source] = []
        source_groups[item.source].append(item)
    
    selected = []
    sources_order = [
        "fact", "relation", "priority", "pattern",
        "theme", "semantic", "interpretation", "narrative",
    ]
    source_limits = {
        "fact": 3, "relation": 3, "priority": 2, "pattern": 2,
        "theme": 2, "semantic": 2, "interpretation": 2, "narrative": 2,
    }
    
    while len(selected) < limit:
        added = False
        for source in sources_order:
            if source not in source_groups:
                continue
            source_count = sum(1 for item in selected if item.source == source)
            if source_count >= source_limits.get(source, 2):
                continue
            for item in source_groups[source]:
                if item not in selected:
                    selected.append(item)
                    added = True
                    break
            if len(selected) >= limit:
                break
        if not added:
            for item in items:
                if item not in selected:
                    selected.append(item)
                    break
        if len(selected) >= limit:
            break
    
    return selected


# ==========================================================
# SECTION BUILD
# ==========================================================

def _build_section_evidence(
    blueprint,
    plan,
    section,
    sources: dict[str, list[Any]],
) -> EvidenceSection:
    candidates = []
    requested_sources = tuple(_get(section, "sources", ()) or ())
    preferred_sources = []
    
    for source in requested_sources:
        if source in sources and source not in preferred_sources:
            preferred_sources.append(source)
    
    section_type = _get(section, "section_type", "")
    for source in SECTION_SOURCE_PRIORITY.get(section_type, ()):
        if source in sources and source not in preferred_sources:
            preferred_sources.append(source)
    
    all_source_types = list(PRIMARY_SOURCES) + list(SECONDARY_SOURCES) + list(DERIVED_SOURCES)
    for source in all_source_types:
        if source in sources and source not in preferred_sources:
            preferred_sources.append(source)
    
    if not preferred_sources:
        preferred_sources = [source for source in sources]
    
    for source in preferred_sources:
        for index, item in enumerate(sources[source]):
            candidates.append(
                _make_evidence_item(
                    source=source, item=item, index=index,
                    blueprint=blueprint, section=section, plan=plan,
                )
            )
    
    candidates = _deduplicate(candidates)
    candidates = _avoid_overcrowding(candidates, MAX_EVIDENCE_PER_SECTION)
    
    confidence_values = [_confidence(item, 0.5) for item in candidates]
    confidence = (
        sum(confidence_values) / len(confidence_values)
        if confidence_values else 0.0
    )
    
    section_priority = _safe_float(_get(section, "priority", 0.0))
    
    return EvidenceSection(
        section_type=section_type or "unknown",
        title=_get(section, "title", ""),
        priority=section_priority,
        evidence=tuple(candidates),
        confidence=round(confidence, 3),
        data={
            "requested_sources": list(requested_sources),
            "selected_sources": list(preferred_sources),
            "evidence_count": len(candidates),
            "primary_count": sum(1 for item in candidates if item.source in PRIMARY_SOURCES),
            "source_distribution": {
                source: sum(1 for item in candidates if item.source == source)
                for source in set(item.source for item in candidates)
            },
        },
    )


# ==========================================================
# PLAN LEVEL LIMIT
# ==========================================================

def _limit_plan_evidence(
    sections: list[EvidenceSection],
    limit: int,
) -> list[EvidenceSection]:
    total = sum(len(section.evidence) for section in sections)
    if total <= limit:
        return sections
    
    selected_by_section = {}
    selected_count = 0
    
    for index, section in enumerate(sections):
        if not section.evidence:
            selected_by_section[index] = []
            continue
        strongest = section.evidence[0]
        selected_by_section[index] = [strongest]
        selected_count += 1
    
    primary_items = [
        item
        for section in sections
        for item in section.evidence
        if item.source in PRIMARY_SOURCES
        and item not in [
            selected
            for items in selected_by_section.values()
            for selected in items
        ]
    ]
    
    for primary_item in primary_items[:MIN_PRIMARY_EVIDENCE]:
        for index, section in enumerate(sections):
            if primary_item in section.evidence:
                selected_by_section[index].append(primary_item)
                selected_count += 1
                break
    
    pool = []
    for index, section in enumerate(sections):
        for item in section.evidence:
            if item not in selected_by_section[index]:
                pool.append((item.relevance, item.strength, index, item))
    pool.sort(key=lambda value: (value[0], value[1]), reverse=True)
    
    remaining = max(0, limit - selected_count)
    for relevance, strength, index, item in pool[:remaining]:
        selected_by_section[index].append(item)
    
    result = []
    for index, section in enumerate(sections):
        selected = selected_by_section.get(index, [])
        selected.sort(key=lambda item: (item.relevance, item.strength), reverse=True)
        result.append(
            EvidenceSection(
                section_type=section.section_type,
                title=section.title,
                priority=section.priority,
                evidence=tuple(selected),
                confidence=(
                    round(sum(item.relevance for item in selected) / len(selected), 3)
                    if selected else 0.0
                ),
                data={
                    **section.data,
                    "evidence_count": len(selected),
                    "primary_count": sum(1 for item in selected if item.source in PRIMARY_SOURCES),
                },
            )
        )
    
    return result


# ==========================================================
# PLAN BUILD
# ==========================================================

def _calculate_plan_confidence(
    blueprint,
    sections: list[EvidenceSection],
) -> float:
    blueprint_confidence = _confidence(blueprint, 0.0)
    section_confidences = [
        section.confidence
        for section in sections
        if section.evidence
    ]
    evidence_confidence = (
        sum(section_confidences) / len(section_confidences)
        if section_confidences else 0.0
    )
    confidence = blueprint_confidence * 0.60 + evidence_confidence * 0.40
    return round(min(1.0, confidence), 3)


def _build_evidence_plan(
    composition,
    sources: dict[str, list[Any]],
) -> EvidencePlan:
    raw_sections = _get(composition, "sections", ()) or ()
    sections = []
    
    for section in raw_sections:
        sections.append(
            _build_section_evidence(
                blueprint=composition,
                plan=composition,
                section=section,
                sources=sources,
            )
        )
    
    sections = _limit_plan_evidence(sections, MAX_EVIDENCE_PER_PLAN)
    confidence = _calculate_plan_confidence(composition, sections)
    
    all_items = [
        item
        for section in sections
        for item in section.evidence
    ]
    
    primary_count = sum(1 for item in all_items if item.source in PRIMARY_SOURCES)
    unique_sources = tuple(sorted({item.source for item in all_items}))
    unique_types = tuple(sorted({item.evidence_type for item in all_items}))
    
    return EvidencePlan(
        theme_key=_get(composition, "theme_key", "unknown"),
        strength=float(_get(composition, "strength", 0.0) or 0.0),
        confidence=confidence,
        sections=tuple(sections),
        total_evidence=len(all_items),
        primary_evidence=primary_count,
        unique_sources=unique_sources,
        data={
            "section_count": len(sections),
            "total_evidence": len(all_items),
            "primary_evidence": primary_count,
            "primary_ratio": round(primary_count / len(all_items), 3) if all_items else 0.0,
            "unique_source_count": len(unique_sources),
            "unique_type_count": len(unique_types),
            "blueprint_confidence": float(_get(composition, "confidence", 0.0) or 0.0),
        },
    )


# ==========================================================
# SOURCE COLLECTION
# ==========================================================

def _collect_sources(
    facts, priorities, relations, patterns,
    themes, semantics, interpretations, narratives,
) -> dict[str, list[Any]]:
    return {
        "fact": _as_list(facts),
        "priority": _as_list(priorities),
        "relation": _as_list(relations),
        "pattern": _as_list(patterns),
        "theme": _as_list(themes),
        "semantic": _as_list(semantics),
        "interpretation": _as_list(interpretations),
        "narrative": _as_list(narratives),
    }


# ==========================================================
# VALIDATION
# ==========================================================

def validate_evidence_report(report: EvidenceReport) -> list[str]:
    issues = []
    
    for plan in report.all():
        for section in plan.sections:
            if len(section.evidence) == 0:
                issues.append(
                    f"Section {section.section_type} has no evidence in plan {plan.theme_key}"
                )
            if (
                section.section_type in {"central_theme", "mechanism", "tension"}
                and len(section.evidence) < 3
            ):
                issues.append(
                    f"Critical section {section.section_type} has only "
                    f"{len(section.evidence)} evidence items in plan {plan.theme_key}"
                )
        
        if plan.primary_evidence < MIN_PRIMARY_EVIDENCE:
            issues.append(
                f"Plan {plan.theme_key} has only {plan.primary_evidence} "
                f"primary evidence items (minimum {MIN_PRIMARY_EVIDENCE})"
            )
        
        if plan.total_evidence < 10:
            issues.append(
                f"Plan {plan.theme_key} has only {plan.total_evidence} evidence items"
            )
    
    return issues


# ==========================================================
# PUBLIC API
# ==========================================================

def build_evidence(
    compositions,
    facts=None,
    priorities=None,
    relations=None,
    patterns=None,
    themes=None,
    semantics=None,
    interpretations=None,
    narratives=None,
    chart=None,
) -> EvidenceReport:
    """
    Строит EvidenceReport.
    """
    logger.info(f"Building evidence for {len(_as_list(compositions))} compositions")
    
    composition_list = _as_list(compositions)
    if not composition_list:
        logger.warning("No compositions provided")
        return EvidenceReport()
    
    sources = _collect_sources(
        facts=facts, priorities=priorities, relations=relations,
        patterns=patterns, themes=themes, semantics=semantics,
        interpretations=interpretations, narratives=narratives,
    )
    
    plans = []
    for composition in composition_list:
        plan = _build_evidence_plan(composition, sources)
        if plan.confidence < MIN_EVIDENCE_CONFIDENCE:
            logger.debug(f"Skipping plan {plan.theme_key} due to low confidence")
            continue
        plans.append(plan)
    
    report = EvidenceReport(plans)
    issues = validate_evidence_report(report)
    
    if issues:
        logger.warning(f"Evidence report has {len(issues)} issues:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info(f"Evidence report is valid: {len(report)} plans")
    
    return report


# ==========================================================
# CONVENIENCE FUNCTIONS
# ==========================================================

def strongest_evidence(report: EvidenceReport, n: int = 5) -> list[EvidencePlan]:
    return report.top(n)


def evidence_for_theme(report: EvidenceReport, theme_key: str) -> list[EvidencePlan]:
    return report.by_theme(theme_key)


def evidence_for_section(plan: EvidencePlan, section_type: str) -> list[EvidenceItem]:
    for section in plan.sections:
        if section.section_type == section_type:
            return list(section.evidence)
    return []


def evidence_summary(plan: EvidencePlan) -> dict[str, Any]:
    section_summary = {}
    for section in plan.sections:
        section_summary[section.section_type] = {
            "count": len(section.evidence),
            "priority": section.priority,
            "confidence": section.confidence,
            "sources": sorted({item.source for item in section.evidence}),
            "types": sorted({item.evidence_type for item in section.evidence}),
            "primary_count": sum(1 for item in section.evidence if item.source in PRIMARY_SOURCES),
            "source_distribution": {
                source: sum(1 for item in section.evidence if item.source == source)
                for source in set(item.source for item in section.evidence)
            },
        }
    
    return {
        "theme_key": plan.theme_key,
        "strength": plan.strength,
        "confidence": plan.confidence,
        "total_evidence": plan.total_evidence,
        "primary_evidence": plan.primary_evidence,
        "primary_ratio": round(plan.primary_ratio, 3),
        "unique_sources": list(plan.unique_sources),
        "sections": section_summary,
    }


def build_llm_payload(report: EvidenceReport, max_themes: int = 3) -> dict:
    return report.get_llm_payload(max_themes)