"""
Liber Astrodum

priority_builder.py

Строитель приоритетов.
Принимает FactCollection, возвращает список фактов
с добавленными полями priority, weight и reason.

Использует правила классической астрологии:
- Для лунара: Луна и управитель ASC имеют высший приоритет.
- Для натала: управитель ASC, Солнце, Луна.
- Планеты в угловых домах, в обители, с аспектами к главным
  планетам получают повышенный вес.

Автор:
    Olaf Haldi

Архитектура:
    Astrodo Stage III — Priority Engine v1.0

Версия:
    1.0
"""

# ==========================================================
# КОНСТАНТЫ ВЕСОВ
# ==========================================================

# Базовые веса для разных типов фактов
BASE_WEIGHTS = {
    'planet_position': 10,
    'planet_sign': 5,
    'house_position': 5,
    'house_ruler': 20,
    'ruler_strength': 15,
    'aspect': 8,
    'element_balance': 3,
    'modality_balance': 3,
    'stellium': 12,
}

# Бонусы за роль планеты
ROLE_BONUS = {
    'asc_ruler': 30,       # Управитель ASC
    'lunar_moon': 35,      # Луна в лунаре
    'solar_sun': 35,       # Солнце в соляре
    'natal_sun': 25,       # Солнце в натале
    'natal_moon': 25,      # Луна в натале
    'dispositor': 20,      # Диспозитор главной планеты
}

# Бонусы за положение
POSITION_BONUS = {
    'angular': 15,         # В угловом доме (1, 4, 7, 10)
    'succedent': 8,        # В последующем доме (2, 5, 8, 11)
    'cadent': 0,           # В падающем доме (3, 6, 9, 12)
    'domicile': 12,        # В обители
    'exaltation': 10,      # В экзальтации
    'detriment': -5,       # В изгнании
    'fall': -8,            # В падении
}

# Бонус за аспект к главной планете
ASPECT_TO_MAIN_BONUS = 10

# Угловые дома
ANGULAR_HOUSES = {1, 4, 7, 10}
SUCCEDENT_HOUSES = {2, 5, 8, 11}
CADENT_HOUSES = {3, 6, 9, 12}

# ==========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================================

def _find_asc_sign(facts):
    """Находит знак Асцендента из фактов."""
    for f in facts:
        if f['type'] == 'house_position' and f['object'] == 'House_1':
            return f['data'].get('sign', '')
    return ''


def _find_asc_ruler(facts):
    """Находит управителя ASC из фактов house_ruler."""
    for f in facts:
        if f['type'] == 'house_ruler' and f['data'].get('house') == 1:
            return f['object']
    return ''


def _find_main_planet(facts, chart_type='lunar'):
    """
    Определяет главную планету в зависимости от типа карты.
    Лунар → Луна. Соляр → Солнце. Натал → управитель ASC.
    """
    if chart_type == 'lunar':
        return 'Moon'
    elif chart_type == 'solar':
        return 'Sun'
    else:
        return _find_asc_ruler(facts)


def _find_dispositor(facts, planet_name):
    """
    Находит диспозитора планеты.
    Диспозитор = управитель знака, в котором стоит планета.
    """
    for f in facts:
        if f['type'] == 'planet_sign' and f['object'] == planet_name:
            sign = f['data'].get('sign', '')
            # Ищем управителя этого знака
            for rf in facts:
                if rf['type'] == 'house_ruler':
                    ruler_sign = rf['data'].get('sign', '')
                    if ruler_sign == sign:
                        # Нашли дом, где на куспиде этот знак.
                        # Управитель этого дома = управитель знака.
                        return rf['object']
            # Fallback: используем dignities
            from dignities import DOMICILE
            for planet, signs in DOMICILE.items():
                if sign in signs:
                    return planet
    return ''


def _get_house(planet_name, facts):
    """Возвращает номер дома, в котором стоит планета."""
    for f in facts:
        if f['type'] == 'planet_position' and f['object'] == planet_name:
            return f['data'].get('house')
    return None


def _is_angular(house):
    return house in ANGULAR_HOUSES


def _is_succedent(house):
    return house in SUCCEDENT_HOUSES


def _get_essential_dignities(planet_name, facts):
    """Извлекает данные о достоинствах из фактов ruler_strength."""
    for f in facts:
        if f['type'] == 'ruler_strength' and f['object'] == planet_name:
            return f['data'].get('essential_details', {})
    return {}


def _has_aspect_to(planet_name, target_planet, facts):
    """Проверяет, есть ли аспект между двумя планетами."""
    for f in facts:
        if f['type'] == 'aspect':
            p1 = f['data'].get('planet1', '')
            p2 = f['data'].get('planet2', '')
            if (p1 == planet_name and p2 == target_planet) or                (p2 == planet_name and p1 == target_planet):
                return True
    return False

