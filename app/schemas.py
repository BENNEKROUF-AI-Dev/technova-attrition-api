"""Schémas Pydantic : validation des entrées et format de sortie de /predict."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class EmployeeInput(BaseModel):
    """Données brutes d'un employé, telles qu'attendues par le modèle.

    Chaque champ est typé et validé. Les variables catégorielles n'acceptent
    que les modalités vues à l'entraînement (sinon l'API renvoie une erreur 422).
    """
    # ── SIRH ────────────────────────────────────────────────
    age: int = Field(..., ge=18, le=70, examples=[41])
    genre: Literal["F", "M"]
    revenu_mensuel: int = Field(..., ge=0, examples=[5993])
    statut_marital: Literal["Célibataire", "Divorcé(e)", "Marié(e)"]
    departement: Literal["Commercial", "Consulting", "Ressources Humaines"]
    poste: Literal[
        "Assistant de Direction", "Cadre Commercial", "Consultant",
        "Directeur Technique", "Manager", "Représentant Commercial",
        "Ressources Humaines", "Senior Manager", "Tech Lead",
    ]
    nombre_experiences_precedentes: int = Field(..., ge=0, examples=[8])
    annee_experience_totale: int = Field(..., ge=0, examples=[8])
    annees_dans_l_entreprise: int = Field(..., ge=0, examples=[6])
    annees_dans_le_poste_actuel: int = Field(..., ge=0, examples=[4])

    # ── Évaluations ─────────────────────────────────────────
    satisfaction_employee_environnement: int = Field(..., ge=1, le=4, examples=[2])
    note_evaluation_precedente: int = Field(..., ge=1, le=4, examples=[3])
    niveau_hierarchique_poste: int = Field(..., ge=1, le=5, examples=[2])
    satisfaction_employee_nature_travail: int = Field(..., ge=1, le=4, examples=[4])
    satisfaction_employee_equipe: int = Field(..., ge=1, le=4, examples=[1])
    satisfaction_employee_equilibre_pro_perso: int = Field(..., ge=1, le=4, examples=[1])
    note_evaluation_actuelle: int = Field(..., ge=1, le=4, examples=[3])
    heure_supplementaires: Literal["Oui", "Non"]
    augmentation_pct: float = Field(..., ge=0, le=100, examples=[11.0])

    # ── Sondage ─────────────────────────────────────────────
    nombre_participation_pee: int = Field(..., ge=0, examples=[0])
    nb_formations_suivies: int = Field(..., ge=0, examples=[0])
    distance_domicile_travail: int = Field(..., ge=0, examples=[1])
    niveau_education: int = Field(..., ge=1, le=5, examples=[2])
    domaine_etude: Literal[
        "Autre", "Entrepreunariat", "Infra & Cloud",
        "Marketing", "Ressources Humaines", "Transformation Digitale",
    ]
    frequence_deplacement: Literal["Aucun", "Occasionnel", "Frequent"]
    annees_depuis_la_derniere_promotion: int = Field(..., ge=0, examples=[0])
    annes_sous_responsable_actuel: int = Field(..., ge=0, examples=[5])


class PredictionOutput(BaseModel):
    """Réponse de l'API pour une prédiction."""
    probabilite_demission: float = Field(..., description="Probabilité estimée de démission (0 à 1).")
    prediction: int = Field(..., description="1 = risque de démission, 0 = pas de risque.")
    risque: bool = Field(..., description="True si la probabilité dépasse le seuil de décision.")
    seuil: float = Field(..., description="Seuil de décision appliqué.")
