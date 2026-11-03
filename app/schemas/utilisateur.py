"""Schémas Pydantic pour les utilisateurs.

Un schéma distinct pour la création, la modification et la lecture.
Le hash du mot de passe n'est jamais exposé (RG21).
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.enums import Role


class UtilisateurCreate(BaseModel):
    email: EmailStr
    nom_complet: str = Field(min_length=1, max_length=255)
    mot_de_passe: str = Field(min_length=8, max_length=128)  # RG21 : min 8 caractères
    role: Role


class UtilisateurUpdate(BaseModel):
    """Modification partielle : seuls les champs envoyés sont changés."""

    nom_complet: str | None = Field(default=None, min_length=1, max_length=255)
    role: Role | None = None
    actif: bool | None = None
    mot_de_passe: str | None = Field(default=None, min_length=8, max_length=128)


class UtilisateurRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nom_complet: str
    role: Role
    actif: bool
    created_at: datetime
