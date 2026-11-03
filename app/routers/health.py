"""Route de santé (hors préfixe /api/v1)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

router = APIRouter(tags=["santé"])


@router.get("/health")
def health(db: Session = Depends(get_db)) -> dict[str, str]:
    """Répond {"status": "ok"} après avoir vérifié que la base répond."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:  # pragma: no cover - dépend de l'état de la base
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "Base de données indisponible."
        )
    return {"status": "ok"}
