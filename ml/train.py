"""
Entraînement du modèle d'attrition et export de l'artefact .joblib.

Reproduit fidèlement le modèle final des notebooks :
    Régression Logistique (C=0.1) + SMOTE, sur features mises à l'échelle.

Pipeline : 3 CSV -> jointure/features/encodage -> X, y
           -> split stratifié -> StandardScaler (fit train)
           -> SMOTE (train) -> LogisticRegression(C=0.1).fit

L'artefact sauvegardé contient TOUT ce dont l'API a besoin pour prédire
exactement comme à l'entraînement :
    model, scaler, cont_cols, feature_columns, threshold, metadata

Usage :
    python ml/train.py
    python ml/train.py --data-dir data --out models/attrition_model.joblib
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import sklearn
from imblearn.over_sampling import SMOTE
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score, classification_report, confusion_matrix, f1_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from features import build_xy

RANDOM_STATE = 42
TEST_SIZE = 0.2
THRESHOLD = 0.5  # seuil de décision retenu dans le notebook (predict standard)


def main() -> None:
    parser = argparse.ArgumentParser(description="Entraîne et exporte le modèle d'attrition.")
    parser.add_argument("--data-dir", default="data",
                        help="Dossier contenant les 3 CSV (défaut: data).")
    parser.add_argument("--out", default="models/attrition_model.joblib",
                        help="Chemin de sortie de l'artefact (défaut: models/attrition_model.joblib).")
    args = parser.parse_args()

    data = Path(args.data_dir)
    sirh = str(data / "extrait_sirh.csv")
    eval_ = str(data / "extrait_eval.csv")
    sondage = str(data / "extrait_sondage.csv")

    # ── 1. Préparation des données (jointure + features + encodage + décorrélation)
    print("→ Construction de X, y depuis les 3 CSV...")
    X, y, dropped = build_xy(sirh, eval_, sondage)
    print(f"  X = {X.shape} | y = {y.shape} | taux démission = {y.mean()*100:.1f}%")
    print(f"  Features décorrélées supprimées : {dropped}")

    # ── 2. Colonnes continues (à scaler) vs binaires (inchangées)
    binary_cols = [c for c in X.columns if X[c].nunique() <= 2]
    cont_cols = [c for c in X.columns if c not in binary_cols]
    print(f"  Continues : {len(cont_cols)} | Binaires : {len(binary_cols)}")

    # ── 3. Split stratifié AVANT le scaling (évite le data leakage)
    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y)

    # ── 4. Scaling : fit sur TRAIN uniquement, transform train + test
    scaler = StandardScaler()
    X_train = X_train_raw.copy()
    X_test = X_test_raw.copy()
    X_train[cont_cols] = scaler.fit_transform(X_train_raw[cont_cols])
    X_test[cont_cols] = scaler.transform(X_test_raw[cont_cols])

    # ── 5. SMOTE sur le TRAIN uniquement
    X_sm, y_sm = SMOTE(random_state=RANDOM_STATE).fit_resample(X_train, y_train)
    print(f"  Après SMOTE : {len(X_train)} -> {len(X_sm)} lignes d'entraînement")

    # ── 6. Modèle final : Régression Logistique (C=0.1)
    model = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE, C=0.1)
    model.fit(X_sm, y_sm)

    # ── 7. Évaluation (doit reproduire les chiffres du notebook)
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= THRESHOLD).astype(int)
    cm = confusion_matrix(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    aucpr = average_precision_score(y_test, y_proba)
    n_pos = int(y_test.sum())

    print("\n" + "=" * 56)
    print("MODÈLE FINAL — LogReg (C=0.1) + SMOTE")
    print("=" * 56)
    print(classification_report(y_test, y_pred, target_names=["Reste", "Part"], zero_division=0))
    print(f"F1 = {f1:.3f} | Rappel = {recall:.3f} | AUC-PR = {aucpr:.3f}")
    print(f"-> {cm[1, 1]} démissionnaires détectés sur {n_pos} ({cm[1, 1]/n_pos*100:.1f}%)")

    # ── 8. Export de l'artefact (tout ce que l'API doit charger)
    artifact = {
        "model": model,
        "scaler": scaler,
        "cont_cols": cont_cols,
        "feature_columns": list(X.columns),
        "threshold": THRESHOLD,
        "metadata": {
            "model_type": "LogisticRegression(C=0.1) + SMOTE",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "sklearn_version": sklearn.__version__,
            "n_features": X.shape[1],
            "dropped_correlated": dropped,
            "test_metrics": {
                "f1": round(float(f1), 4),
                "recall": round(float(recall), 4),
                "auc_pr": round(float(aucpr), 4),
                "true_positives": int(cm[1, 1]),
                "positives_total": n_pos,
            },
        },
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, out)
    print(f"\n✅ Artefact sauvegardé : {out}  ({out.stat().st_size/1024:.1f} Ko)")
    print("   Contenu :", ", ".join(artifact.keys()))
    print("   Métadonnées :", json.dumps(artifact["metadata"]["test_metrics"]))


if __name__ == "__main__":
    main()
