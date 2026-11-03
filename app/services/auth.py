"""Service d'authentification."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.utilisateur import Utilisateur


def get_par_email(db: Session, email: str) -> Utilisateur | None:
    return db.scalar(select(Utilisateur).where(Utilisateur.email == email))


def authentifier(db: Session, email: str, mot_de_passe: str) -> Utilisateur | None:
    """Vérifie les identifiants.

    Retourne l'utilisateur si e-mail connu ET mot de passe correct, sinon None
    (RG23 : même issue que l'e-mail soit inconnu ou le mot de passe faux).
    La vérification du compte actif est faite par l'appelant (RG22).
    """
    utilisateur = get_par_email(db, email)
    if utilisateur is None:
        return None
    if not verify_password(mot_de_passe, utilisateur.mot_de_passe_hash):
        return None
    return utilisateur
