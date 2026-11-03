"""Tests des utilisateurs (RG24, doublon e-mail, tri)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def _id_admin(client: TestClient, token) -> int:
    liste = client.get("/api/v1/utilisateurs", headers=token("admin")).json()
    return next(u["id"] for u in liste if u["email"] == "admin@test.sn")


def test_creer_doublon_email(client: TestClient, token) -> None:
    reponse = client.post(
        "/api/v1/utilisateurs",
        headers=token("admin"),
        json={
            "email": "admin@test.sn",
            "nom_complet": "Doublon",
            "mot_de_passe": "password123",
            "role": "accueil",
        },
    )
    assert reponse.status_code == 409


def test_mot_de_passe_trop_court(client: TestClient, token) -> None:
    # RG21 : longueur minimale 8.
    reponse = client.post(
        "/api/v1/utilisateurs",
        headers=token("admin"),
        json={
            "email": "court@test.sn",
            "nom_complet": "Court",
            "mot_de_passe": "123",
            "role": "accueil",
        },
    )
    assert reponse.status_code == 422


def test_admin_ne_peut_pas_se_desactiver(client: TestClient, token) -> None:
    # RG24.
    admin_id = _id_admin(client, token)
    reponse = client.patch(
        f"/api/v1/utilisateurs/{admin_id}",
        headers=token("admin"),
        json={"actif": False},
    )
    assert reponse.status_code == 409


def test_admin_ne_peut_pas_retirer_son_role(client: TestClient, token) -> None:
    # RG24.
    admin_id = _id_admin(client, token)
    reponse = client.patch(
        f"/api/v1/utilisateurs/{admin_id}",
        headers=token("admin"),
        json={"role": "accueil"},
    )
    assert reponse.status_code == 409


def test_liste_triee_par_nom(client: TestClient, token) -> None:
    reponse = client.get("/api/v1/utilisateurs", headers=token("admin"))
    assert reponse.status_code == 200
    noms = [u["nom_complet"] for u in reponse.json()]
    assert noms == sorted(noms)
