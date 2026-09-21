# ==========================================
# Liber Astrodum - Auth files
# ==========================================

Write-Host "Creating folders..." -ForegroundColor Cyan

New-Item -ItemType Directory -Force -Path "db" | Out-Null
New-Item -ItemType Directory -Force -Path "api" | Out-Null

# db/__init__.py
Set-Content -Path "db\__init__.py" -Value "" -Encoding UTF8

# db/database.py
@'
"""
Liber Astrodum - db/database.py
SQLite with WAL optimizations.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "liber.db")

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
    },
    echo=False,
    pool_pre_ping=True,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
'@ | Set-Content -Path "db\database.py" -Encoding UTF8

# db/models.py
@'
"""
Liber Astrodum - db/models.py
User and NatalChart models.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    natal_chart = relationship(
        "NatalChart",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class NatalChart(Base):
    __tablename__ = "natal_charts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    birth_year = Column(Integer, nullable=False)
    birth_month = Column(Integer, nullable=False)
    birth_day = Column(Integer, nullable=False)
    birth_hour = Column(Integer, default=12)
    birth_minute = Column(Integer, default=0)
    birth_lat = Column(Float, nullable=False)
    birth_lon = Column(Float, nullable=False)
    birth_city = Column(String, default="")

    chart_data = Column(Text, default="{}")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="natal_chart")
'@ | Set-Content -Path "db\models.py" -Encoding UTF8

# api/__init__.py
Set-Content -Path "api\__init__.py" -Value "" -Encoding UTF8

# core/auth.py
@'
"""
Liber Astrodum - core/auth.py
JWT authentication.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "liber-astrodum-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        return None


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    user_id = decode_token(token)
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def require_user(user: Optional[User] = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Auth required",
        )
    return user
'@ | Set-Content -Path "core\auth.py" -Encoding UTF8

# api/auth_routes.py
@'
"""
Liber Astrodum - api/auth_routes.py
Registration and login.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import User
from core.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password too short")

    user = User(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "email": user.email}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "email": user.email}
'@ | Set-Content -Path "api\auth_routes.py" -Encoding UTF8

# api/me_routes.py
@'
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
'@ | Set-Content -Path "api\me_routes.py" -Encoding UTF8

Write-Host ""
Write-Host "DONE!" -ForegroundColor Green
Write-Host "Created: db/, api/, core/auth.py"