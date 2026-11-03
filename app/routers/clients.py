"""Routeur des clients (routes 7 à 13)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.deps import get_current_user, require_admin
from app.enums import Genre
from app.schemas.client import (
    ClientCreate,
    ClientRead,
    ClientResume,
    ClientUpdate,
    CommandeMini,
)
from app.schemas.common import LIMIT_DEFAUT, LIMIT_MAX, Page
from app.services import client as service

router = APIRouter(
    prefix="/clients",
    tags=["clients"],
    dependencies=[Depends(get_current_user)],  # tout utilisateur connecté
)


@router.post("", response_model=ClientRead, status_code=status.HTTP_201_CREATED)
def creer_client(donnees: ClientCreate, db: Session = Depends(get_db)) -> ClientRead:
    client = service.creer(db, donnees)
    db.commit()
    db.refresh(client)
    return client


@router.get("", response_model=Page[ClientRead])
def lister_clients(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None, min_length=2),
    genre: Genre | None = None,
    limit: int = Query(default=LIMIT_DEFAUT, ge=1, le=LIMIT_MAX),
    offset: int = Query(default=0, ge=0),
) -> Page[ClientRead]:
    genre_val = genre.value if genre else None
    items, total = service.lister(db, q, genre_val, limit, offset)
    return Page[ClientRead](items=items, total=total, limit=limit, offset=offset)


@router.get("/{client_id}", response_model=ClientRead)
def detail_client(client_id: int, db: Session = Depends(get_db)) -> ClientRead:
    return service.get_ou_404(db, client_id)


@router.patch("/{client_id}", response_model=ClientRead)
def modifier_client(
    client_id: int, donnees: ClientUpdate, db: Session = Depends(get_db)
) -> ClientRead:
    client = service.get_ou_404(db, client_id)
    client = service.modifier(db, client, donnees)
    db.commit()
    db.refresh(client)
    return client


@router.delete(
    "/{client_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
def supprimer_client(client_id: int, db: Session = Depends(get_db)) -> None:
    client = service.get_ou_404(db, client_id)
    service.supprimer(db, client)
    db.commit()


@router.get("/{client_id}/commandes", response_model=Page[CommandeMini])
def commandes_du_client(
    client_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(default=LIMIT_DEFAUT, ge=1, le=LIMIT_MAX),
    offset: int = Query(default=0, ge=0),
) -> Page[CommandeMini]:
    client = service.get_ou_404(db, client_id)
    items, total = service.lister_commandes(db, client, limit, offset)
    return Page[CommandeMini](items=items, total=total, limit=limit, offset=offset)


@router.get("/{client_id}/resume", response_model=ClientResume)
def resume_client(client_id: int, db: Session = Depends(get_db)) -> ClientResume:
    client = service.get_ou_404(db, client_id)
    return service.resume(db, client)
