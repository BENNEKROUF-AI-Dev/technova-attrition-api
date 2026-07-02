"""Tests de l'API (Pytest + TestClient)."""
import os

os.environ.setdefault("API_USERNAME", "admin")
os.environ.setdefault("API_PASSWORD", "secret123")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)

EMPLOYE_VALIDE = {
    "age": 41, "genre": "F", "revenu_mensuel": 5993, "statut_marital": "Célibataire",
    "departement": "Commercial", "poste": "Cadre Commercial",
    "nombre_experiences_precedentes": 8, "annee_experience_totale": 8,
    "annees_dans_l_entreprise": 6, "annees_dans_le_poste_actuel": 4,
    "satisfaction_employee_environnement": 2, "note_evaluation_precedente": 3,
    "niveau_hierarchique_poste": 2, "satisfaction_employee_nature_travail": 4,
    "satisfaction_employee_equipe": 1, "satisfaction_employee_equilibre_pro_perso": 1,
    "note_evaluation_actuelle": 3, "heure_supplementaires": "Oui", "augmentation_pct": 11.0,
    "nombre_participation_pee": 0, "nb_formations_suivies": 0, "distance_domicile_travail": 1,
    "niveau_education": 2, "domaine_etude": "Infra & Cloud",
    "frequence_deplacement": "Occasionnel", "annees_depuis_la_derniere_promotion": 0,
    "annes_sous_responsable_actuel": 5,
}


def _auth_headers() -> dict:
    r = client.post("/token", data={"username": "admin", "password": "secret123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_employe_valide():
    response = client.post("/predict", json=EMPLOYE_VALIDE, headers=_auth_headers())
    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body["probabilite_demission"] <= 1.0
    assert body["prediction"] in (0, 1)
    assert isinstance(body["risque"], bool)


def test_predict_categorie_invalide():
    mauvais = dict(EMPLOYE_VALIDE, genre="X")
    response = client.post("/predict", json=mauvais, headers=_auth_headers())
    assert response.status_code == 422


def test_predict_champ_manquant():
    incomplet = dict(EMPLOYE_VALIDE)
    del incomplet["age"]
    response = client.post("/predict", json=incomplet, headers=_auth_headers())
    assert response.status_code == 422


def test_predict_valeur_hors_bornes():
    hors = dict(EMPLOYE_VALIDE, satisfaction_employee_equipe=9)
    response = client.post("/predict", json=hors, headers=_auth_headers())
    assert response.status_code == 422
