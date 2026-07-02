"""Tests du feature engineering (ml/features.py).

On teste les fonctions sur de petits DataFrames construits à la main, pour
vérifier le comportement attendu sans dépendre des vrais fichiers CSV.
"""
import numpy as np
import pandas as pd

from ml.features import (
    create_features,
    drop_correlated_features,
    encode_features,
)


def test_create_features_ajoute_les_colonnes_attendues():
    """create_features doit ajouter les 6 features métier."""
    df = pd.DataFrame({
        "satisfaction_employee_environnement": [2, 4],
        "satisfaction_employee_nature_travail": [3, 4],
        "satisfaction_employee_equipe": [1, 4],
        "satisfaction_employee_equilibre_pro_perso": [2, 4],
        "revenu_mensuel": [3000, 6000],
        "annees_dans_l_entreprise": [1, 9],
        "annees_depuis_la_derniere_promotion": [6, 2],
        "nombre_experiences_precedentes": [4, 1],
        "age": [30, 50],
        "distance_domicile_travail": [20, 5],
        "nb_formations_suivies": [0, 3],
    })
    out = create_features(df)
    for col in ["AvgSatisfaction", "IncomePerYear", "PromotionStagnation",
                "JobHopper", "LongCommute", "LowTraining"]:
        assert col in out.columns


def test_create_features_calculs_corrects():
    """Vérifie quelques valeurs calculées."""
    df = pd.DataFrame({
        "satisfaction_employee_environnement": [2],
        "satisfaction_employee_nature_travail": [2],
        "satisfaction_employee_equipe": [2],
        "satisfaction_employee_equilibre_pro_perso": [2],
        "revenu_mensuel": [6000],
        "annees_dans_l_entreprise": [2],
        "annees_depuis_la_derniere_promotion": [6],   # > 5 -> stagnation = 1
        "nombre_experiences_precedentes": [1],
        "age": [40],                                   # 1/40 = 0.025 < 0.3 -> JobHopper 0
        "distance_domicile_travail": [20],             # > 15 -> LongCommute 1
        "nb_formations_suivies": [1],                  # <= 1 -> LowTraining 1
    })
    out = create_features(df)
    assert out["AvgSatisfaction"].iloc[0] == 2.0
    assert out["IncomePerYear"].iloc[0] == 2000.0     # 6000 / (2+1)
    assert out["PromotionStagnation"].iloc[0] == 1
    assert out["JobHopper"].iloc[0] == 0
    assert out["LongCommute"].iloc[0] == 1
    assert out["LowTraining"].iloc[0] == 1


def test_encode_features_binaire_et_ordinal():
    """genre, heures sup. et fréquence de déplacement doivent être encodés en nombres."""
    df = pd.DataFrame({
        "genre": ["F", "M"],
        "heure_supplementaires": ["Non", "Oui"],
        "frequence_deplacement": ["Aucun", "Frequent"],
        "departement": ["Commercial", "Consulting"],
        "poste": ["Manager", "Consultant"],
        "statut_marital": ["Marié(e)", "Célibataire"],
        "domaine_etude": ["Marketing", "Autre"],
    })
    out = encode_features(df)
    assert out["genre"].tolist() == [0, 1]
    assert out["heure_supplementaires"].tolist() == [0, 1]
    assert out["frequence_deplacement"].tolist() == [0, 2]


def test_encode_features_one_hot():
    """Les colonnes nominales doivent être transformées en colonnes 0/1 (One-Hot)."""
    df = pd.DataFrame({
        "genre": ["F", "M"],
        "heure_supplementaires": ["Non", "Oui"],
        "frequence_deplacement": ["Aucun", "Occasionnel"],
        "departement": ["Commercial", "Consulting"],
        "poste": ["Manager", "Consultant"],
        "statut_marital": ["Marié(e)", "Célibataire"],
        "domaine_etude": ["Marketing", "Autre"],
    })
    out = encode_features(df)
    # Plus aucune colonne texte d'origine ne doit subsister
    assert "departement" not in out.columns
    # Au moins une colonne One-Hot doit apparaître (drop_first => 1 colonne pour 2 modalités)
    assert any(c.startswith("departement_") for c in out.columns)


def test_drop_correlated_features_supprime_une_colonne_redondante():
    """Deux colonnes quasi identiques : l'une des deux doit être supprimée."""
    n = 50
    rng = np.random.default_rng(0)
    base = rng.normal(size=n)
    df = pd.DataFrame({
        "a": base,
        "b": base + rng.normal(scale=0.001, size=n),  # quasi identique à 'a' -> |r| ~ 1
        "c": rng.normal(size=n),                       # indépendante
        "cible": rng.integers(0, 2, size=n),
    })
    out, dropped = drop_correlated_features(df, threshold=0.80)
    # Exactement une des deux colonnes corrélées doit être retirée
    assert len(dropped) == 1
    assert dropped[0] in ("a", "b")
    assert "c" in out.columns
