"""Configuration centralisée, chargée depuis les variables d'environnement.

Aucune valeur secrète n'est codée en dur : tout passe par le `.env`
(non versionné) ou par les secrets du pipeline CI/CD.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "dev"
    api_title: str = "TechNova Attrition API"
    api_version: str = "0.1.0"

    secret_key: str = "changez-moi"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    database_url: str = "postgresql+psycopg2://user:pwd@localhost:5432/attrition"
    model_path: str = "models/attrition_model.joblib"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
