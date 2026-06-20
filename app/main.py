"""Point d'entrée de l'API FastAPI.

Lancement local :
    uvicorn app.main:app --reload
Documentation interactive : http://localhost:8000/docs
"""
from fastapi import FastAPI

from app.routers import predictions

app = FastAPI(
    title="TechNova Attrition API",
    version="1.0.0",
    description="Prédit le risque de démission d'un employé à partir de ses données RH.",
)

app.include_router(predictions.router)


@app.get("/health", tags=["monitoring"])
def health_check() -> dict:
    """Vérifie que l'API répond."""
    return {"status": "ok"}
