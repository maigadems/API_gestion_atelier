"""Point d'entrée de l'API FastAPI.

Toutes les routes métier sont préfixées par /api/v1 (sauf /health).
Documentation interactive Swagger : /docs.
"""
from __future__ import annotations

from fastapi import FastAPI

from app.core.config import settings
from app.routers import auth, catalogue, clients, health, utilisateurs

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "API de gestion d'un atelier de couture — Partie A (Palier 1 : socle). "
        "Authentification, utilisateurs, clients et catalogue."
    ),
)

# Route de santé, hors préfixe.
app.include_router(health.router)

# Routes métier, préfixées par /api/v1.
prefix = settings.api_v1_prefix
app.include_router(auth.router, prefix=prefix)
app.include_router(utilisateurs.router, prefix=prefix)
app.include_router(clients.router, prefix=prefix)
app.include_router(catalogue.router, prefix=prefix)


@app.get("/", tags=["racine"])
def racine() -> dict[str, str]:
    return {
        "application": settings.app_name,
        "documentation": "/docs",
        "sante": "/health",
    }
