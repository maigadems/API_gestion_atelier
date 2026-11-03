"""Service de gestion des utilisateurs (comptes du personnel)."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.enums import Role
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurUpdate


def get_ou_404(db: Session, utilisateur_id: int) -> Utilisateur:
    utilisateur = db.get(Utilisateur, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Utilisateur introuvable.")
    return utilisateur


def lister(db: Session) -> list[Utilisateur]:
    """Liste des comptes, triés par nom complet."""
    return list(db.scalars(select(Utilisateur).order_by(Utilisateur.nom_complet)))


def creer(db: Session, donnees: UtilisateurCreate) -> Utilisateur:
    existant = db.scalar(select(Utilisateur).where(Utilisateur.email == donnees.email))
    if existant is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Cet e-mail est déjà utilisé.")
    utilisateur = Utilisateur(
        email=donnees.email,
        nom_complet=donnees.nom_complet,
        mot_de_passe_hash=hash_password(donnees.mot_de_passe),
        role=donnees.role.value,
        actif=True,
    )
    db.add(utilisateur)
    db.flush()
    return utilisateur


def modifier(
    db: Session,
    cible: Utilisateur,
    donnees: UtilisateurUpdate,
    acteur: Utilisateur,
) -> Utilisateur:
    """Modifie nom, rôle, état actif ou mot de passe.

    RG24 : un administrateur ne peut ni se désactiver lui-même ni retirer son
    propre rôle d'administrateur.
    """
    champs = donnees.model_dump(exclude_unset=True)

    if cible.id == acteur.id:
        if "actif" in champs and champs["actif"] is False:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Un administrateur ne peut pas se désactiver lui-même.",
            )
        if "role" in champs and champs["role"] != Role.admin:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Un administrateur ne peut pas retirer son propre rôle d'administrateur.",
            )

    if "nom_complet" in champs:
        cible.nom_complet = champs["nom_complet"]
    if "role" in champs:
        role = champs["role"]
        cible.role = role.value if isinstance(role, Role) else role
    if "actif" in champs:
        cible.actif = champs["actif"]
    if "mot_de_passe" in champs:
        cible.mot_de_passe_hash = hash_password(champs["mot_de_passe"])

    db.flush()
    return cible
