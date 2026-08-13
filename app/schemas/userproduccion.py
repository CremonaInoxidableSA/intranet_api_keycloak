from pydantic import BaseModel, EmailStr
from typing import Optional


class CreateUserProduccionRequest(BaseModel):

    email: EmailStr

    nombre: str

    apellido: str

    dni: int | None = None

    legajo: int | None = None

    habilitado: bool = True

    grupo: Optional[str] = None