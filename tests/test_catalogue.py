"""Tests du catalogue (RG6 : prestation inactive, doublon de nom, filtre actifs)."""
from __future__ import annotations

from fastapi.testclient import TestClient


def _creer(client, token, nom="Boubou", prix=35000, delai=10):
    return client.post(
        "/api/v1/catalogue",
        headers=token("admin"),
        json={"nom": nom, "prix_base": prix, "delai_jours": delai},
    )


def test_creer_prestation(client: TestClient, token) -> None:
    reponse = _creer(client, token)
    assert reponse.status_code == 201
    corps = reponse.json()
    assert corps["nom"] == "Boubou"
    assert corps["actif"] is True


def test_doublon_nom(client: TestClient, token) -> None:
    assert _creer(client, token, nom="Robe").status_code == 201
    assert _creer(client, token, nom="Robe").status_code == 409


def test_liste_actifs_seulement_par_defaut(client: TestClient, token) -> None:
    pid = _creer(client, token, nom="Chemise").json()["id"]
    # Désactiver la prestation.
    maj = client.patch(
        f"/api/v1/catalogue/{pid}", headers=token("admin"), json={"actif": False}
    )
    assert maj.status_code == 200

    # Par défaut, les prestations inactives ne sont pas listées.
    actifs = client.get("/api/v1/catalogue", headers=token("accueil")).json()
    assert all(p["nom"] != "Chemise" for p in actifs)

    # actifs_seulement=false montre tout.
    tous = client.get(
        "/api/v1/catalogue?actifs_seulement=false", headers=token("accueil")
    ).json()
    assert any(p["nom"] == "Chemise" for p in tous)


def test_detail_introuvable(client: TestClient, token) -> None:
    assert (
        client.get("/api/v1/catalogue/9999", headers=token("accueil")).status_code
        == 404
    )
