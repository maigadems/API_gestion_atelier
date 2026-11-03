"""Sécurité : hachage des mots de passe (Argon2) et jetons JWT.

RG21 : mots de passe hachés avec Argon2, jamais en clair, jamais renvoyés.
RG22 : jetons JWT signés avec date d'expiration.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

from app.core.config import settings

_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Retourne le hash Argon2 d'un mot de passe en clair."""
    return _hasher.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Vérifie un mot de passe en clair contre son hash Argon2."""
    try:
        return _hasher.verify(hashed, password)
    except (Argon2Error, ValueError, TypeError):
        return False


def create_access_token(subject: str | int) -> tuple[str, int]:
    """Crée un jeton JWT signé.

    Retourne (token, expires_in_secondes).
    """
    expire_minutes = settings.access_token_expire_minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {"sub": str(subject), "exp": expire}
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return token, expire_minutes * 60


def decode_token(token: str) -> dict | None:
    """Décode et vérifie un jeton JWT. Retourne la charge utile ou None."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError:
        return None
