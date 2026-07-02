"""Configuration commune à tous les tests.

Définit les variables d'environnement AVANT que l'application ne soit importée :
  - une base SQLite dédiée aux tests (pas Neon),
  - des identifiants et une clé JWT factices.
Ainsi, la CI n'a besoin d'aucun secret réel pour exécuter les tests.
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("API_USERNAME", "admin")
os.environ.setdefault("API_PASSWORD", "secret123")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
