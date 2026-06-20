"""Endpoint de prédiction."""
from fastapi import APIRouter

from app.model import predict_one
from app.schemas import EmployeeInput, PredictionOutput

router = APIRouter(tags=["predictions"])


@router.post("/predict", response_model=PredictionOutput)
def predict(employee: EmployeeInput) -> PredictionOutput:
    """Prédit le risque de démission d'un employé à partir de ses données."""
    result = predict_one(employee.model_dump())
    return PredictionOutput(**result)
