"""Modèle Mesure (prise de mesures d'un client).

Les 18 mesures sont facultatives et exprimées en centimètres.
Les routes de gestion des mesures relèvent de la partie B (palier 2) ; le
modèle est défini ici pour que le schéma initial Alembic soit complet.
"""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.client import Client

# Les 18 mesures facultatives en cm (ordre de l'énoncé).
MESURE_CHAMPS = (
    "taille_cm",
    "tour_cou",
    "carrure_dos",
    "longueur_epaule",
    "tour_poitrine",
    "tour_taille",
    "tour_bassin",
    "longueur_manche",
    "tour_bras",
    "tour_poignet",
    "longueur_dos",
    "longueur_haut",
    "longueur_pantalon",
    "tour_cuisse",
    "tour_genou",
    "bas_pantalon",
    "entrejambe",
    "longueur_robe",
)


class Mesure(Base):
    __tablename__ = "mesures"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("clients.id", ondelete="CASCADE"), index=True, nullable=False
    )
    date_prise: Mapped[date] = mapped_column(Date, nullable=False)
    prise_par_id: Mapped[int | None] = mapped_column(
        ForeignKey("utilisateurs.id"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    taille_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_cou: Mapped[float | None] = mapped_column(Float, nullable=True)
    carrure_dos: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_epaule: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_poitrine: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_taille: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_bassin: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_manche: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_bras: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_poignet: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_dos: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_haut: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_pantalon: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_cuisse: Mapped[float | None] = mapped_column(Float, nullable=True)
    tour_genou: Mapped[float | None] = mapped_column(Float, nullable=True)
    bas_pantalon: Mapped[float | None] = mapped_column(Float, nullable=True)
    entrejambe: Mapped[float | None] = mapped_column(Float, nullable=True)
    longueur_robe: Mapped[float | None] = mapped_column(Float, nullable=True)

    client: Mapped["Client"] = relationship(back_populates="mesures")
