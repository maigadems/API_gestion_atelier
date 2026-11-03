"""Service de gestion du catalogue des prestations (TypeVetement)."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.catalogue import TypeVetement
from app.schemas.catalogue import TypeVetementCreate, TypeVetementUpdate


def get_ou_404(db: Session, type_id: int) -> TypeVetement:
    prestation = db.get(TypeVetement, type_id)
    if prestation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Prestation introuvable.")
    return prestation


def creer(db: Session, donnees: TypeVetementCreate) -> TypeVetement:
    existant = db.scalar(select(TypeVetement).where(TypeVetement.nom == donnees.nom))
    if existant is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Une prestation porte déjà ce nom."
        )
    prestation = TypeVetement(
        nom=donnees.nom,
        description=donnees.description,
        prix_base=donnees.prix_base,
        delai_jours=donnees.delai_jours,
        actif=True,
    )
    db.add(prestation)
    db.flush()
    return prestation


def lister(db: Session, actifs_seulement: bool) -> list[TypeVetement]:
    """Liste triée par nom. Par défaut, seules les prestations actives."""
    requete = select(TypeVetement)
    if actifs_seulement:
        requete = requete.where(TypeVetement.actif.is_(True))
    return list(db.scalars(requete.order_by(TypeVetement.nom)))


def modifier(
    db: Session, prestation: TypeVetement, donnees: TypeVetementUpdate
) -> TypeVetement:
    champs = donnees.model_dump(exclude_unset=True)

    if "nom" in champs and champs["nom"] != prestation.nom:
        existant = db.scalar(
            select(TypeVetement).where(TypeVetement.nom == champs["nom"])
        )
        if existant is not None:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Une prestation porte déjà ce nom."
            )

    for champ in ("nom", "description", "prix_base", "delai_jours", "actif"):
        if champ in champs:
            setattr(prestation, champ, champs[champ])

    db.flush()
    return prestation
