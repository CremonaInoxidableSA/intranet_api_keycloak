from fastapi import APIRouter, HTTPException, Depends, Query

from app.services.gestionproduccion.listausuarios import obtener_lista_usuarios
from app.services.gestionproduccion.detallesusuarios import obtener_detalle_usuario
from app.security.permissions import require_role
from app.schemas.authenticated_user import AuthenticatedUser
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/usuarios-produccion",
    tags=["Produccion"]
)

@router.get(
    "/detalles",
    dependencies=[Depends(require_role("PERMISO_CONSULTAR_USUARIOS_PRODUCCION"))]
)
async def obtener_usuario(
    user_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Obtiene los detalles de un usuario específico del sistema de producción.
    Retorna: nombre, apellido, email, grupo y DNI.
    """
    
    try:
        usuario = await obtener_detalle_usuario(
            user_id=user_id
        )
        
        return usuario
    
    except Exception as e:
        error_str = str(e)
        
        if "Error al conectar con Keycloak" in error_str:
            raise HTTPException(
                status_code=503,
                detail="Error al conectar con el servidor de autenticación"
            )
        elif "no pertenece a los grupos de producción permitidos" in error_str:
            raise HTTPException(
                status_code=403,
                detail="El usuario no tiene acceso a este sistema"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=error_str
            )
