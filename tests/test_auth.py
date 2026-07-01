"""Tests de l'authentification JWT."""
import os

os.environ.setdefault("API_USERNAME", "admin")
os.environ.setdefault("API_PASSWORD", "secret123")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from tests.test_api import EMPLOYE_VALIDE  # noqa: E402

client = TestClient(app)


def _token() -> str:
    r = client.post("/token", data={"username": "admin", "password": "secret123"})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_token_identifiants_valides():
    r = client.post("/token", data={"username": "admin", "password": "secret123"})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"
    assert "access_token" in r.json()


def test_token_identifiants_invalides():
    r = client.post("/token", data={"username": "admin", "password": "mauvais"})
    assert r.status_code == 401


def test_predict_sans_jeton_refuse():
    """Sans jeton, /predict doit renvoyer 401."""
    r = client.post("/predict", json=EMPLOYE_VALIDE)
    assert r.status_code == 401


def test_predict_avec_jeton_ok():
    """Avec un jeton valide, /predict fonctionne."""
    headers = {"Authorization": f"Bearer {_token()}"}
    r = client.post("/predict", json=EMPLOYE_VALIDE, headers=headers)
    assert r.status_code == 200
    assert 0.0 <= r.json()["probabilite_demission"] <= 1.0


def test_predict_jeton_invalide_refuse():
    headers = {"Authorization": "Bearer jeton.bidon.invalide"}
    r = client.post("/predict", json=EMPLOYE_VALIDE, headers=headers)
    assert r.status_code == 401
