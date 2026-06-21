"""Modèles des 3 tables (SQLAlchemy ORM) avec clés primaires et étrangères.

Relations :
    dataset  1 ──< prediction          (via prediction.employee_id → dataset.employee_id)
    prediction 1 ──< monitoring_applicatif (via monitoring.prediction_id → prediction.id)
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Dataset(Base):
    """Données de référence du Projet 4 (3 fichiers joints)."""
    __tablename__ = "dataset"

    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True)  # 🔑 clé primaire
    age: Mapped[int] = mapped_column(Integer)
    genre: Mapped[str] = mapped_column(String)
    revenu_mensuel: Mapped[int] = mapped_column(Integer)
    statut_marital: Mapped[str] = mapped_column(String)
    departement: Mapped[str] = mapped_column(String)
    poste: Mapped[str] = mapped_column(String)
    nombre_experiences_precedentes: Mapped[int] = mapped_column(Integer)
    annee_experience_totale: Mapped[int] = mapped_column(Integer)
    annees_dans_l_entreprise: Mapped[int] = mapped_column(Integer)
    annees_dans_le_poste_actuel: Mapped[int] = mapped_column(Integer)
    satisfaction_employee_environnement: Mapped[int] = mapped_column(Integer)
    note_evaluation_precedente: Mapped[int] = mapped_column(Integer)
    niveau_hierarchique_poste: Mapped[int] = mapped_column(Integer)
    satisfaction_employee_nature_travail: Mapped[int] = mapped_column(Integer)
    satisfaction_employee_equipe: Mapped[int] = mapped_column(Integer)
    satisfaction_employee_equilibre_pro_perso: Mapped[int] = mapped_column(Integer)
    note_evaluation_actuelle: Mapped[int] = mapped_column(Integer)
    heure_supplementaires: Mapped[str] = mapped_column(String)
    augmentation_pct: Mapped[float] = mapped_column(Float)
    a_quitte_l_entreprise: Mapped[str] = mapped_column(String)
    nombre_participation_pee: Mapped[int] = mapped_column(Integer)
    nb_formations_suivies: Mapped[int] = mapped_column(Integer)
    distance_domicile_travail: Mapped[int] = mapped_column(Integer)
    niveau_education: Mapped[int] = mapped_column(Integer)
    domaine_etude: Mapped[str] = mapped_column(String)
    frequence_deplacement: Mapped[str] = mapped_column(String)
    annees_depuis_la_derniere_promotion: Mapped[int] = mapped_column(Integer)
    annes_sous_responsable_actuel: Mapped[int] = mapped_column(Integer)
    cible: Mapped[int] = mapped_column(Integer)  # 1 = a quitté, 0 = est resté

    predictions = relationship("Prediction", back_populates="employe")


class Prediction(Base):
    """Une prédiction faite par l'API (features d'entrée + résultat du modèle)."""
    __tablename__ = "prediction"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 🔑
    # 🔗 clé étrangère vers dataset (nullable : l'employé n'est pas toujours connu)
    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("dataset.employee_id"), nullable=True
    )
    features: Mapped[dict] = mapped_column(JSON)  # le payload d'entrée complet
    probabilite_demission: Mapped[float] = mapped_column(Float)
    prediction: Mapped[int] = mapped_column(Integer)
    risque: Mapped[bool] = mapped_column(Boolean)
    seuil: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    employe = relationship("Dataset", back_populates="predictions")
    monitoring = relationship("MonitoringApplicatif", back_populates="prediction")


class MonitoringApplicatif(Base):
    """Métriques techniques d'un appel à l'API (temps de réponse, code HTTP)."""
    __tablename__ = "monitoring_applicatif"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # 🔑
    # 🔗 clé étrangère vers prediction
    prediction_id: Mapped[int | None] = mapped_column(
        ForeignKey("prediction.id"), nullable=True
    )
    endpoint: Mapped[str] = mapped_column(String)
    methode: Mapped[str] = mapped_column(String)
    code_http: Mapped[int] = mapped_column(Integer)
    temps_reponse_ms: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    prediction = relationship("Prediction", back_populates="monitoring")
