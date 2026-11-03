"""Schémas communs : pagination."""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

# Valeurs par défaut de pagination (section 8 de l'énoncé).
LIMIT_DEFAUT = 20
LIMIT_MAX = 100
OFFSET_DEFAUT = 0


class Page(BaseModel, Generic[T]):
    """Enveloppe de liste paginée : {items, total, limit, offset}."""

    items: list[T]
    total: int
    limit: int
    offset: int
