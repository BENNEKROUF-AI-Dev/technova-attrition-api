"""
Feature engineering du projet 4 (attrition TechNova).

Transcription fidèle des notebooks 1 et 2 (jointure, nettoyage, création de
features, encodage, décorrélation). Ces fonctions sont utilisées À L'IDENTIQUE
à l'entraînement (ml/train.py) et à l'inférence (l'API /predict), pour éviter
tout décalage entre entraînement et production (training/serving skew).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# Colonnes qualitatives encodées en One-Hot (3+ modalités sans ordre)
NOMINAL_COLS = ["departement", "poste", "statut_marital", "domaine_etude"]

# Colonnes supprimées au nettoyage (variance nulle / doublon)
COLS_TO_DROP = [
    "nombre_heures_travailless",            # toujours 80
    "nombre_employee_sous_responsabilite",  # toujours 1
    "ayant_enfants",                        # toujours 'Y'
    "code_sondage",                         # doublon de id_employee
]

EXCLUDE = ["id_employee", "cible", "a_quitte_l_entreprise"]


# ──────────────────────────────────────────────────────────────────────
#  1. Jointure des 3 sources
# ──────────────────────────────────────────────────────────────────────
def load_and_merge(path_sirh: str, path_eval: str, path_sondage: str) -> pd.DataFrame:
    """Charge les 3 CSV et les assemble (jointure INNER sur id_employee)."""
    sirh = pd.read_csv(path_sirh)
    eval_ = pd.read_csv(path_eval)
    sondage = pd.read_csv(path_sondage)

    # eval_number "E_42" -> 42
    eval_["id_employee"] = eval_["eval_number"].str.extract(r"E_(\d+)").astype(int)
    # "11 %" -> 11.0
    eval_["augmentation_pct"] = (
        eval_["augementation_salaire_precedente"]
        .str.replace("%", "", regex=False).str.strip().astype(float)
    )

    df = (
        sirh
        .merge(
            eval_.drop(columns=["eval_number", "augementation_salaire_precedente"]),
            on="id_employee", how="inner",
        )
        .merge(sondage, left_on="id_employee", right_on="code_sondage", how="inner")
    )
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Supprime les colonnes inutiles et crée la cible binaire."""
    df = df.drop(columns=COLS_TO_DROP)
    df["cible"] = df["a_quitte_l_entreprise"].map({"Oui": 1, "Non": 0})
    return df


# ──────────────────────────────────────────────────────────────────────
#  2. Création des features métier
# ──────────────────────────────────────────────────────────────────────
def create_features(df: pd.DataFrame) -> pd.DataFrame:
    sat_cols = [
        "satisfaction_employee_environnement",
        "satisfaction_employee_nature_travail",
        "satisfaction_employee_equipe",
        "satisfaction_employee_equilibre_pro_perso",
    ]
    df["AvgSatisfaction"] = df[sat_cols].mean(axis=1).round(2)
    df["IncomePerYear"] = (df["revenu_mensuel"] / (df["annees_dans_l_entreprise"] + 1)).round(0)
    df["PromotionStagnation"] = (df["annees_depuis_la_derniere_promotion"] > 5).astype(int)
    df["JobHopper"] = ((df["nombre_experiences_precedentes"] / df["age"]) > 0.3).astype(int)
    df["LongCommute"] = (df["distance_domicile_travail"] > 15).astype(int)
    df["LowTraining"] = (df["nb_formations_suivies"] <= 1).astype(int)
    return df


# ──────────────────────────────────────────────────────────────────────
#  3. Encodage des variables qualitatives
# ──────────────────────────────────────────────────────────────────────
def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    df["genre"] = df["genre"].map({"F": 0, "M": 1})
    df["heure_supplementaires"] = df["heure_supplementaires"].map({"Non": 0, "Oui": 1})
    df["frequence_deplacement"] = df["frequence_deplacement"].map(
        {"Aucun": 0, "Occasionnel": 1, "Frequent": 2}
    )
    df = pd.get_dummies(df, columns=NOMINAL_COLS, drop_first=True, dtype=int)
    return df


# ──────────────────────────────────────────────────────────────────────
#  4. Suppression des features trop corrélées (|r| > 0.80)
# ──────────────────────────────────────────────────────────────────────
def drop_correlated_features(df: pd.DataFrame, target_col: str = "cible",
                             threshold: float = 0.80) -> tuple:
    ohe = [c for c in df.columns if any(c.startswith(p) for p in
           ["poste_", "departement_", "statut_marital_", "domaine_etude_"])]
    cont = df.select_dtypes("number").columns.difference(EXCLUDE + ohe)
    corr = df[cont].corr().abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    corr_target = df[cont].corrwith(df[target_col]).abs()
    to_drop = []
    for col in upper.columns:
        for partner in upper.index[upper[col] > threshold].tolist():
            loser = col if corr_target.get(col, 0) < corr_target.get(partner, 0) else partner
            if loser not in to_drop:
                to_drop.append(loser)
    return df.drop(columns=to_drop), to_drop


def get_X_y(df: pd.DataFrame) -> tuple:
    """Retourne X (toutes features numériques) et y (cible binaire)."""
    X = df.drop(columns=EXCLUDE, errors="ignore").astype(float)
    y = df["cible"]
    return X, y


# ──────────────────────────────────────────────────────────────────────
#  Pipeline complet (entraînement) : des 3 CSV à X, y
# ──────────────────────────────────────────────────────────────────────
def build_xy(path_sirh: str, path_eval: str, path_sondage: str,
             threshold: float = 0.80) -> tuple:
    df = load_and_merge(path_sirh, path_eval, path_sondage)
    df = clean_data(df)
    df = create_features(df)
    df = encode_features(df)
    df, dropped = drop_correlated_features(df, threshold=threshold)
    X, y = get_X_y(df)
    return X, y, dropped


# ──────────────────────────────────────────────────────────────────────
#  Inférence : prépare des données brutes pour le modèle déjà entraîné
#  (utilisé par l'API /predict). Aligne les colonnes et applique le scaler.
# ──────────────────────────────────────────────────────────────────────
def prepare_for_inference(df_raw: pd.DataFrame, feature_columns: list,
                          cont_cols: list, scaler) -> pd.DataFrame:
    """
    df_raw : données brutes déjà jointes (mêmes colonnes que les 3 sources
             fusionnées), SANS la cible.
    Applique create_features + encode_features, réaligne sur l'ordre exact
    des colonnes du modèle (colonnes manquantes = 0), puis applique le scaler.
    """
    df = df_raw.copy()
    df = create_features(df)
    df = encode_features(df)
    # Réaligne : ajoute les colonnes OHE absentes (=0) et ordonne comme à l'entraînement
    df = df.reindex(columns=feature_columns, fill_value=0).astype(float)
    df[cont_cols] = scaler.transform(df[cont_cols])
    return df
