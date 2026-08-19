"""
Проверка размеров промптов и полного цикла.
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

import time
import json


def main():
    print("=" * 70)
    print("PROMPT SIZE TEST")
    print("=" * 70)
    
    # Засекаем время
    start_time = time.time()
    
    # 1. Chart
    print("\n[1/10] Создание карты...")
    chart = build_natal_chart(
        year=1991, month=2, day=14,
        hour=6, minute=55,
        lat=50.45, lon=30.52,
    )
    print(f"  ✓ Chart: {chart.type}, {chart.datetime}")
    
    # 2. Facts
    print("[2/10] Извлечение фактов...")
    facts = build_facts(chart)
    print(f"  ✓ Facts: {len(facts)}")
    
    # 3. Priorities
    print("[3/10] Расчёт приоритетов...")
    priorities = build_priorities(facts, chart_type=chart.type)
    print(f"  ✓ Priorities: {len(priorities)}")
    
    # 4. Relations
    print("[4/10] Построение отношений...")
    relations = build_relations(facts, priorities)
    print(f"  ✓ Relations: {len(relations)}")
    
    # 5. Patterns
    print("[5/10] Поиск паттернов...")
    patterns = build_patterns(relations, priorities)
    print(f"  ✓ Patterns: {len(patterns)}")
    
    # 6. Themes
    print("[6/10] Определение тем...")
    themes = build_themes(patterns, relations, priorities)
    print(f"  ✓ Themes: {len(themes)}")
    
    # 7. Semantics
    print("[7/10] Семантический анализ...")
    semantics = build_semantics(
        themes, chart=chart, patterns=patterns,
        relations=relations, priorities=priorities,
    )
    print(f"  ✓ Semantics: {len(semantics)}")
    
    # 8. Interpretations
    print("[8/10] Интерпретации...")
    interpretations = build_interpretations(
        semantics, chart=chart, themes=themes,
        patterns=patterns, relations=relations,
        priorities=priorities,
    )
    print(f"  ✓ Interpretations: {len(interpretations)}")
    
    # 9. Narrative
    print("[9/10] Нарративные чертежи...")
    narratives = build_narrative(
        semantics, interpretations,
        themes=themes, chart=chart,
        patterns=patterns, relations=relations,
        priorities=priorities,
    )
    print(f"  ✓ Narratives: {len(narratives)}")
    
    # 10. Compositions + Evidence + Prompts
    print("[10/10] Композиции, Evidence, Промпты...")
    compositions = build_compositions(
        narratives,
        semantics=semantics,
        interpretations=interpretations,
        themes=themes, patterns=patterns,
        relations=relations, priorities=priorities,
        chart=chart,
    )
    print(f"  ✓ Compositions: {len(compositions)}")
    
    evidence = build_evidence(
        compositions,
        facts=facts, priorities=priorities,
        relations=relations, patterns=patterns,
        themes=themes, semantics=semantics,
        interpretations=interpretations,
        narratives=narratives, chart=chart,
    )
    print(f"  ✓ Evidence Plans: {len(evidence)}")
    
    prompts = build_prompts(
        compositions=compositions,
        evidence_report=evidence,
        chart=chart,
        chart_type=chart.type,
    )
    print(f"  ✓ Prompts: {len(prompts)}")
    
    # Время выполнения
    elapsed = time.time() - start_time
    
    # ==========================================================
    # РЕЗУЛЬТАТЫ
    # ==========================================================
    
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 70)
    
    print(f"\nВремя выполнения: {elapsed:.2f} сек")
    
    print("\n" + "-" * 70)
    print("РАЗМЕРЫ ПРОМПТОВ")
    print("-" * 70)
    
    total_chars = 0
    total_tokens_approx = 0
    
    for theme_key, prompt in prompts.items():
        chars = len(prompt)
        tokens_approx = chars // 4  # Примерно 4 символа на токен
        
        total_chars += chars
        total_tokens_approx += tokens_approx
        
        print(f"\n  {theme_key}:")
        print(f"    Символов: {chars:,}")
        print(f"    Токенов (approx): {tokens_approx:,}")
        
        # Показываем структуру промпта
        lines = prompt.split("\n")
        sections = [l for l in lines if l.startswith(("Карта:", "Тема:", "ДОКАЗАТЕЛЬСТВА", "Режим:", "Правила:", "Стиль:", "Формат:"))]
        
        print(f"    Секции: {len(sections)}")
        for section in sections:
            print(f"      {section[:60]}...")
    
    print(f"\n  ИТОГО:")
    print(f"    Символов: {total_chars:,}")
    print(f"    Токенов (approx): {total_tokens_approx:,}")
    print(f"    Средний размер: {total_chars // len(prompts):,} символов")
    
    # ==========================================================
    # ПРОВЕРКА СОДЕРЖИМОГО
    # ==========================================================
    
    print("\n" + "-" * 70)
    print("ПРОВЕРКА СОДЕРЖИМОГО")
    print("-" * 70)
    
    first_theme = list(prompts.keys())[0] if prompts else None
    
    if first_theme:
        prompt = prompts[first_theme]
        
        checks = {
            "Chart metadata": "Карта:" in prompt,
            "Composition": "Тема:" in prompt,
            "Evidence": "ДОКАЗАТЕЛЬСТВА" in prompt,
            "Rules": "Правила:" in prompt,
            "Style": "Стиль:" in prompt,
            "Output format": "Формат ответа:" in prompt,
            "Sections": "[SECTION:" in prompt,
        }
        
        for check_name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
        
        # Проверяем JSON evidence
        if "ДОКАЗАТЕЛЬСТВА" in prompt:
            evidence_part = prompt.split("ДОКАЗАТЕЛЬСТВА:")[1].split("Режим:")[0].strip()
            try:
                evidence_json = json.loads(evidence_part)
                section_count = len(evidence_json)
                total_evidence = sum(len(v) for v in evidence_json.values())
                print(f"  ✓ Evidence JSON: {section_count} секций, {total_evidence} доказательств")
            except json.JSONDecodeError:
                print(f"  ✗ Evidence JSON: ошибка парсинга")
    
    # ==========================================================
    # ПРИМЕР ПРОМПТА (первые 2000 символов)
    # ==========================================================
    
    print("\n" + "-" * 70)
    print("ПРИМЕР ПРОМПТА (первые 2000 символов)")
    print("-" * 70)
    
    if first_theme:
        print(prompts[first_theme][:2000])
    
    # ==========================================================
    # СТОИМОСТЬ (ПРИМЕРНО)
    # ==========================================================
    
    print("\n" + "-" * 70)
    print("ПРИМЕРНАЯ СТОИМОСТЬ (GPT-4)")
    print("-" * 70)
    
    # Цены GPT-4 (примерные)
    input_price_per_1k = 0.03  # $ за 1000 токенов
    output_price_per_1k = 0.06
    
    for theme_key, prompt in prompts.items():
        input_tokens = len(prompt) // 4
        input_cost = (input_tokens / 1000) * input_price_per_1k
        # Предполагаем вывод ~1000 токенов
        output_cost = (1000 / 1000) * output_price_per_1k
        total_cost = input_cost + output_cost
        
        print(f"  {theme_key}: ${total_cost:.4f} (вход: ${input_cost:.4f} + вывод: ${output_cost:.4f})")
    
    print(f"\n  ИТОГО за 3 темы: ${sum((len(p) // 4 / 1000) * 0.03 + 0.06 for p in prompts.values()):.4f}")


if __name__ == "__main__":
    main()