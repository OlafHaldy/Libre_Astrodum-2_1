from builders.natal_builder import build_natal_chart
from fact_engine.fact_builder import build_facts
from priority_engine.priority_builder import build_priorities
from core.relations import build_relations
from core.patterns import build_patterns
from core.themes import build_themes
from core.semantics import build_semantics


# ==========================================================
# ТЕСТОВЫЕ ДАННЫЕ
# ==========================================================
# Замени эти значения на любые данные для проверки.

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
    # 5. PATTERNS
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

    print("\n" + "=" * 70)
    print(f"[PATTERNS] {len(patterns)}")
    print("=" * 70)

    for pattern in patterns.top(20):
        print(
            f"{pattern.strength:6.1f} "
            f"{pattern.type:25} "
            f"{pattern.theme_hint:30} "
            f"{pattern.data}"
        )
    print("\n" + "=" * 70)
    print("[TENSIONS]")
    print("=" * 70)

    for pattern in patterns.tensions:
        print(
            f"{pattern.strength:6.1f} "
            f"{pattern.data}"
        )

    print("\n" + "=" * 70)
    print("[SUPPORTS]")
    print("=" * 70)

    for pattern in patterns.supports:
        print(
            f"{pattern.strength:6.1f} "
            f"{pattern.data}"
        )

    print("\n" + "=" * 70)

    print("[PATTERN TYPES]")
    

    print("=" * 70)

    pattern_types = {}

    for pattern in patterns:
        pattern_types[pattern.type] = (
            pattern_types.get(pattern.type, 0) + 1
        )

    for pattern_type, count in sorted(pattern_types.items()):
        print(f"{pattern_type:30} {count}")
        print("\n" + "=" * 70)
    print(f"[THEMES] {len(themes)}")
    print("=" * 70)

    for theme in themes.top(10):
        print(
            f"{theme.strength:6.1f} "
            f"coherence={theme.coherence:5.1f} "
            f"evidence={theme.evidence_count:2} "
            f"{theme.theme_key:30} "
            f"planets={theme.planets} "
            f"houses={theme.houses}"
        )

    print("\n" + "=" * 70)
    print("[THEME DETAILS]")
    print("=" * 70)

    for theme in themes.top(5):
        print(f"\n{theme.theme_key}")
        print(f"  strength:   {theme.strength}")
        print(f"  coherence:  {theme.coherence}")
        print(f"  evidence:   {theme.evidence_count}")
        print(f"  patterns:   {theme.pattern_types}")
        print(f"  planets:    {theme.planets}")
        print(f"  houses:     {theme.houses}")
        print(f"  tensions:   {theme.tensions}")
        print(f"  supports:   {theme.supports}")    
        print("\n" + "=" * 70)
    print(f"[SEMANTICS] {len(semantics)}")
    print("=" * 70)

    for profile in semantics.top(10):
        print(
            f"{profile.strength:6.1f} "
            f"conf={profile.data.get('semantic_confidence', 0):.2f} "
            f"{profile.theme_key}"
        )

        print(
            f"  domains:   {profile.domains}"
        )

        print(
            f"  keywords:  {profile.keywords}"
        )

        print(
            f"  planets:   {profile.planets}"
        )

        print(
            f"  houses:    {profile.houses}"
        )

        print(
            f"  roles:     {profile.primary_roles}"
        )

        print(
            f"  secondary: {profile.secondary_roles}"
        )

        print(
            f"  processes: {profile.processes}"
        )

        print(
            f"  claims:    {profile.data.get('claim_count', 0)}"
        )

        for claim in profile.claims:
            print(
                f"    - {claim.kind}: "
                f"{claim.key} "
                f"(conf={claim.confidence:.2f})"
            )

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

    print("\nTop patterns:")

    for pattern in patterns.top(5):
        print(
            f"  • {pattern.type}: "
            f"{pattern.theme_hint} "
            f"[{pattern.strength}]"
        )


if __name__ == "__main__":
    main()
