"""Modèle Livraison (partie B — défini ici pour compléter le schéma)."""
from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import StatutLivraison
from app.models.base import Base


class Livraison(Base):
    __tablename__ = "livraisons"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Une seule livraison par commande.
    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    # mode : retrait_atelier | domicile
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    adresse: Mapped[str | None] = mapped_column(Text, nullable=True)
    livreur: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_effective: Mapped[date | None] = mapped_column(Date, nullable=True)
    # statut : planifiee | livree
    statut: Mapped[str] = mapped_column(
        String(20), nullable=False, default=StatutLivraison.planifiee.value
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
