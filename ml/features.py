"""
Feature engineering du projet 4 (attrition TechNova).

Ces fonctions sont reprises du notebook d'analyse (Partie 1) afin que
l'entraînement du modèle ET l'API de prédiction appliquent EXACTEMENT
les mêmes transformations. C'est la garantie qu'une donnée envoyée à
l'API est traitée comme à l'entraînement.
"""
from __future__ import annotations

import pandas as pd


SATISFACTION_COLS = [
    "satisfaction_employee_environnement",
    "satisfaction_employee_nature_travail",
    "satisfaction_employee_equipe",
    "satisfaction_employee_equilibre_pro_perso",
]

NOMINAL_COLS = ["departement", "poste", "statut_marital", "domaine_etude"]


def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """Crée les features métier dérivées."""
    df = df.copy()

    df["AvgSatisfaction"] = df[SATISFACTION_COLS].mean(axis=1).round(2)
    df["IncomePerYear"] = (
        df["revenu_mensuel"] / (df["annees_dans_l_entreprise"] + 1)
    ).round(0)
    df["PromotionStagnation"] = (
        df["annees_depuis_la_derniere_promotion"] > 5
    ).astype(int)
    df["JobHopper"] = (
        (df["nombre_experiences_precedentes"] / df["age"]) > 0.3
    ).astype(int)
    df["LongCommute"] = (df["distance_domicile_travail"] > 15).astype(int)
    df["LowTraining"] = (df["nb_formations_suivies"] <= 1).astype(int)

    return df


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    """Encode les variables qualitatives selon leur sens métier."""
    df = df.copy()

    df["genre"] = df["genre"].map({"F": 0, "M": 1})
    df["heure_supplementaires"] = df["heure_supplementaires"].map({"Non": 0, "Oui": 1})

    freq_order = {"Aucun": 0, "Occasionnel": 1, "Frequent": 2}
    df["frequence_deplacement"] = df["frequence_deplacement"].map(freq_order)

    df = pd.get_dummies(df, columns=NOMINAL_COLS, drop_first=True, dtype=int)
    return df


def build_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Applique l'ensemble du pré-traitement à un DataFrame brut joint."""
    df = create_features(df)
    df = encode_features(df)
    return df


# TODO (étapes suivantes) :
#   - drop_correlated_features() et get_X_y() pour l'entraînement
#   - figer la liste finale des colonnes du modèle (ordre des features)
