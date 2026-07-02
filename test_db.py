"""Tests d'intégration de la base (SQLite de test, configurée dans conftest.py).

Vérifie qu'un appel /predict :
  - écrit une ligne dans `prediction`,
  - écrit une ligne dans `monitoring_applicatif`,
  - relie les deux par la clé étrangère prediction_id.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from db import models
from db.database import SessionLocal
from tests.test_api import EMPLOYE_VALIDE


@pytest.fixture(scope="module")
def client():
    """Le gestionnaire de contexte déclenche le lifespan (création des tables)."""
    with TestClient(app) as c:
        yield c


def _token(client) -> dict:
    r = client.post("/token", data={"username": "admin", "password": "secret123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_predict_ecrit_une_prediction_en_base(client):
    avant = SessionLocal().query(models.Prediction).count()
    r = client.post("/predict", json=EMPLOYE_VALIDE, headers=_token(client))
    assert r.status_code == 200
    apres = SessionLocal().query(models.Prediction).count()
    assert apres == avant + 1


def test_predict_ecrit_le_monitoring(client):
    avant = SessionLocal().query(models.MonitoringApplicatif).count()
    client.post("/predict", json=EMPLOYE_VALIDE, headers=_token(client))
    apres = SessionLocal().query(models.MonitoringApplicatif).count()
    assert apres == avant + 1


def test_monitoring_relie_a_la_prediction(client):
    client.post("/predict", json=EMPLOYE_VALIDE, headers=_token(client))
    db = SessionLocal()
    derniere = db.query(models.Prediction).order_by(models.Prediction.id.desc()).first()
    assert derniere is not None
    assert len(derniere.monitoring) >= 1
    mon = derniere.monitoring[0]
    assert mon.prediction_id == derniere.id
    assert mon.code_http == 200
    assert mon.temps_reponse_ms >= 0


def test_valeurs_prediction_coherentes(client):
    client.post("/predict", json=EMPLOYE_VALIDE, headers=_token(client))
    db = SessionLocal()
    p = db.query(models.Prediction).order_by(models.Prediction.id.desc()).first()
    assert 0.0 <= p.probabilite_demission <= 1.0
    assert p.prediction in (0, 1)
    assert isinstance(p.features, dict)
