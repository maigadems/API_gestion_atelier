"""Fixtures de test.

Les tests utilisent une base SQLite en mémoire (autorisé pour les tests
uniquement). La dépendance get_db est surchargée pour pointer dessus.
"""
from __future__ import annotations

import os

# Forcer une configuration de test AVANT tout import de l'application.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "cle-de-test")

from collections.abc import Generator  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import get_db
from app.core.security import hash_password
from app.enums import Role
from app.main import app
from app.models import Base
from app.models.utilisateur import Utilisateur

# Base SQLite en mémoire, partagée entre connexions (StaticPool).
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
TestingSessionLocal = sessionmaker(
    bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True
)

# Comptes de test (un par rôle + un compte désactivé).
COMPTES = {
    "admin": ("admin@test.sn", "password123", Role.admin, True),
    "accueil": ("accueil@test.sn", "password123", Role.accueil, True),
    "tailleur": ("tailleur@test.sn", "password123", Role.tailleur, True),
    "desactive": ("desactive@test.sn", "password123", Role.accueil, False),
}


def _override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def _base_de_donnees() -> Generator[None, None, None]:
    """Recrée le schéma et les comptes de test avant chaque test."""
    Base.metadata.create_all(engine)
    db = TestingSessionLocal()
    try:
        for nom, (email, mdp, role, actif) in COMPTES.items():
            db.add(
                Utilisateur(
                    email=email,
                    nom_complet=f"Compte {nom}",
                    mot_de_passe_hash=hash_password(mdp),
                    role=role.value,
                    actif=actif,
                )
            )
        db.commit()
    finally:
        db.close()
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def token(client: TestClient):
    """Retourne une fonction qui fournit les en-têtes d'auth pour un rôle donné."""

    def _token(role: str = "admin") -> dict[str, str]:
        email, mdp, _, _ = COMPTES[role]
        reponse = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": mdp},
        )
        assert reponse.status_code == 200, reponse.text
        jeton = reponse.json()["access_token"]
        return {"Authorization": f"Bearer {jeton}"}

    return _token
