"""Connexion à la base de données (SQLAlchemy).

L'URL de connexion vient de la variable d'environnement DATABASE_URL
(secret côté Hugging Face). En local/CI sans variable, on retombe sur une
base SQLite pour pouvoir tester sans Neon.
"""
from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./technova.db")

# Neon fournit un préfixe "postgresql://" ; SQLAlchemy + psycopg2 attend
# "postgresql+psycopg2://". On normalise automatiquement.
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    """Dépendance FastAPI : fournit une session de base et la ferme après usage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
