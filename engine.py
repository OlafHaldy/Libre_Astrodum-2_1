"""
Liber Astrodum — Unified Engine
Единая точка входа для Flask/FastAPI app.
"""

from fact_engine.fact_builder import build_facts
from priority_engine.priority_builder import build_priorities
from core.relations import build_relations
from core.patterns import build_patterns
from core.themes import build_themes
from core.semantics import build_semantics
from core.interpretation import build_interpretations
from core.narrative import build_narrative
from core.composer import build_compositions
from core.evidence import build_evidence
from core.prompt_builder import build_prompts


def analyze_full(chart):
    """
    Принимает готовый Chart.
    Возвращает полный результат анализа.
    """
    
    facts = build_facts(chart)
    priorities = build_priorities(facts, chart_type=chart.type)
    relations = build_relations(facts, priorities)
    patterns = build_patterns(relations, priorities)
    themes = build_themes(patterns, relations, priorities)
    semantics = build_semantics(
        themes, chart=chart, patterns=patterns,
        relations=relations, priorities=priorities,
    )
    interpretations = build_interpretations(
        semantics, chart=chart, themes=themes,
        patterns=patterns, relations=relations,
        priorities=priorities,
    )
    narratives = build_narrative(
        semantics, interpretations,
        themes=themes, chart=chart,
        patterns=patterns, relations=relations,
        priorities=priorities,
    )
    compositions = build_compositions(
        narratives,
        semantics=semantics,
        interpretations=interpretations,
        themes=themes, patterns=patterns,
        relations=relations, priorities=priorities,
        chart=chart,
    )
    evidence = build_evidence(
        compositions,
        facts=facts, priorities=priorities,
        relations=relations, patterns=patterns,
        themes=themes, semantics=semantics,
        interpretations=interpretations,
        narratives=narratives, chart=chart,
    )
    prompts = build_prompts(
        compositions=compositions,
        evidence_report=evidence,
        chart=chart,
        chart_type=chart.type,
    )
    
    return {
        "facts": facts,
        "priorities": priorities,
        "relations": relations,
        "patterns": patterns,
        "themes": themes,
        "semantics": semantics,
        "interpretations": interpretations,
        "narratives": narratives,
        "compositions": compositions,
        "evidence": evidence,
        "prompts": prompts,
    }
