"""Tests des droits par rôle (401 sans jeton, 403 rôle insuffisant)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_creer_utilisateur_interdit_sans_jeton(client: TestClient) -> None:
    reponse = client.post(
        "/api/v1/utilisateurs",
        json={
            "email": "x@test.sn",
            "nom_complet": "X",
            "mot_de_passe": "password123",
            "role": "accueil",
        },
    )
    assert reponse.status_code == 401


def test_creer_utilisateur_interdit_pour_accueil(client: TestClient, token) -> None:
    reponse = client.post(
        "/api/v1/utilisateurs",
        headers=token("accueil"),
        json={
            "email": "x@test.sn",
            "nom_complet": "X",
            "mot_de_passe": "password123",
            "role": "accueil",
        },
    )
    assert reponse.status_code == 403


def test_creer_utilisateur_autorise_pour_admin(client: TestClient, token) -> None:
    reponse = client.post(
        "/api/v1/utilisateurs",
        headers=token("admin"),
        json={
            "email": "nouveau@test.sn",
            "nom_complet": "Nouveau",
            "mot_de_passe": "password123",
            "role": "tailleur",
        },
    )
    assert reponse.status_code == 201


def test_supprimer_client_interdit_pour_tailleur(client: TestClient, token) -> None:
    # Créer un client (tout rôle connecté le peut).
    creation = client.post(
        "/api/v1/clients",
        headers=token("accueil"),
        json={"nom": "Diop", "prenom": "Fatou", "telephone": "770000000"},
    )
    assert creation.status_code == 201
    client_id = creation.json()["id"]

    # Le tailleur ne peut pas supprimer (route réservée admin).
    reponse = client.delete(
        f"/api/v1/clients/{client_id}", headers=token("tailleur")
    )
    assert reponse.status_code == 403


def test_catalogue_creation_reservee_admin(client: TestClient, token) -> None:
    reponse = client.post(
        "/api/v1/catalogue",
        headers=token("accueil"),
        json={"nom": "Veste", "prix_base": 20000, "delai_jours": 6},
    )
    assert reponse.status_code == 403
