from fastapi import APIRouter, HTTPException, Depends, Query

from app.services.gestionpermisos.eliminarmodulos import eliminar_modulo
from app.security.permissions import require_role
from app.security.dependencies import get_current_user
from app.schemas.authenticated_user import AuthenticatedUser

router = APIRouter(
    prefix="/modulos",
    tags=["Permisos"]
)


@router.delete(
    "/eliminar",
    dependencies=[Depends(require_role("PERMISO_ELIMINAR_MODULOS"))]
)
async def delete_modulo(
    modulo_nombre: str = Query(..., description="Nombre del módulo a eliminar"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Elimina un módulo de Keycloak y BD.
    También elimina todos los submódulos asociados.
    """
    
    try:
        resultado = await eliminar_modulo(modulo_nombre)
        return resultado
    
    except Exception as e:
        error_str = str(e)
        
        if "no existe" in error_str:
            raise HTTPException(
                status_code=404,
                detail=error_str
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error al eliminar módulo: {error_str}"
        )