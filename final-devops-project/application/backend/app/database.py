"""Database configuration. No default passwords or implicit schema creation."""
import os
from pathlib import Path

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def database_url():
    if os.getenv("DATABASE_URL_FILE"):
        return Path(os.environ["DATABASE_URL_FILE"]).read_text().strip()
    if os.getenv("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    password_file = os.getenv("DB_PASSWORD_FILE")
    password = Path(password_file).read_text().strip() if password_file else os.getenv("DB_PASSWORD")
    if not password:
        raise RuntimeError("Set DATABASE_URL, DATABASE_URL_FILE, or DB_PASSWORD_FILE")
    return URL.create(
        "postgresql+psycopg", username=os.getenv("DB_USER", "taskboard"),
        password=password, host=os.getenv("DB_HOST", "postgres"),
        port=int(os.getenv("DB_PORT", "5432")), database=os.getenv("DB_NAME", "taskboard"),
    )


class Base(DeclarativeBase):
    pass


engine = create_engine(database_url(), pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    with SessionLocal() as session:
        yield session
