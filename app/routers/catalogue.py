"""Routeur du catalogue des prestations (routes 14 à 17)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user, require_admin
from app.schemas.catalogue import (
    TypeVetementCreate,
    TypeVetementRead,
    TypeVetementUpdate,
)
from app.services import catalogue as service

router = APIRouter(
    prefix="/catalogue",
    tags=["catalogue"],
    dependencies=[Depends(get_current_user)],
)


@router.post(
    "",
    response_model=TypeVetementRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def creer_prestation(
    donnees: TypeVetementCreate, db: Session = Depends(get_db)
) -> TypeVetementRead:
    prestation = service.creer(db, donnees)
    db.commit()
    db.refresh(prestation)
    return prestation


@router.get("", response_model=list[TypeVetementRead])
def lister_prestations(
    db: Session = Depends(get_db),
    actifs_seulement: bool = Query(default=True),
) -> list[TypeVetementRead]:
    return service.lister(db, actifs_seulement)


@router.get("/{type_id}", response_model=TypeVetementRead)
def detail_prestation(type_id: int, db: Session = Depends(get_db)) -> TypeVetementRead:
    return service.get_ou_404(db, type_id)


@router.patch(
    "/{type_id}",
    response_model=TypeVetementRead,
    dependencies=[Depends(require_admin)],
)
def modifier_prestation(
    type_id: int, donnees: TypeVetementUpdate, db: Session = Depends(get_db)
) -> TypeVetementRead:
    prestation = service.get_ou_404(db, type_id)
    prestation = service.modifier(db, prestation, donnees)
    db.commit()
    db.refresh(prestation)
    return prestation
