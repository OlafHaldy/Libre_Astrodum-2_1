"""
Liber Astrodum

core/prompt_context.py

PromptContext — промежуточный слой между Pipeline и Prompt Engine.
Преобразует AnalysisContext в структуру, готовую для генерации текста.

Не содержит текста. Только структурированные данные.
Prompt Builder превратит это в промпт.

Автор:
    Olaf Haldi

Архитектура:
    Liber Astrodum 2.0

Версия:
    2.0
"""


class PromptContext:
    """
    Данные, подготовленные для Prompt Builder.

    Содержит:
    - main_theme: структура главной темы
    - key_factors: ключевые факторы (топ-5 по importance)
    - strengths: сильные стороны карты (высокая confidence)
    - challenges: слабые места (низкая confidence)
    - contradictions: противоречия
    - dominant_elements: доминирующие стихии
    - dominant_modes: доминирующие кресты
    - dominant_houses: доминирующие дома
    """

    def __init__(
        self,
        main_theme,
        key_factors,
        strengths,
        challenges,
        contradictions,
        dominant_elements,
        dominant_modes,
        dominant_houses,
    ):
        self.main_theme = main_theme
        self.key_factors = key_factors
        self.strengths = strengths
        self.challenges = challenges
        self.contradictions = contradictions
        self.dominant_elements = dominant_elements
        self.dominant_modes = dominant_modes
        self.dominant_houses = dominant_houses

    def to_dict(self) -> dict:
        return {
            "main_theme": self.main_theme.to_dict() if hasattr(self.main_theme, 'to_dict') else self.main_theme,
            "key_factors": [f.to_dict() if hasattr(f, 'to_dict') else f for f in self.key_factors],
            "strengths": [s.to_dict() if hasattr(s, 'to_dict') else s for s in self.strengths],
            "challenges": [c.to_dict() if hasattr(c, 'to_dict') else c for c in self.challenges],
            "contradictions": [c.to_dict() if hasattr(c, 'to_dict') else c for c in self.contradictions],
            "dominant_elements": self.dominant_elements,
            "dominant_modes": self.dominant_modes,
            "dominant_houses": self.dominant_houses,
        }


def build_prompt_context(analysis_context) -> PromptContext:
    """
    Строит PromptContext из AnalysisContext.

    Parameters
    ----------
    analysis_context : AnalysisContext

    Returns
    -------
    PromptContext
    """
    reasoning = analysis_context.reasoning
    dominants = analysis_context.dominants
    priorities = analysis_context.priorities

    # Главная тема
    main_theme = reasoning.main_theme

    # Ключевые факторы: топ-5 по importance
    key_factors = priorities.top(5)

    # Сильные стороны: факты с confidence > 55
    strengths = [
        f for f in priorities
        if f.get('confidence', 50) > 55
    ][:5]

    # Слабые места: факты с confidence < 45 и importance > 15
    challenges = [
        f for f in priorities
        if f.get('confidence', 50) < 45 and f.get('importance', 0) > 15
    ][:5]

    # Противоречия
    contradictions = reasoning.contradictions

    # Доминанты
    dominant_elements = dominants.elements
    dominant_modes = dominants.modes
    dominant_houses = dominants.houses

    return PromptContext(
        main_theme=main_theme,
        key_factors=key_factors,
        strengths=strengths,
        challenges=challenges,
        contradictions=contradictions,
        dominant_elements=dominant_elements,
        dominant_modes=dominant_modes,
        dominant_houses=dominant_houses,
    )