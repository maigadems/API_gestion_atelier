from fastapi import APIRouter

from app.schemas.clients import ClientCreate

router = APIRouter(prefix="/clients", tags=["Clients"])


@router.post("", status_code=201)
def creer_client(client: ClientCreate):
    return {"nom": client.nom, "telephone": client.telephone}
