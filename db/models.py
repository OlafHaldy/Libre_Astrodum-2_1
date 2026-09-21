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
    display_name = Column(String, default="Искатель")
    avatar_url = Column(String, default="")
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
class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chart_type = Column(String, nullable=False)   # "lunar", "solar", "daily"
    target_year = Column(Integer, nullable=False)
    target_month = Column(Integer, nullable=True)
    target_day = Column(Integer, nullable=True)
    title = Column(String, default="")
    interpretation = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
