"""Base déclarative SQLAlchemy 2 et utilitaires communs."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase


def utcnow() -> datetime:
    """Horodatage courant en UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Classe de base pour tous les modèles ORM."""
