"""Routeur des utilisateurs (réservé à l'administrateur)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import require_admin
from app.models.utilisateur import Utilisateur
from app.schemas.utilisateur import UtilisateurCreate, UtilisateurRead, UtilisateurUpdate
from app.services import utilisateur as service

router = APIRouter(prefix="/utilisateurs", tags=["utilisateurs"])


@router.post(
    "",
    response_model=UtilisateurRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def creer_utilisateur(
    donnees: UtilisateurCreate,
    db: Session = Depends(get_db),
) -> Utilisateur:
    utilisateur = service.creer(db, donnees)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur


@router.get(
    "",
    response_model=list[UtilisateurRead],
    dependencies=[Depends(require_admin)],
)
def lister_utilisateurs(db: Session = Depends(get_db)) -> list[Utilisateur]:
    return service.lister(db)


@router.get(
    "/{utilisateur_id}",
    response_model=UtilisateurRead,
    dependencies=[Depends(require_admin)],
)
def detail_utilisateur(
    utilisateur_id: int,
    db: Session = Depends(get_db),
) -> Utilisateur:
    return service.get_ou_404(db, utilisateur_id)


@router.patch("/{utilisateur_id}", response_model=UtilisateurRead)
def modifier_utilisateur(
    utilisateur_id: int,
    donnees: UtilisateurUpdate,
    db: Session = Depends(get_db),
    acteur: Utilisateur = Depends(require_admin),
) -> Utilisateur:
    cible = service.get_ou_404(db, utilisateur_id)
    utilisateur = service.modifier(db, cible, donnees, acteur)
    db.commit()
    db.refresh(utilisateur)
    return utilisateur
