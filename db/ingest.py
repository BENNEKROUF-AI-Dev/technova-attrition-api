"""Script autonome d'ingestion du dataset de référence dans la table `dataset`.

Usage : python db/ingest.py
(L'API ingère aussi automatiquement au premier démarrage ; ce script permet
de le faire manuellement ou de ré-ingérer après une remise à zéro.)
"""
from db.init_db import ingest_reference_if_empty, init_db

if __name__ == "__main__":
    init_db()
    n = ingest_reference_if_empty()
    print(f"Tables prêtes. Lignes ingérées dans `dataset` : {n}")
