"""Fonctions utilitaires transverses."""
from __future__ import annotations

import re

_PHONE_STRIP = str.maketrans("", "", " .-()")
_PHONE_RE = re.compile(r"^\+?\d{6,20}$")


def normaliser_telephone(valeur: str) -> str:
    """Normalise un numéro de téléphone (RG1).

    Supprime espaces, points, tirets et parenthèses, puis valide la forme :
    6 à 20 chiffres, avec un « + » initial facultatif.

    Lève ``ValueError`` si le numéro est invalide (traduit en 422 par FastAPI).
    """
    if valeur is None:
        raise ValueError("Le téléphone est obligatoire.")
    normalise = valeur.strip().translate(_PHONE_STRIP)
    if not _PHONE_RE.match(normalise):
        raise ValueError(
            "Numéro de téléphone invalide : 6 à 20 chiffres, "
            "avec un « + » initial facultatif."
        )
    return normalise
