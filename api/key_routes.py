from fastapi import APIRouter, Query
from core.key_to_sign import get_key_aphorism, SIGN_NAMES_RU, KEY_CATEGORIES

router = APIRouter(prefix="/api/v1/key", tags=["key"])

@router.get("")
def key_aphorism(
    sign: str = Query("Aquarius", description="Знак зодиака на английском"),
    category: str = Query(None, description="Категория: Дом, Работа, Любовь и т.д.")
):
    """Получить афоризм для знака"""
    
    # Валидация знака
    if sign not in SIGN_NAMES_RU:
        return {"error": f"Unknown sign: {sign}"}, 400
    
    # Валидация категории
    if category and category not in KEY_CATEGORIES:
        return {"error": f"Unknown category: {category}"}, 400
    
    result = get_key_aphorism(sign, category)
    return result


@router.get("/categories")
def list_categories():
    """Список всех категорий с иконками"""
    return {
        "categories": [
            {"name": name, "icon": data["icon"]}
            for name, data in KEY_CATEGORIES.items()
        ]
    }