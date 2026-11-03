"""Modèles Commande, LigneCommande, HistoriqueStatut.

La logique de gestion des commandes relève de la partie B (palier 2). Les
modèles sont définis ici pour compléter le schéma initial et alimenter les
routes du palier 1 (/clients/{id}/commandes et /clients/{id}/resume).
"""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import StatutCommande
from app.models.base import Base, utcnow

if TYPE_CHECKING:
    from app.models.client import Client


class Commande(Base):
    __tablename__ = "commandes"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id"), index=True, nullable=False
    )
    mesure_id: Mapped[int | None] = mapped_column(ForeignKey("mesures.id"), nullable=True)
    statut: Mapped[str] = mapped_column(
        String(20), nullable=False, default=StatutCommande.en_attente.value
    )
    date_commande: Mapped[date] = mapped_column(Date, nullable=False)
    date_livraison_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_livraison_reelle: Mapped[date | None] = mapped_column(Date, nullable=True)
    remise: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_paye: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cree_par_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateurs.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    client: Mapped["Client"] = relationship(back_populates="commandes")
    lignes: Mapped[list["LigneCommande"]] = relationship(
        back_populates="commande", cascade="all, delete-orphan"
    )
    historique: Mapped[list["HistoriqueStatut"]] = relationship(
        back_populates="commande", cascade="all, delete-orphan"
    )

    @property
    def solde(self) -> int:
        return self.montant_total - self.montant_paye


class LigneCommande(Base):
    __tablename__ = "lignes_commande"

    id: Mapped[int] = mapped_column(primary_key=True)
    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type_vetement_id: Mapped[int] = mapped_column(
        ForeignKey("types_vetement.id"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    quantite: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    prix_unitaire: Mapped[int] = mapped_column(Integer, nullable=False)

    commande: Mapped["Commande"] = relationship(back_populates="lignes")


class HistoriqueStatut(Base):
    __tablename__ = "historiques_statut"

    id: Mapped[int] = mapped_column(primary_key=True)
    commande_id: Mapped[int] = mapped_column(
        ForeignKey("commandes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    ancien_statut: Mapped[str | None] = mapped_column(String(20), nullable=True)
    nouveau_statut: Mapped[str] = mapped_column(String(20), nullable=False)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    utilisateur_id: Mapped[int | None] = mapped_column(
        ForeignKey("utilisateurs.id"), nullable=True
    )
    date_changement: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    commande: Mapped["Commande"] = relationship(back_populates="historique")
