"""Configuration de l'application via variables d'environnement (.env).

Aucune valeur secrète n'est codée en dur : tout provient de l'environnement.
Voir .env.example pour la liste des variables attendues.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Application ---
    app_name: str = "API Atelier de Couture"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # --- Base de données ---
    # Exemple PostgreSQL : postgresql+psycopg://user:pass@host:5432/dbname
    database_url: str = "postgresql+psycopg://atelier:atelier@localhost:5432/atelier"

    # --- Sécurité / JWT ---
    secret_key: str = "dev-secret-key-a-remplacer-en-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 8  # 8 heures

    # --- Compte administrateur initial (utilisé par app.seed) ---
    admin_email: str = "admin@atelier.sn"
    admin_password: str = "changeme123"
    admin_nom_complet: str = "Administrateur"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
