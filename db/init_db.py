"""Initialisation de la base : création des tables + ingestion du dataset.

Appelé au démarrage de l'API (Option B). Idempotent : ne recrée pas les
tables existantes et n'ingère le dataset que si la table est vide.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from db import models
from db.database import Base, SessionLocal, engine

REFERENCE_CSV = Path(__file__).resolve().parent.parent / "data" / "dataset_reference.csv"


def init_db() -> None:
    """Crée les 3 tables si elles n'existent pas encore."""
    Base.metadata.create_all(bind=engine)


def ingest_reference_if_empty() -> int:
    """Charge le dataset de référence dans la table `dataset` si elle est vide.

    Retourne le nombre de lignes ingérées (0 si déjà peuplée ou CSV absent).
    """
    if not REFERENCE_CSV.exists():
        return 0

    db = SessionLocal()
    try:
        if db.query(models.Dataset).first() is not None:
            return 0  # déjà peuplée → on ne fait rien

        df = pd.read_csv(REFERENCE_CSV)
        objets = [models.Dataset(**row) for row in df.to_dict(orient="records")]
        db.bulk_save_objects(objets)
        db.commit()
        return len(objets)
    finally:
        db.close()
