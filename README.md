---
title: TechNova Attrition API
emoji: 📉
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# TechNova Attrition API

Déploiement en production d'un modèle de Machine Learning de **prédiction de l'attrition** (probabilité de démission d'un employé), pour le client **Futurisys** / **TechNova Partners**.

Le modèle est exposé via une API REST (FastAPI), testée (Pytest), versionnée (Git), adossée à une base PostgreSQL et déployée via un pipeline CI/CD.

> **État du projet :** étape 1 — mise en place du dépôt et de la structure. Les briques API, tests, base de données et CI/CD sont présentes sous forme de squelette et seront implémentées aux étapes suivantes.

---

## Table des matières

1. [Présentation](#présentation)
2. [Architecture du projet](#architecture-du-projet)
3. [Installation](#installation)
4. [Utilisation](#utilisation)
5. [Déploiement](#déploiement)
6. [Authentification](#authentification)
7. [Sécurisation](#sécurisation)
8. [Tests](#tests)
9. [Conventions Git](#conventions-git)

---

## Présentation

Le modèle, issu du projet d'analyse d'attrition, prend en entrée les caractéristiques d'un employé (données SIRH, évaluations de performance, réponses au sondage interne) et renvoie une **probabilité de démission**. L'objectif de ce projet est de rendre ce modèle **utilisable en production** via une API performante, fiable et sécurisée, dans le respect des bonnes pratiques d'ingénierie logicielle.

**Stack technique :** Python · FastAPI · scikit-learn · PostgreSQL · Pytest · GitHub Actions.

## Architecture du projet

```
technova-attrition-api/
├── app/                    # Code de l'API FastAPI
│   ├── main.py             # Point d'entrée (création de l'app, routes)
│   ├── config.py           # Configuration via variables d'environnement
│   ├── schemas.py          # Schémas Pydantic (entrée / sortie)
│   ├── model.py            # Chargement du modèle + prédiction
│   ├── security.py         # Authentification (JWT)
│   └── routers/            # Endpoints regroupés par domaine
├── ml/                     # Code Machine Learning
│   ├── features.py         # Feature engineering (partagé entraînement/API)
│   └── train.py            # Entraînement + sérialisation du modèle
├── db/                     # Base de données
│   ├── schema.sql          # Définition des tables
│   └── create_db.py        # Script de création de la base
├── tests/                  # Tests unitaires et fonctionnels (Pytest)
├── models/                 # Artefacts de modèles entraînés (non versionnés)
├── docs/                   # Documentation (schéma de données, etc.)
├── .github/workflows/      # Pipelines CI/CD (GitHub Actions)
├── requirements.txt        # Dépendances Python
├── .env.example            # Modèle de configuration (à copier en .env)
└── .gitignore
```

## Installation

**Prérequis :** Python 3.11+, PostgreSQL, Git.

```bash
# 1. Cloner le dépôt
git clone <url-du-depot>
cd technova-attrition-api

# 2. Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env             # puis renseigner vos valeurs
```

## Utilisation

```bash
# Lancer l'API en local
uvicorn app.main:app --reload
```

- API : `http://localhost:8000`
- Documentation interactive (Swagger / OpenAPI) : `http://localhost:8000/docs`
- Vérification de l'état : `GET /health`

> L'endpoint de prédiction (`POST /predict`) et les schémas de données seront documentés ici une fois l'étape API réalisée.

## Déploiement

Le déploiement est automatisé via GitHub Actions (voir `.github/workflows/`). Le pipeline gère les environnements **dev / test / prod** et la **gestion des secrets**.

> Procédure de déploiement détaillée à compléter à l'étape CI/CD.

## Authentification

L'accès aux endpoints sensibles est protégé par **JWT** (JSON Web Token). Un client s'authentifie pour obtenir un token, qu'il joint ensuite à ses requêtes via l'en-tête `Authorization: Bearer <token>`.

> Détails (obtention du token, durée de validité) à compléter à l'étape API/sécurité.

## Sécurisation

- Les secrets (clé JWT, identifiants de base de données) ne sont **jamais** versionnés : ils passent par le `.env` local (ignoré par Git) et par les **GitHub Secrets** en CI/CD.
- Les entrées de l'API sont validées par Pydantic (typage strict, rejet des données malformées).
- Les communications doivent passer par HTTPS en production.

## Tests

```bash
# Lancer la suite de tests
pytest

# Avec rapport de couverture
pytest --cov=app --cov=ml --cov-report=term-missing
```

## Conventions Git

Voir [`CONTRIBUTING.md`](CONTRIBUTING.md) pour le détail des conventions de **branches**, de **commits** et de **tags**.
