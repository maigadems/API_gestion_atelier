"""Dépendances FastAPI : authentification et contrôle des rôles."""
from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.enums import Role
from app.models.utilisateur import Utilisateur

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")

_401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Jeton manquant, invalide ou expiré.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Utilisateur:
    """Récupère l'utilisateur connecté à partir du jeton JWT.

    401 si le jeton est absent/invalide/expiré ou si le compte est désactivé
    (RG22 : un compte désactivé est refusé même avec un jeton encore valide).
    """
    payload = decode_token(token)
    if payload is None:
        raise _401
    sub = payload.get("sub")
    if sub is None:
        raise _401
    try:
        utilisateur = db.get(Utilisateur, int(sub))
    except (TypeError, ValueError):
        raise _401
    if utilisateur is None or not utilisateur.actif:
        raise _401
    return utilisateur


def require_roles(*roles: Role) -> Callable[..., Utilisateur]:
    """Fabrique une dépendance qui exige l'un des rôles donnés (403 sinon)."""
    autorises = {r.value for r in roles}

    def _verifier(
        utilisateur: Utilisateur = Depends(get_current_user),
    ) -> Utilisateur:
        if utilisateur.role not in autorises:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Votre rôle ne permet pas cette action.",
            )
        return utilisateur

    return _verifier


# Raccourcis fréquents.
require_admin = require_roles(Role.admin)
