"""Endpoint de prédiction : prédit, puis journalise en base."""
import logging
import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.model import predict_one
from app.schemas import EmployeeInput, PredictionOutput
from db import models
from db.database import get_db

router = APIRouter(tags=["predictions"])
logger = logging.getLogger("uvicorn.error")


@router.post("/predict", response_model=PredictionOutput)
def predict(employee: EmployeeInput, db: Session = Depends(get_db)) -> PredictionOutput:
    """Prédit le risque de démission et journalise l'appel (prediction + monitoring)."""
    t0 = time.perf_counter()
    data = employee.model_dump()
    employee_id = data.pop("employee_id", None)   # champ optionnel, pas une feature

    result = predict_one(data)

    # Journalisation en base (sans casser la réponse si la base est indisponible)
    try:
        pred = models.Prediction(
            employee_id=employee_id,
            features=data,
            probabilite_demission=result["probabilite_demission"],
            prediction=result["prediction"],
            risque=result["risque"],
            seuil=result["seuil"],
        )
        db.add(pred)
        db.commit()
        db.refresh(pred)

        elapsed_ms = (time.perf_counter() - t0) * 1000
        db.add(models.MonitoringApplicatif(
            prediction_id=pred.id,
            endpoint="/predict",
            methode="POST",
            code_http=200,
            temps_reponse_ms=round(elapsed_ms, 2),
        ))
        db.commit()
    except Exception as exc:                       # noqa: BLE001
        db.rollback()
        logger.warning("Journalisation en base échouée : %s", exc)

    return PredictionOutput(**result)
