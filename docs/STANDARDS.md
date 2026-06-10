# Standards de code & d'expérimentation ML

Ce document définit les conventions à respecter pour contribuer au projet. Il complète les conventions Git décrites dans `CONTRIBUTING.md`.

## 1. Standards de code

- **Style** : code formaté et vérifié avec **ruff** (configuration dans `pyproject.toml`). Toute Pull Request doit passer `ruff check .` sans erreur.
- **Python** : version 3.11. Typage des signatures de fonctions encouragé (annotations de type).
- **Nommage** : `snake_case` pour les variables et fonctions, `PascalCase` pour les classes, constantes en `MAJUSCULES`.
- **Docstrings** : chaque module et chaque fonction publique est documenté (rôle, entrées, sorties).
- **Imports** : triés automatiquement (règle `I` de ruff), pas d'imports inutilisés.
- **Secrets** : aucune valeur sensible dans le code. Tout passe par les variables d'environnement (`.env` en local, GitHub Secrets en CI/CD).

## 2. Standards de tests

- Framework : **pytest**. Les tests vivent dans `tests/`.
- Chaque endpoint de l'API et chaque fonction de transformation de données critique doit être couvert, y compris les **cas d'erreur** (entrée invalide, valeur manquante).
- La **couverture** est mesurée à chaque exécution (`pytest --cov`). Objectif indicatif : viser une couverture significative du code métier (`app/`, `ml/`).
- Un test ne doit pas dépendre d'un service externe (base, Space) : on isole via des données factices ou des *mocks*.

## 3. Standards d'expérimentation ML

- **Reproductibilité** : toute expérimentation fixe une graine aléatoire (`random_state=42`) et documente la version des données utilisées.
- **Séparation des données** : `train_test_split` stratifié sur la cible ; le jeu de test ne sert jamais à l'entraînement ni au réglage.
- **Pré-traitement partagé** : le feature engineering vit dans `ml/features.py` et est utilisé **à l'identique** à l'entraînement et à l'inférence, pour éviter tout décalage (*training/serving skew*).
- **Choix de modèle** : justifié par des métriques adaptées au déséquilibre des classes (F1, rappel, AUC-PR) plutôt que la seule accuracy.
- **Artefacts** : les modèles entraînés (`.joblib`) ne sont pas versionnés dans Git (cf. `.gitignore`) ; ils sont régénérables via `ml/train.py`.

## 4. Workflow de contribution

1. Créer une branche `feature/*` depuis `develop`.
2. Développer + écrire les tests.
3. Ouvrir une Pull Request : la **CI doit être verte** (lint + tests) avant toute fusion.
4. Fusionner dans `develop`, puis dans `main` pour déclencher le déploiement (CD) vers le Space Hugging Face.
