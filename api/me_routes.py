"""
Liber Astrodum - api/me_routes.py
User profile and natal chart.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

from db.database import get_db
from db.models import User, NatalChart
from core.auth import require_user
from core.prompt_builder import build_prompt

router = APIRouter(prefix="/api/v1/me", tags=["me"])


class NatalData(BaseModel):
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int = 12
    birth_minute: int = 0
    birth_lat: float
    birth_lon: float
    birth_city: str = ""


@router.get("/")
def get_me(user: User = Depends(require_user)):
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name or "Искатель",
        "avatar_url": user.avatar_url or "",
        "has_natal": user.natal_chart is not None,
        "created_at": user.created_at.strftime("%d.%m.%Y") if user.created_at else "",
    }


@router.post("/natal")
def save_natal(
    data: NatalData,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    from builders.natal_builder import build_natal_chart
    from ai import generate
    from graphics.wheel_renderer import draw_wheel
    import json

    try:
        # Строим натал
        chart = build_natal_chart(
            data.birth_year, data.birth_month, data.birth_day,
            data.birth_hour, data.birth_minute,
            data.birth_lat, data.birth_lon,
        )

        # Колесо
        wheel_svg = draw_wheel(chart)

        # === СОБИРАЕМ КОНТЕКСТ ДЛЯ ПОРТРЕТА ===
        context_lines = []

        if "Sun" in chart.planets:
            sun = chart.planets["Sun"]
            context_lines.append(f"Солнце: {sun['degree']}° {sun['sign']}")
        if "Moon" in chart.planets:
            moon = chart.planets["Moon"]
            context_lines.append(f"Луна: {moon['degree']}° {moon['sign']}")
        if "Ascendant" in chart.houses:
            asc = chart.houses["Ascendant"]
            context_lines.append(f"Асцендент: {asc['degree']}° {asc['sign']}")

        context_lines.append("")
        for planet, pdata in chart.planets.items():
            if planet in ["Sun", "Moon"]:
                continue
            context_lines.append(f"{planet}: {pdata['degree']}° {pdata['sign']}")

        context_lines.append("")
        for i in range(1, 13):
            house = chart.houses.get(i)
            if house:
                context_lines.append(f"Дом {i}: {house['sign']}")

        context_text = "\n".join(context_lines)

        # === ПРОМПТ ПОРТРЕТА ===
        prompt = f"""Ты — Астродо, хранитель Небесного Архива Liber Astrodum.

Ты читаешь натальную карту человека. Это не отчёт — это портрет его души.

Твоя задача — создать глубокое, живое и целостное описание личности.

Это НЕ список аспектов.
Это НЕ техническая интерпретация.
Это НЕ гороскоп.
Это НЕ совет.
Это НЕ предсказание.

Это — ПОРТРЕТ ЧЕЛОВЕКА, написанный языком звёзд.

═══════════════════════════════════════

ДАННЫЕ КАРТЫ:
{context_text}

═══════════════════════════════════════

СТРУКТУРА (ровно 5 секций):

[SECTION:PORTRAIT] — Портрет
Опиши человека как целостную личность. Не перечисляй планеты — покажи, как они сплетаются в характер. 3-4 предложения.

[SECTION:STRENGTH] — Сила
В чём главный дар этого человека? Что помогает ему идти по жизни? 2-3 предложения.

[SECTION:SHADOW] — Тень
Что мешает? Где внутренний конфликт? Без осуждения, с пониманием. 2-3 предложения.

[SECTION:PATH] — Путь
Куда ведёт эта карта? Какой урок души? Какая цель? 2-3 предложения.

[SECTION:GIFT] — Дар
Одно короткое предложение — как афоризм. Что человек может подарить миру.

═══════════════════════════════════════

СТИЛЬ:
- Обращайся к человеку лично: «Ты — ...», «В тебе — ...»
- Тёплый, но не сентиментальный
- Глубокий, но понятный
- Образный, но конкретный
- Без технического жаргона (не «Юпитер в 11 доме», а «твоя сила — в сообществах»)

ЗАПРЕЩЕНО:
- Перечислять планеты и дома напрямую
- Использовать слова «аспект», «диспозитор», «дом», «градус»
- Писать «вам нужно», «следует развивать»
- Давать советы
- Предсказывать события

Выдай ровно 5 секций с маркерами. Ничего больше."""

        # Генерация
        try:
            interpretation = generate(prompt)
        except Exception as e:
            interpretation = "Интерпретация временно недоступна."

        # Сохраняем в JSON
        chart_json = json.dumps({
            "planets": chart.planets,
            "houses": chart.houses,
            "aspects": chart.aspects,
            "datetime": chart.datetime,
            "wheel": wheel_svg,
        }, default=str)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка построения натала: {e}")

    natal = db.query(NatalChart).filter(NatalChart.user_id == user.id).first()
    if not natal:
        natal = NatalChart(user_id=user.id)
        db.add(natal)

    natal.birth_year = data.birth_year
    natal.birth_month = data.birth_month
    natal.birth_day = data.birth_day
    natal.birth_hour = data.birth_hour
    natal.birth_minute = data.birth_minute
    natal.birth_lat = data.birth_lat
    natal.birth_lon = data.birth_lon
    natal.birth_city = data.birth_city
    natal.chart_data = chart_json
    natal.interpretation = interpretation

    db.commit()
    db.refresh(natal)

    return {
        "status": "ok",
        "has_natal": True,
        "wheel": wheel_svg,
        "interpretation": interpretation,
    }


@router.get("/natal")
def get_natal(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    natal = db.query(NatalChart).filter(NatalChart.user_id == user.id).first()
    if not natal:
        raise HTTPException(status_code=404, detail="Натал не сохранён")

    chart_data = json.loads(natal.chart_data or "{}")

    return {
        "birth_year": natal.birth_year,
        "birth_month": natal.birth_month,
        "birth_day": natal.birth_day,
        "birth_hour": natal.birth_hour,
        "birth_minute": natal.birth_minute,
        "birth_lat": natal.birth_lat,
        "birth_lon": natal.birth_lon,
        "birth_city": natal.birth_city,
        "chart_data": chart_data,
        "wheel": chart_data.get("wheel", ""),
        "interpretation": natal.interpretation or "",
    }
from fastapi import UploadFile, File
import shutil
import os

AVATAR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    # Проверяем тип файла
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Только изображения")

    # Ограничиваем размер (2 МБ)
    content = await file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Файл больше 2 МБ")

    # Сохраняем
    ext = file.filename.split(".")[-1].lower()
    filename = f"user_{user.id}.{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    # Обновляем user
    user.avatar_url = f"/static/avatars/{filename}"
    db.commit()

    return {"status": "ok", "avatar_url": user.avatar_url}


class UpdateProfileRequest(BaseModel):
    display_name: str


@router.post("/profile")
def update_profile(
    data: UpdateProfileRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    user.display_name = data.display_name.strip() or "Искатель"
    db.commit()
    return {"status": "ok", "display_name": user.display_name}


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    from core.auth import verify_password, hash_password

    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Неверный старый пароль")

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Пароль слишком короткий")

    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"status": "ok"}


@router.delete("/")
def delete_account(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    db.delete(user)
    db.commit()
    return {"status": "ok"}
