import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Por defecto SQLite. Ejemplo PostgreSQL:
# postgresql+psycopg2://user:pass@localhost:5432/votaciones
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./votaciones.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
