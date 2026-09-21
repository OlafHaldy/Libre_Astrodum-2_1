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
    """Создаёт все таблицы и делает простую миграцию."""
    from db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Простая миграция: добавить недостающие колонки
    import sqlite3
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверяем колонку interpretation в natal_charts
        cursor.execute("PRAGMA table_info(natal_charts)")
        columns = [row[1] for row in cursor.fetchall()]
        if "interpretation" not in columns:
            cursor.execute("ALTER TABLE natal_charts ADD COLUMN interpretation TEXT DEFAULT ''")
            conn.commit()
            print("[DB] Migration: added column interpretation to natal_charts")

        conn.close()
    except Exception as e:
        print(f"[DB] Migration warning: {e}")
