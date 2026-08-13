from pydantic import BaseModel
from typing import Optional

class UpdateUserRequestProduccion(BaseModel):

    email: Optional[str] = None

    nombre: Optional[str] = None

    apellido: Optional[str] = None
    
    legajo: Optional[int] = None
    
    dni: Optional[int] = None
    
    grupo: Optional[str] = None