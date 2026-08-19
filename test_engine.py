"""
Liber Astrodum — Test Engine
Полный цикл: Chart → Facts → Priorities → Relations → Patterns → Themes → Semantics → Interpretations → Narrative → Compositions → Evidence → Prompts
"""

from builders.natal_builder import build_natal_chart
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


# ==========================================================
# ТЕСТОВЫЕ ДАННЫЕ
# ==========================================================
YEAR = 1991
MONTH = 2
DAY = 14
HOUR = 6
MINUTE = 55

LAT = 50.45
LON = 30.52


def main():
    print("=" * 70)
    print("LIBER ASTRODUM — ASTRODUM ENGINE TEST")
    print("=" * 70)

    # ------------------------------------------------------
    # 1. CHART
    # ------------------------------------------------------

    chart = build_natal_chart(
        year=YEAR,
        month=MONTH,
        day=DAY,
        hour=HOUR,
        minute=MINUTE,
        lat=LAT,
        lon=LON,
    )

    print("\n[CHART]")
    print(chart)

    # ------------------------------------------------------
    # 2. FACTS
    # ------------------------------------------------------

    facts = build_facts(chart)

    print("\n" + "=" * 70)
    print(f"[FACTS] {len(facts)}")
    print("=" * 70)

    for fact in facts.all():
        print(
            f"{fact.get('type'):20} "
            f"{fact.get('object'):25} "
            f"{fact.get('data')}"
        )

    # ------------------------------------------------------
    # 3. PRIORITIES
    # ------------------------------------------------------

    priorities = build_priorities(
        facts,
        chart_type=chart.type,
    )

    print("\n" + "=" * 70)
    print("[TOP PRIORITIES]")
    print("=" * 70)

    for fact in priorities.top(15):
        print(
            f"{fact.get('importance'):6.1f} "
            f"{fact.get('confidence'):6.1f} "
            f"{fact.get('type'):20} "
            f"{fact.get('object'):25} "
            f"{fact.get('importance_reasons')}"
        )

    # ------------------------------------------------------
    # 4. RELATIONS
    # ------------------------------------------------------

    relations = build_relations(
        facts,
        priorities,
    )

    print("\n" + "=" * 70)
    print(f"[RELATIONS] {len(relations)}")
    print("=" * 70)

    for relation in relations.top(30):
        print(
            f"{relation.importance:6.1f} "
            f"{relation.type:25} "
            f"{relation.source:15} → "
            f"{relation.target:20} "
            f"{relation.data}"
        )

    # ------------------------------------------------------
    # 5. ANALYSIS PIPELINE
    # ------------------------------------------------------

    patterns = build_patterns(
        relations,
        priorities,
    )
    themes = build_themes(
        patterns,
        relations,
        priorities,
    )
    semantics = build_semantics(
        themes,
        chart=chart,
        patterns=patterns,
        relations=relations,
        priorities=priorities,
    )
    interpretations = build_interpretations(
        semantics,
        chart=chart,
        themes=themes,
        patterns=patterns,
        relations=relations,
        priorities=priorities,
    )
    narratives = build_narrative(
        semantics,
        interpretations,
        themes=themes,
        chart=chart,
        patterns=patterns,
        relations=relations,
        priorities=priorities,
    )
    compositions = build_compositions(
        narratives,
        semantics=semantics,
        interpretations=interpretations,
        themes=themes,
        patterns=patterns,
        relations=relations,
        priorities=priorities,
        chart=chart,
    )
    evidence = build_evidence(
        compositions,
        facts=facts,
        priorities=priorities,
        relations=relations,
        patterns=patterns,
        themes=themes,
        semantics=semantics,
        interpretations=interpretations,
        narratives=narratives,
        chart=chart,
    )

    # ==========================================================
    # COMPOSITION PLANS
    # ==========================================================

    print("\n" + "=" * 70)
    print(f"[COMPOSITION PLANS] {len(compositions)}")
    print("=" * 70)

    for plan in compositions.top(10):
        print(
            f"{plan.strength:7.1f} "
            f"conf={plan.confidence:.2f} "
            f"{plan.theme_key}"
        )
        print(f"  core_theme:        {plan.core_theme}")
        print(f"  dominant_process:  {plan.dominant_process}")
        print(f"  claims:            {plan.central_claims}")
        print(f"  sections:          {len(plan.sections)}")

        for section in plan.sections:
            print(
                f"    {section.section_type:15} "
                f"priority={section.priority:5.1f} "
                f"{section.title}"
            )

    # ==========================================================
    # EVIDENCE PLANS
    # ==========================================================

    print("\n" + "=" * 70)
    print(f"[EVIDENCE PLANS] {len(evidence)}")
    print("=" * 70)

    for plan in evidence.top(3):
        print(f"\n{plan.theme_key}")
        print(f"  strength:        {plan.strength:.2f}")
        print(f"  confidence:      {plan.confidence:.3f}")
        print(f"  total_evidence:   {plan.total_evidence}")
        print(f"  primary_evidence: {plan.primary_evidence}")
        print(f"  unique_sources:   {plan.unique_sources}")

        print("\n  SECTIONS:")

        for section in plan.sections:
            print(
                f"    [{section.section_type}] "
                f"{section.title} "
                f"confidence={section.confidence:.3f} "
                f"evidence={len(section.evidence)}"
            )

            for item in section.evidence:
                # Показываем natural_language если есть
                if item.natural_language:
                    print(
                        f"      - {item.source}:"
                        f"{item.kind} "
                        f"score={item.score:.2f} "
                        f"| {item.natural_language}"
                    )
                else:
                    print(
                        f"      - {item.source}:"
                        f"{item.kind} "
                        f"{item.key} "
                        f"score={item.score:.2f}"
                    )

    # ==========================================================
    # PROMPTS FOR LLM
    # ==========================================================

    print("\n" + "=" * 70)
    print("[PROMPTS FOR LLM]")
    print("=" * 70)

    prompts = build_prompts(
        compositions=compositions,
        evidence_report=evidence,
        chart=chart,
        chart_type=chart.type if hasattr(chart, 'type') else 'natal',
    )

    for theme_key, prompt in prompts.items():
        print(f"\n{'=' * 70}")
        print(f"THEME: {theme_key}")
        print(f"PROMPT LENGTH: {len(prompt)} chars")
        print(f"{'=' * 70}")
        # Показываем первые 3000 символов
        print(prompt[:3000])
        if len(prompt) > 3000:
            print(f"\n... [ещё {len(prompt) - 3000} chars]")

    # ==========================================================
    # NARRATIVE BLUEPRINTS
    # ==========================================================

    print("\n" + "=" * 70)
    print(f"[NARRATIVE BLUEPRINTS] {len(narratives)}")
    print("=" * 70)

    for blueprint in narratives:
        print(
            f"{blueprint.strength:7.1f} "
            f"conf={blueprint.confidence:.2f} "
            f"{blueprint.theme_key}"
        )
        print(f"  core_theme:        {blueprint.core_theme}")
        print(f"  dominant_process:  {blueprint.dominant_process}")
        print(f"  mechanisms:        {blueprint.mechanisms}")
        print(f"  dynamics:          {blueprint.dynamics}")
        print(f"  tensions:          {blueprint.tensions}")
        print(f"  supports:          {blueprint.supports}")
        print(f"  manifestations:    {blueprint.manifestations}")
        print(f"  resolution:        {blueprint.resolution}")
        print()

    # ------------------------------------------------------
    # 6. SUMMARY
    # ------------------------------------------------------

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Facts:     {len(facts)}")
    print(f"Priorities:{len(priorities)}")
    print(f"Relations: {len(relations)}")
    print(f"Patterns:  {len(patterns)}")
    print(f"Themes:    {len(themes)}")
    print(f"Evidence:  {len(evidence)}")
    print(f"Prompts:   {len(prompts)}")

    print("\nTop patterns:")
    for pattern in patterns.top(5):
        print(
            f"  • {pattern.type}: "
            f"{pattern.theme_hint} "
            f"[{pattern.strength}]"
        )


if __name__ == "__main__":
    main()