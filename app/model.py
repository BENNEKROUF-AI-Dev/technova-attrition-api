"""Chargement du modèle (une seule fois) et fonction de prédiction.

L'artefact .joblib contient le modèle, le scaler, l'ordre des colonnes et le
seuil. On le charge une fois au démarrage du module (pas à chaque requête).
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pandas as pd

# Permet d'importer ml/features.py quel que soit le répertoire de lancement
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ml"))
from features import prepare_for_inference  # noqa: E402

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "attrition_model.joblib"

# ── Chargement unique au démarrage ──────────────────────────
_artifact = joblib.load(MODEL_PATH)
_model = _artifact["model"]
_scaler = _artifact["scaler"]
_feature_columns = _artifact["feature_columns"]
_cont_cols = _artifact["cont_cols"]
_threshold = _artifact["threshold"]


def get_metadata() -> dict:
    """Métadonnées du modèle chargé (pour un éventuel endpoint d'info)."""
    return _artifact.get("metadata", {})


def predict_one(employee: dict) -> dict:
    """Prédit le risque de démission pour un employé (dict de champs bruts)."""
    df_raw = pd.DataFrame([employee])
    X = prepare_for_inference(df_raw, _feature_columns, _cont_cols, _scaler)
    proba = float(_model.predict_proba(X)[:, 1][0])
    is_risk = proba >= _threshold
    return {
        "probabilite_demission": round(proba, 4),
        "prediction": int(is_risk),
        "risque": bool(is_risk),
        "seuil": _threshold,
    }
