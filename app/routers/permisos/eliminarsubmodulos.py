from fastapi import APIRouter, HTTPException, Depends, Query

from app.services.gestionpermisos.eliminarsubmodulos import eliminar_submodulo
from app.security.permissions import require_role
from app.security.dependencies import get_current_user
from app.schemas.authenticated_user import AuthenticatedUser

router = APIRouter(
    prefix="/submodulos",
    tags=["Permisos"]
)


@router.delete(
    "/eliminar",
    dependencies=[Depends(require_role("PERMISO_ELIMINAR_SUBMODULOS"))]
)
async def delete_submodulo(
    submodulo_nombre: str = Query(..., description="Nombre del submódulo a eliminar"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Elimina un submódulo de Keycloak y BD.
    """
    
    try:
        resultado = await eliminar_submodulo(submodulo_nombre)
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
            detail=f"Error al eliminar submódulo: {error_str}"
        )
