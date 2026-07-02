"""Endpoint d'authentification : délivre un jeton JWT."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.security import authenticate, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
    """Vérifie les identifiants et renvoie un jeton d'accès JWT."""
    if not authenticate(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=form_data.username)
    return {"access_token": access_token, "token_type": "bearer"}
