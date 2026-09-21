"""
Liber Astrodum
api/prediction_routes.py

История прогнозов пользователя (Архив искателя).
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from db.database import get_db
from db.models import User, Prediction
from core.auth import require_user

router = APIRouter(prefix="/api/v1/me/predictions", tags=["predictions"])


class SavePredictionRequest(BaseModel):
    chart_type: str            # "lunar", "solar", "daily"
    target_year: int
    target_month: Optional[int] = None
    target_day: Optional[int] = None
    title: str = ""
    interpretation: str


@router.get("/")
def list_predictions(
    chart_type: Optional[str] = None,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    query = db.query(Prediction).filter(Prediction.user_id == user.id)
    if chart_type:
        query = query.filter(Prediction.chart_type == chart_type)
    items = query.order_by(Prediction.created_at.desc()).all()

    return [
        {
            "id": p.id,
            "chart_type": p.chart_type,
            "target_year": p.target_year,
            "target_month": p.target_month,
            "target_day": p.target_day,
            "title": p.title or "Прогноз",
            "created_at": p.created_at.strftime("%d.%m.%Y") if p.created_at else "",
        }
        for p in items
    ]


@router.post("/")
def save_prediction(
    data: SavePredictionRequest,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    prediction = Prediction(
        user_id=user.id,
        chart_type=data.chart_type,
        target_year=data.target_year,
        target_month=data.target_month,
        target_day=data.target_day,
        title=data.title or "Прогноз",
        interpretation=data.interpretation,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return {"status": "ok", "id": prediction.id}


@router.get("/{prediction_id}")
def get_prediction(
    prediction_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    p = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == user.id,
    ).first()

    if not p:
        raise HTTPException(status_code=404, detail="Прогноз не найден")

    return {
        "id": p.id,
        "chart_type": p.chart_type,
        "target_year": p.target_year,
        "target_month": p.target_month,
        "target_day": p.target_day,
        "title": p.title,
        "interpretation": p.interpretation,
        "created_at": p.created_at.strftime("%d.%m.%Y") if p.created_at else "",
    }


@router.delete("/{prediction_id}")
def delete_prediction(
    prediction_id: int,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    p = db.query(Prediction).filter(
        Prediction.id == prediction_id,
        Prediction.user_id == user.id,
    ).first()

    if not p:
        raise HTTPException(status_code=404, detail="Прогноз не найден")

    db.delete(p)
    db.commit()
    return {"status": "ok"}