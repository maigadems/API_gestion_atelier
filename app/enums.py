"""Énumérations métier (valeurs en français, comme dans l'énoncé)."""
from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    admin = "admin"
    tailleur = "tailleur"
    accueil = "accueil"


class Genre(str, Enum):
    homme = "homme"
    femme = "femme"
    enfant = "enfant"


class StatutCommande(str, Enum):
    en_attente = "en_attente"
    en_coupe = "en_coupe"
    en_couture = "en_couture"
    essayage = "essayage"
    retouches = "retouches"
    terminee = "terminee"
    livree = "livree"
    annulee = "annulee"


class ModePaiement(str, Enum):
    especes = "especes"
    wave = "wave"
    orange_money = "orange_money"
    virement = "virement"
    cheque = "cheque"


class ModeLivraison(str, Enum):
    retrait_atelier = "retrait_atelier"
    domicile = "domicile"


class StatutLivraison(str, Enum):
    planifiee = "planifiee"
    livree = "livree"
