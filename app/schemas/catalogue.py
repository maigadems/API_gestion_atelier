"""Schémas Pydantic pour le catalogue des prestations (TypeVetement)."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TypeVetementCreate(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    description: str | None = None
    prix_base: int = Field(ge=0)  # FCFA
    delai_jours: int = Field(ge=0)


class TypeVetementUpdate(BaseModel):
    """Modification partielle."""

    nom: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    prix_base: int | None = Field(default=None, ge=0)
    delai_jours: int | None = Field(default=None, ge=0)
    actif: bool | None = None


class TypeVetementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    description: str | None
    prix_base: int
    delai_jours: int
    actif: bool
