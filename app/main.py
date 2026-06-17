"""Point d'entrée de l'API FastAPI.

Lancement local :
    uvicorn app.main:app --reload
Documentation interactive : http://localhost:8000/docs
"""
from fastapi import FastAPI

from app.config import settings

app = FastAPI(title=settings.api_title, version=settings.api_version)


@app.get("/health", tags=["monitoring"])
def health_check() -> dict:
    """Vérifie que l'API répond."""
    return {"status": "ok", "env": settings.app_env}


# TODO : app.include_router(predictions.router) une fois l'étape API faite
