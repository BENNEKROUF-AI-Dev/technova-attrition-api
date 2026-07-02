"""Authentification JWT (flux OAuth2 « password »).

Un utilisateur d'API unique (identifiant + mot de passe) est lu depuis des
variables d'environnement (secrets). À la connexion, l'API délivre un jeton
JWT signé ; les endpoints protégés exigent ensuite ce jeton.

Aucun mot de passe n'est stocké dans le code : tout vient de l'environnement.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from secrets import compare_digest

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# ── Configuration (depuis les secrets / variables d'environnement) ──────
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-a-changer-en-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "changeme")

# Indique à FastAPI où récupérer le jeton (endpoint /token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate(username: str, password: str) -> bool:
    """Vérifie l'identifiant et le mot de passe (comparaison à temps constant)."""
    user_ok = compare_digest(username, API_USERNAME)
    pwd_ok = compare_digest(password, API_PASSWORD)
    return user_ok and pwd_ok


def create_access_token(subject: str) -> str:
    """Génère un JWT signé contenant le sujet (l'identifiant) et une expiration."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """Dépendance FastAPI : valide le jeton et renvoie l'identifiant, sinon 401."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc
    return username
