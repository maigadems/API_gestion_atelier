"""Routeur d'authentification : /auth/login et /auth/me."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token
from app.deps import get_current_user
from app.models.utilisateur import Utilisateur
from app.schemas.auth import Token
from app.schemas.utilisateur import UtilisateurRead
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["authentification"])


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Connexion OAuth2 (username = e-mail, password).

    401 si identifiants incorrects ou compte désactivé (RG22, RG23).
    """
    utilisateur = auth_service.authentifier(db, form.username, form.password)
    if utilisateur is None or not utilisateur.actif:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Identifiants incorrects ou compte désactivé.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, expires_in = create_access_token(utilisateur.id)
    return Token(access_token=token, token_type="bearer", expires_in=expires_in)


@router.get("/me", response_model=UtilisateurRead)
def me(utilisateur: Utilisateur = Depends(get_current_user)) -> Utilisateur:
    """Profil de l'utilisateur connecté (sans donnée sensible)."""
    return utilisateur
