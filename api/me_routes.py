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
        "has_natal": user.natal_chart is not None,
    }


@router.post("/natal")
def save_natal(
    data: NatalData,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    from builders.natal_builder import build_natal_chart

    try:
        chart = build_natal_chart(
            data.birth_year, data.birth_month, data.birth_day,
            data.birth_hour, data.birth_minute,
            data.birth_lat, data.birth_lon,
        )
        chart_json = json.dumps({
            "planets": chart.planets,
            "houses": chart.houses,
            "aspects": chart.aspects,
            "datetime": chart.datetime,
        }, default=str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Natal build error: {e}")

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

    db.commit()
    db.refresh(natal)

    return {"status": "ok", "has_natal": True}


@router.get("/natal")
def get_natal(
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    natal = db.query(NatalChart).filter(NatalChart.user_id == user.id).first()
    if not natal:
        raise HTTPException(status_code=404, detail="Natal not saved")

    return {
        "birth_year": natal.birth_year,
        "birth_month": natal.birth_month,
        "birth_day": natal.birth_day,
        "birth_hour": natal.birth_hour,
        "birth_minute": natal.birth_minute,
        "birth_lat": natal.birth_lat,
        "birth_lon": natal.birth_lon,
        "birth_city": natal.birth_city,
        "chart_data": json.loads(natal.chart_data or "{}"),
    }
