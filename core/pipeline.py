"""
Liber Astrodum

core/pipeline.py

Главный конвейер Liber Astrodum 2.0.
Собирает всю цепочку: Chart → Facts → Priorities → Dominants → Reasoning.

Не генерирует текст. Возвращает AnalysisContext.

Спецификация: docs/PIPELINE_SPEC.md

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.0
"""

from core.chart import Chart
from fact_engine.fact_builder import build_facts
from priority_engine.priority_builder import build_priorities
from core.dominants import build_dominant_report
from core.reasoning import build_reasoning_report
from core.prompt_context import build_prompt_context


class AnalysisContext:
    """
    Полный результат анализа карты.
    """

    def __init__(self, chart, facts, priorities, dominants, reasoning):
        self.chart = chart
        self.facts = facts
        self.priorities = priorities
        self.dominants = dominants
        self.reasoning = reasoning

    def to_dict(self) -> dict:
        return {
            "chart": self.chart.to_dict(),
            "facts": self.facts.to_list() if hasattr(self.facts, 'to_list') else list(self.facts),
            "priorities": self.priorities.to_list() if hasattr(self.priorities, 'to_list') else list(self.priorities),
            "dominants": self.dominants.to_dict() if hasattr(self.dominants, 'to_dict') else self.dominants,
            "reasoning": self.reasoning.to_dict() if hasattr(self.reasoning, 'to_dict') else self.reasoning,
        }

    def __repr__(self) -> str:
        return (f"<AnalysisContext type={self.chart.type} "
                f"facts={len(self.facts)}>")


def run_pipeline(chart: Chart) -> AnalysisContext:
    """
    Прогоняет карту через полный конвейер анализа.

    Parameters
    ----------
    chart : Chart

    Returns
    -------
    AnalysisContext
    """
    facts = build_facts(chart)
    priorities = build_priorities(facts, chart_type=chart.type)
    dominants = build_dominant_report(chart, priorities)
    reasoning = build_reasoning_report(chart, priorities, dominants)

    return AnalysisContext(
        chart=chart,
        facts=facts,
        priorities=priorities,
        dominants=dominants,
        reasoning=reasoning,
    )
def run_full_pipeline(chart: Chart) -> dict:
    """
    Полный цикл: Chart → AnalysisContext → PromptContext.
    Возвращает всё, что нужно для Prompt Builder.
    """
    analysis = run_pipeline(chart)
    prompt_ctx = build_prompt_context(analysis)
    return {
        "analysis": analysis.to_dict(),
        "prompt_context": prompt_ctx.to_dict(),
    }