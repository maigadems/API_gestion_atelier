#!/usr/bin/env bash
set -e

echo "[entrypoint] Attente de la base de données..."
python - <<'PY'
import time
import sqlalchemy
from app.core.config import settings

engine = sqlalchemy.create_engine(settings.database_url)
for tentative in range(30):
    try:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        print("[entrypoint] Base de données prête.")
        break
    except Exception as exc:  # noqa: BLE001
        print(f"[entrypoint] Base indisponible ({tentative + 1}/30) : {exc}")
        time.sleep(2)
else:
    raise SystemExit("[entrypoint] Base de données injoignable.")
PY

echo "[entrypoint] Application des migrations (alembic upgrade head)..."
alembic upgrade head

echo "[entrypoint] Initialisation des données (seed)..."
python -m app.seed

echo "[entrypoint] Démarrage de l'API..."
exec "$@"
