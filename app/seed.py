"""Script d'initialisation : « python -m app.seed ».

Crée le premier administrateur (à partir des variables d'environnement) et les
prestations du catalogue de départ (annexe B). Idempotent : peut être relancé
sans créer de doublon. Suppose que le schéma existe déjà (alembic upgrade head).
"""
from __future__ import annotations

from sqlalchemy import select

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.enums import Role
from app.models.catalogue import TypeVetement
from app.models.utilisateur import Utilisateur

# Annexe B — catalogue de départ (prix en FCFA, délais en jours).
CATALOGUE_DEPART = [
    ("Boubou", "Boubou homme en bazin ou brodé", 35000, 10),
    ("Costume 2 pièces", "Veste et pantalon", 85000, 14),
    ("Robe", "Robe sur mesure", 30000, 7),
    ("Ensemble wax", "Tenue deux pièces en wax", 25000, 7),
    ("Chemise", "Chemise sur mesure", 15000, 5),
    ("Pantalon", "Pantalon sur mesure", 12000, 4),
    ("Retouche", "Ourlet, rétrécissement, remplacement de fermeture", 3000, 2),
]


def creer_admin(db) -> None:
    existant = db.scalar(
        select(Utilisateur).where(Utilisateur.email == settings.admin_email)
    )
    if existant is not None:
        print(f"[seed] Administrateur déjà présent : {settings.admin_email}")
        return
    admin = Utilisateur(
        email=settings.admin_email,
        nom_complet=settings.admin_nom_complet,
        mot_de_passe_hash=hash_password(settings.admin_password),
        role=Role.admin.value,
        actif=True,
    )
    db.add(admin)
    print(f"[seed] Administrateur créé : {settings.admin_email}")


def creer_catalogue(db) -> None:
    for nom, description, prix_base, delai_jours in CATALOGUE_DEPART:
        existant = db.scalar(select(TypeVetement).where(TypeVetement.nom == nom))
        if existant is not None:
            continue
        db.add(
            TypeVetement(
                nom=nom,
                description=description,
                prix_base=prix_base,
                delai_jours=delai_jours,
                actif=True,
            )
        )
        print(f"[seed] Prestation créée : {nom}")


def main() -> None:
    db = SessionLocal()
    try:
        creer_admin(db)
        creer_catalogue(db)
        db.commit()
        print("[seed] Initialisation terminée.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
