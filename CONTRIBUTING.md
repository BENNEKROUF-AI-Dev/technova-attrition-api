# Conventions de contribution

Ces conventions garantissent un historique clair, une collaboration fluide et une gestion de versions traçable — exactement ce qui est attendu à l'étape 1.

## Branches

| Branche          | Rôle                                                      |
| ---------------- | --------------------------------------------------------- |
| `main`           | Code stable, prêt pour la production. Chaque release y est *taguée*. |
| `develop`        | Branche d'intégration où sont fusionnées les fonctionnalités. |
| `feature/<nom>`  | Une branche par fonctionnalité, créée depuis `develop`.   |

**Nommage des branches de fonctionnalité** (en minuscules, mots séparés par des tirets) :

```
feature/api-fastapi
feature/tests-pytest
feature/database-postgresql
feature/auth-jwt
feature/ci-cd
fix/<description>        # correction de bug
docs/<description>       # documentation seule
```

Workflow : `feature/*` → fusionnée dans `develop` (via Pull Request) → `develop` fusionnée dans `main` pour une release.

## Commits

On suit la convention **Conventional Commits** : `type: description courte à l'impératif`.

| Type      | Usage                                            |
| --------- | ------------------------------------------------ |
| `feat`    | Nouvelle fonctionnalité                          |
| `fix`     | Correction de bug                                |
| `docs`    | Documentation                                    |
| `test`    | Ajout ou modification de tests                   |
| `refactor`| Refactorisation sans changement de comportement  |
| `chore`   | Tâches diverses (config, dépendances)            |
| `ci`      | Pipeline d'intégration / déploiement             |

Exemples :

```
feat: ajoute l'endpoint POST /predict
fix: corrige le mapping de la variable genre
test: couvre les cas d'erreur du feature engineering
docs: complète la section déploiement du README
chore: initialise la structure du projet
```

Règles : un commit = un changement cohérent ; message au présent de l'impératif ; pas de commit « wip » ou « divers » sur `main`.

## Tags (versionnage sémantique)

On utilise le **SemVer** : `vMAJEUR.MINEUR.CORRECTIF`.

- `MAJEUR` : changement incompatible (ex. modification du contrat de l'API)
- `MINEUR` : nouvelle fonctionnalité rétrocompatible
- `CORRECTIF` : correction de bug rétrocompatible

```bash
git tag -a v0.1.0 -m "Structure initiale du projet (étape 1)"
git push origin v0.1.0
```