# ==========================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ==========================================================

def build_priorities(facts, chart_type='lunar'):
    """
    Принимает список фактов (list[dict]) и возвращает новый список
    с добавленными полями priority, weight и reason.

    Parameters
    ----------
    facts : list[dict]
        Список фактов из Fact Engine.
    chart_type : str
        Тип карты: 'natal', 'lunar', 'solar', 'transit', 'synastry'.

    Returns
    -------
    list[dict]
        Факты с полями priority, weight, reason.
    """
    # Преобразуем в list, если пришёл FactCollection
    if hasattr(facts, 'all'):
        facts = facts.all()

    main_planet = _find_main_planet(facts, chart_type)
    asc_ruler = _find_asc_ruler(facts)
    main_dispositor = _find_dispositor(facts, main_planet) if main_planet else ''

    result = []

    for fact in facts:
        weight = BASE_WEIGHTS.get(fact['type'], 5)
        reason_parts = []
        bonus = 0

        obj = fact.get('object', '')

        # --------------------------------------------------
        # РОЛЕВЫЕ БОНУСЫ
        # --------------------------------------------------
        if chart_type == 'lunar' and obj == 'Moon':
            bonus += ROLE_BONUS['lunar_moon']
            reason_parts.append('Луна (главная планета лунара)')

        if chart_type == 'solar' and obj == 'Sun':
            bonus += ROLE_BONUS['solar_sun']
            reason_parts.append('Солнце (главная планета соляра)')

        if obj == asc_ruler and asc_ruler:
            bonus += ROLE_BONUS['asc_ruler']
            reason_parts.append('Управитель ASC')

        if obj == main_dispositor and main_dispositor:
            bonus += ROLE_BONUS['dispositor']
            reason_parts.append(f'Диспозитор {main_planet}')

        if chart_type == 'natal' and obj == 'Sun':
            bonus += ROLE_BONUS['natal_sun']
            reason_parts.append('Солнце (натал)')

        if chart_type == 'natal' and obj == 'Moon':
            bonus += ROLE_BONUS['natal_moon']
            reason_parts.append('Луна (натал)')

        # --------------------------------------------------
        # БОНУСЫ ЗА ПОЛОЖЕНИЕ
        # --------------------------------------------------
        house = _get_house(obj, facts)
        if house:
            if _is_angular(house):
                bonus += POSITION_BONUS['angular']
                reason_parts.append(f'В угловом доме ({house})')
            elif _is_succedent(house):
                bonus += POSITION_BONUS['succedent']
                reason_parts.append(f'В последующем доме ({house})')
            else:
                bonus += POSITION_BONUS['cadent']

        # Достоинства
        dignities = _get_essential_dignities(obj, facts)
        if dignities:
            if dignities.get('domicile'):
                bonus += POSITION_BONUS['domicile']
                reason_parts.append('В обители')
            if dignities.get('exaltation'):
                bonus += POSITION_BONUS['exaltation']
                reason_parts.append('В экзальтации')
            if dignities.get('detriment'):
                bonus += POSITION_BONUS['detriment']
                reason_parts.append('В изгнании')
            if dignities.get('fall'):
                bonus += POSITION_BONUS['fall']
                reason_parts.append('В падении')

        # --------------------------------------------------
        # БОНУСЫ ЗА АСПЕКТЫ К ГЛАВНОЙ ПЛАНЕТЕ
        # --------------------------------------------------
        if main_planet and obj != main_planet:
            if _has_aspect_to(obj, main_planet, facts):
                bonus += ASPECT_TO_MAIN_BONUS
                reason_parts.append(f'Аспект к {main_planet}')

        # --------------------------------------------------
        # БОНУС ЗА УПРАВЛЕНИЕ НЕСКОЛЬКИМИ ДОМАМИ
        # --------------------------------------------------
        if fact['type'] == 'house_ruler':
            house_count = sum(
                1 for f in facts
                if f['type'] == 'house_ruler' and f['object'] == obj
            )
            if house_count > 1:
                bonus += house_count * 5
                reason_parts.append(f'Управляет {house_count} домами')

        # --------------------------------------------------
        # ИТОГОВЫЙ ВЕС
        # --------------------------------------------------
        total_weight = weight + bonus

        # Нормализуем priority в диапазон 0-100
        # Максимально возможный вес ~ 100
        priority = min(100, max(0, total_weight))

        result.append({
            **fact,
            'priority': priority,
            'weight': total_weight,
            'reason': '; '.join(reason_parts) if reason_parts else 'Базовый приоритет',
        })

    # ------------------------------------------------------
    # СОРТИРОВКА ПО УБЫВАНИЮ ПРИОРИТЕТА
    # ------------------------------------------------------
    result.sort(key=lambda f: f['priority'], reverse=True)

    return result
