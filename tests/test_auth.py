"""Tests d'authentification (RG21, RG22, RG23)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_login_reussi(client: TestClient) -> None:
    reponse = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.sn", "password": "password123"},
    )
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["token_type"] == "bearer"
    assert corps["access_token"]
    assert corps["expires_in"] > 0


def test_login_mauvais_mot_de_passe(client: TestClient) -> None:
    reponse = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.sn", "password": "mauvais"},
    )
    assert reponse.status_code == 401


def test_login_email_inconnu(client: TestClient) -> None:
    # RG23 : même code/message qu'un mot de passe faux.
    reponse = client.post(
        "/api/v1/auth/login",
        data={"username": "inconnu@test.sn", "password": "password123"},
    )
    assert reponse.status_code == 401


def test_login_compte_desactive(client: TestClient) -> None:
    # RG22 : un compte désactivé est refusé.
    reponse = client.post(
        "/api/v1/auth/login",
        data={"username": "desactive@test.sn", "password": "password123"},
    )
    assert reponse.status_code == 401


def test_me_sans_jeton(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_avec_jeton(client: TestClient, token) -> None:
    reponse = client.get("/api/v1/auth/me", headers=token("tailleur"))
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["email"] == "tailleur@test.sn"
    assert corps["role"] == "tailleur"
    # RG21 : aucune donnée sensible renvoyée.
    assert "mot_de_passe_hash" not in corps
    assert "mot_de_passe" not in corps
