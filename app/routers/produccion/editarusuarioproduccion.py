from fastapi import APIRouter, HTTPException, Depends
import re

from app.schemas.edit_user_produccion import UpdateUserRequestProduccion
from app.services.gestionproduccion.editarusuario import editar_usuario as editar_usuario_servicio
from app.security.permissions import require_role
from app.security.dependencies import get_current_user
from app.schemas.authenticated_user import AuthenticatedUser

router = APIRouter(
    prefix="/usuarios-produccion",
    tags=["Produccion"]
)

def validar_email(email: str) -> bool:
    """
    Valida que el email tenga un formato correcto.
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

@router.put(
    "/editar",
    dependencies=[Depends(require_role("PERMISO_EDITAR_USUARIOS_PRODUCCION"))]
)
async def editar_usuario(
    user_id: str,
    data: UpdateUserRequestProduccion,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    if data.email is not None and data.email != "":
        if not validar_email(data.email):
            raise HTTPException(
                status_code=400,
                detail="El formato del correo electrónico es inválido"
            )
    
    try:
        resultado = await editar_usuario_servicio(
            user_id=user_id,
            email=data.email,
            nombre=data.nombre,
            apellido=data.apellido,
            legajo=data.legajo,
            dni=data.dni,
            grupo=data.grupo
        )
        
        return resultado
    
    except Exception as e:
        error_str = str(e)
        
        if "no encontrado" in error_str:
            raise HTTPException(
                status_code=404,
                detail=error_str
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error al editar usuario: {error_str}"
        )
