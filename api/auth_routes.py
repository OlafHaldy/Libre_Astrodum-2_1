"""
Liber Astrodum
api/auth_routes.py

Регистрация и вход с логированием.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import logging

from db.database import get_db
from db.models import User
from core.auth import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    logger.info(f"REGISTER attempt: {data.email}")

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        logger.warning(f"REGISTER failed: email exists {data.email}")
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Пароль слишком короткий")

    try:
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"REGISTER success: user_id={user.id}, email={user.email}")
    except Exception as e:
        logger.error(f"REGISTER error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания пользователя: {e}")

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "email": user.email}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"LOGIN attempt: {data.email}")

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        logger.warning(f"LOGIN failed: user not found {data.email}")
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not verify_password(data.password, user.password_hash):
        logger.warning(f"LOGIN failed: wrong password for {data.email}")
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    logger.info(f"LOGIN success: user_id={user.id}")
    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "email": user.email}