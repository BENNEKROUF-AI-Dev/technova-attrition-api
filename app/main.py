"""Point d'entrée de l'API FastAPI.

Au démarrage : création des tables et ingestion du dataset de référence.
Authentification JWT : se connecter via /token pour obtenir un jeton, puis
l'utiliser pour appeler /predict.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import auth, predictions
from db.init_db import ingest_reference_if_empty, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    ingest_reference_if_empty()
    yield


app = FastAPI(
    title="TechNova Attrition API",
    version="1.2.0",
    description="Prédit le risque de démission d'un employé (accès protégé par JWT).",
    lifespan=lifespan,
)

app.include_router(auth.router)
app.include_router(predictions.router)


@app.get("/health", tags=["monitoring"])
def health_check() -> dict:
    """Vérifie que l'API répond (public, non protégé)."""
    return {"status": "ok"}
