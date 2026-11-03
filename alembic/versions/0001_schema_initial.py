"""Schéma initial complet de l'atelier de couture.

Revision ID: 0001_schema_initial
Revises:
Create Date: 2026-11-03
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_schema_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "utilisateurs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("nom_complet", sa.String(length=255), nullable=False),
        sa.Column("mot_de_passe_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_utilisateurs_email", "utilisateurs", ["email"], unique=True)

    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(length=255), nullable=False),
        sa.Column("prenom", sa.String(length=255), nullable=False),
        sa.Column("telephone", sa.String(length=25), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("adresse", sa.Text(), nullable=True),
        sa.Column("genre", sa.String(length=10), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_clients_telephone", "clients", ["telephone"], unique=True)

    op.create_table(
        "types_vetement",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("prix_base", sa.Integer(), nullable=False),
        sa.Column("delai_jours", sa.Integer(), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_types_vetement_nom", "types_vetement", ["nom"], unique=True)

    op.create_table(
        "mesures",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "client_id",
            sa.Integer(),
            sa.ForeignKey("clients.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("date_prise", sa.Date(), nullable=False),
        sa.Column(
            "prise_par_id",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.id"),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("taille_cm", sa.Float(), nullable=True),
        sa.Column("tour_cou", sa.Float(), nullable=True),
        sa.Column("carrure_dos", sa.Float(), nullable=True),
        sa.Column("longueur_epaule", sa.Float(), nullable=True),
        sa.Column("tour_poitrine", sa.Float(), nullable=True),
        sa.Column("tour_taille", sa.Float(), nullable=True),
        sa.Column("tour_bassin", sa.Float(), nullable=True),
        sa.Column("longueur_manche", sa.Float(), nullable=True),
        sa.Column("tour_bras", sa.Float(), nullable=True),
        sa.Column("tour_poignet", sa.Float(), nullable=True),
        sa.Column("longueur_dos", sa.Float(), nullable=True),
        sa.Column("longueur_haut", sa.Float(), nullable=True),
        sa.Column("longueur_pantalon", sa.Float(), nullable=True),
        sa.Column("tour_cuisse", sa.Float(), nullable=True),
        sa.Column("tour_genou", sa.Float(), nullable=True),
        sa.Column("bas_pantalon", sa.Float(), nullable=True),
        sa.Column("entrejambe", sa.Float(), nullable=True),
        sa.Column("longueur_robe", sa.Float(), nullable=True),
    )
    op.create_index("ix_mesures_client_id", "mesures", ["client_id"])

    op.create_table(
        "commandes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("numero", sa.String(length=20), nullable=False),
        sa.Column(
            "client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False
        ),
        sa.Column(
            "mesure_id", sa.Integer(), sa.ForeignKey("mesures.id"), nullable=True
        ),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("date_commande", sa.Date(), nullable=False),
        sa.Column("date_livraison_prevue", sa.Date(), nullable=True),
        sa.Column("date_livraison_reelle", sa.Date(), nullable=True),
        sa.Column("remise", sa.Integer(), nullable=False),
        sa.Column("montant_total", sa.Integer(), nullable=False),
        sa.Column("montant_paye", sa.Integer(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "cree_par_id", sa.Integer(), sa.ForeignKey("utilisateurs.id"), nullable=True
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_commandes_numero", "commandes", ["numero"], unique=True)
    op.create_index("ix_commandes_client_id", "commandes", ["client_id"])

    op.create_table(
        "lignes_commande",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "commande_id",
            sa.Integer(),
            sa.ForeignKey("commandes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "type_vetement_id",
            sa.Integer(),
            sa.ForeignKey("types_vetement.id"),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantite", sa.Integer(), nullable=False),
        sa.Column("prix_unitaire", sa.Integer(), nullable=False),
    )
    op.create_index("ix_lignes_commande_commande_id", "lignes_commande", ["commande_id"])

    op.create_table(
        "historiques_statut",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "commande_id",
            sa.Integer(),
            sa.ForeignKey("commandes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ancien_statut", sa.String(length=20), nullable=True),
        sa.Column("nouveau_statut", sa.String(length=20), nullable=False),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column(
            "utilisateur_id",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.id"),
            nullable=True,
        ),
        sa.Column("date_changement", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_historiques_statut_commande_id", "historiques_statut", ["commande_id"]
    )

    op.create_table(
        "paiements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "commande_id",
            sa.Integer(),
            sa.ForeignKey("commandes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("montant", sa.Integer(), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("date_paiement", sa.Date(), nullable=False),
        sa.Column(
            "enregistre_par_id",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.id"),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_paiements_commande_id", "paiements", ["commande_id"])

    op.create_table(
        "livraisons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "commande_id",
            sa.Integer(),
            sa.ForeignKey("commandes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("adresse", sa.Text(), nullable=True),
        sa.Column("livreur", sa.String(length=255), nullable=True),
        sa.Column("date_prevue", sa.Date(), nullable=True),
        sa.Column("date_effective", sa.Date(), nullable=True),
        sa.Column("statut", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_livraisons_commande_id", "livraisons", ["commande_id"], unique=True
    )


def downgrade() -> None:
    op.drop_table("livraisons")
    op.drop_table("paiements")
    op.drop_table("historiques_statut")
    op.drop_table("lignes_commande")
    op.drop_table("commandes")
    op.drop_table("mesures")
    op.drop_table("types_vetement")
    op.drop_table("clients")
    op.drop_table("utilisateurs")
