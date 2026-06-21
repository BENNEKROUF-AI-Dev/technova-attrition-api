"""Point d'entrée de l'API FastAPI.

Au démarrage : création des tables et ingestion du dataset de référence
(si la base est vide). Lancement local : uvicorn app.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import predictions
from db.init_db import ingest_reference_if_empty, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()                      # crée les 3 tables si besoin
    ingest_reference_if_empty()    # peuple `dataset` au premier démarrage
    yield


app = FastAPI(
    title="TechNova Attrition API",
    version="1.1.0",
    description="Prédit le risque de démission d'un employé et journalise les appels.",
    lifespan=lifespan,
)

app.include_router(predictions.router)


@app.get("/health", tags=["monitoring"])
def health_check() -> dict:
    """Vérifie que l'API répond."""
    return {"status": "ok"}
