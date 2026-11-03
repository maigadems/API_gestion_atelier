"""Tests des clients (RG1, RG4, résumé, pagination)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def _creer(client, token, **kwargs):
    corps = {"nom": "Diop", "prenom": "Fatou", "telephone": "77 123 45 67"}
    corps.update(kwargs)
    return client.post("/api/v1/clients", headers=token("accueil"), json=corps)


def test_creer_client_normalise_telephone(client: TestClient, token) -> None:
    reponse = _creer(client, token)
    assert reponse.status_code == 201
    # RG1 : le téléphone est normalisé (espaces supprimés).
    assert reponse.json()["telephone"] == "771234567"


def test_doublon_telephone_normalise(client: TestClient, token) -> None:
    # RG1 : « 77 123 45 67 » et « 771234567 » désignent le même client.
    assert _creer(client, token, telephone="77 123 45 67").status_code == 201
    doublon = _creer(client, token, telephone="771234567", prenom="Autre")
    assert doublon.status_code == 409


def test_telephone_invalide(client: TestClient, token) -> None:
    # RG1 : forme invalide -> 422.
    reponse = _creer(client, token, telephone="abc")
    assert reponse.status_code == 422


def test_patch_ne_peut_pas_vider_nom(client: TestClient, token) -> None:
    client_id = _creer(client, token).json()["id"]
    reponse = client.patch(
        f"/api/v1/clients/{client_id}",
        headers=token("accueil"),
        json={"nom": ""},
    )
    assert reponse.status_code == 422


def test_patch_garder_son_propre_numero(client: TestClient, token) -> None:
    client_id = _creer(client, token, telephone="770000001").json()["id"]
    reponse = client.patch(
        f"/api/v1/clients/{client_id}",
        headers=token("accueil"),
        json={"telephone": "77 000 00 01"},
    )
    # Garder son propre numéro n'est pas un doublon.
    assert reponse.status_code == 200


def test_supprimer_client_par_admin(client: TestClient, token) -> None:
    client_id = _creer(client, token).json()["id"]
    reponse = client.delete(f"/api/v1/clients/{client_id}", headers=token("admin"))
    assert reponse.status_code == 204
    # Le client n'existe plus.
    assert (
        client.get(f"/api/v1/clients/{client_id}", headers=token("admin")).status_code
        == 404
    )


def test_resume_client_vide(client: TestClient, token) -> None:
    client_id = _creer(client, token).json()["id"]
    reponse = client.get(f"/api/v1/clients/{client_id}/resume", headers=token("admin"))
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["nb_commandes"] == 0
    assert corps["chiffre_affaires"] == 0
    assert corps["solde_du"] == 0
    assert corps["a_des_mesures"] is False


def test_liste_paginee(client: TestClient, token) -> None:
    for i in range(3):
        _creer(client, token, telephone=f"7710000{i:02d}", prenom=f"C{i}")
    reponse = client.get("/api/v1/clients?limit=2&offset=0", headers=token("admin"))
    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["total"] == 3
    assert corps["limit"] == 2
    assert len(corps["items"]) == 2


def test_recherche_q(client: TestClient, token) -> None:
    _creer(client, token, nom="Ndiaye", prenom="Awa", telephone="778888888")
    reponse = client.get("/api/v1/clients?q=Ndiaye", headers=token("admin"))
    assert reponse.status_code == 200
    assert reponse.json()["total"] == 1
