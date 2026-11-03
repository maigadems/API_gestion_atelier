"""Service de gestion des clients."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.enums import StatutCommande
from app.models.client import Client
from app.models.commande import Commande
from app.models.mesure import Mesure
from app.schemas.client import ClientCreate, ClientResume, ClientUpdate


def get_ou_404(db: Session, client_id: int) -> Client:
    client = db.get(Client, client_id)
    if client is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client introuvable.")
    return client


def _telephone_pris(db: Session, telephone: str, sauf_id: int | None = None) -> bool:
    requete = select(Client.id).where(Client.telephone == telephone)
    if sauf_id is not None:
        requete = requete.where(Client.id != sauf_id)
    return db.scalar(requete) is not None


def creer(db: Session, donnees: ClientCreate) -> Client:
    # RG1 : le téléphone (déjà normalisé par le schéma) identifie le client.
    if _telephone_pris(db, donnees.telephone):
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Un client avec ce téléphone existe déjà."
        )
    client = Client(
        nom=donnees.nom,
        prenom=donnees.prenom,
        telephone=donnees.telephone,
        email=donnees.email,
        adresse=donnees.adresse,
        genre=donnees.genre.value if donnees.genre else None,
        notes=donnees.notes,
    )
    db.add(client)
    db.flush()
    return client


def lister(
    db: Session,
    q: str | None,
    genre: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Client], int]:
    """Liste paginée, triée par nom puis prénom.

    q (>= 2 caractères) recherche dans nom, prénom et téléphone.
    """
    filtres = []
    if q:
        motif = f"%{q}%"
        filtres.append(
            or_(
                Client.nom.ilike(motif),
                Client.prenom.ilike(motif),
                Client.telephone.ilike(motif),
            )
        )
    if genre:
        filtres.append(Client.genre == genre)

    base = select(Client)
    for f in filtres:
        base = base.where(f)

    total = db.scalar(
        select(func.count()).select_from(base.order_by(None).subquery())
    )
    items = list(
        db.scalars(
            base.order_by(Client.nom, Client.prenom).limit(limit).offset(offset)
        )
    )
    return items, int(total or 0)


def modifier(db: Session, client: Client, donnees: ClientUpdate) -> Client:
    champs = donnees.model_dump(exclude_unset=True)

    if "telephone" in champs and champs["telephone"] is not None:
        nouveau = champs["telephone"]
        # Garder son propre numéro n'est pas un doublon.
        if _telephone_pris(db, nouveau, sauf_id=client.id):
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Un client avec ce téléphone existe déjà."
            )
        client.telephone = nouveau

    for champ in ("nom", "prenom", "email", "adresse", "notes"):
        if champ in champs:
            setattr(client, champ, champs[champ])
    if "genre" in champs:
        genre = champs["genre"]
        client.genre = genre.value if genre is not None else None

    db.flush()
    return client


def supprimer(db: Session, client: Client) -> None:
    # RG4 : un client qui a des commandes ne peut pas être supprimé.
    a_commandes = db.scalar(
        select(Commande.id).where(Commande.client_id == client.id).limit(1)
    )
    if a_commandes is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Impossible de supprimer un client qui a des commandes.",
        )
    # Les mesures du client sont supprimées en cascade.
    db.delete(client)
    db.flush()


def lister_commandes(
    db: Session, client: Client, limit: int, offset: int
) -> tuple[list[Commande], int]:
    """Commandes d'un client, la plus récente d'abord."""
    base = select(Commande).where(Commande.client_id == client.id)
    total = db.scalar(
        select(func.count()).select_from(
            select(Commande.id).where(Commande.client_id == client.id).subquery()
        )
    )
    items = list(
        db.scalars(
            base.order_by(Commande.date_commande.desc(), Commande.id.desc())
            .limit(limit)
            .offset(offset)
        )
    )
    return items, int(total or 0)


def resume(db: Session, client: Client) -> ClientResume:
    """Résumé d'activité. Les commandes annulées sont exclues."""
    commandes = list(
        db.scalars(
            select(Commande).where(
                Commande.client_id == client.id,
                Commande.statut != StatutCommande.annulee.value,
            )
        )
    )
    nb = len(commandes)
    chiffre_affaires = sum(c.montant_total for c in commandes)
    total_paye = sum(c.montant_paye for c in commandes)
    solde_du = chiffre_affaires - total_paye
    derniere = max((c.date_commande for c in commandes), default=None)
    a_des_mesures = (
        db.scalar(select(Mesure.id).where(Mesure.client_id == client.id).limit(1))
        is not None
    )
    return ClientResume(
        nb_commandes=nb,
        chiffre_affaires=chiffre_affaires,
        total_paye=total_paye,
        solde_du=solde_du,
        derniere_commande=derniere,
        a_des_mesures=a_des_mesures,
    )
