"""Schémas Pydantic pour les clients."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.enums import Genre, StatutCommande
from app.utils import normaliser_telephone


class ClientCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=255)
    prenom: str = Field(min_length=1, max_length=255)
    telephone: str
    email: EmailStr | None = None
    adresse: str | None = None
    genre: Genre | None = None
    notes: str | None = None

    @field_validator("telephone")
    @classmethod
    def _normaliser_tel(cls, v: str) -> str:
        return normaliser_telephone(v)


class ClientUpdate(BaseModel):
    """Modification partielle. nom, prenom et telephone ne peuvent pas être vidés."""

    nom: str | None = Field(default=None, min_length=1, max_length=255)
    prenom: str | None = Field(default=None, min_length=1, max_length=255)
    telephone: str | None = None
    email: EmailStr | None = None
    adresse: str | None = None
    genre: Genre | None = None
    notes: str | None = None

    @field_validator("telephone")
    @classmethod
    def _normaliser_tel(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return normaliser_telephone(v)


class ClientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    prenom: str
    telephone: str
    email: str | None
    adresse: str | None
    genre: Genre | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class CommandeMini(BaseModel):
    """Vue allégée d'une commande pour la liste des commandes d'un client."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    statut: StatutCommande
    date_commande: date
    date_livraison_prevue: date | None
    montant_total: int
    montant_paye: int
    solde: int


class ClientResume(BaseModel):
    """Résumé d'activité d'un client (commandes annulées exclues)."""

    nb_commandes: int
    chiffre_affaires: int
    total_paye: int
    solde_du: int
    derniere_commande: date | None
    a_des_mesures: bool
