import re

from pydantic import BaseModel, field_validator


class ClientCreate(BaseModel):
    nom: str
    prenom: str
    telephone: str
    email: str | None = None

    @field_validator("telephone")
    @classmethod
    def normaliser_telephone(cls, valeur: str) -> str:
        numero = re.sub(r"[ .\-()]", "", valeur)
        if not re.fullmatch(r"\+?[0-9]{6,20}", numero):
            raise ValueError("6 à 20 chiffres, avec un + initial facultatif")
        return numero
