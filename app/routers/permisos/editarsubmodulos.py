from fastapi import APIRouter, HTTPException, Depends

from app.schemas.edit_submodule import EditSubmoduleRequest
from app.services.gestionpermisos.editarsubmodulos import editar_submodulo
from app.security.permissions import require_role
from app.security.dependencies import get_current_user
from app.schemas.authenticated_user import AuthenticatedUser

router = APIRouter(
    prefix="/submodulos",
    tags=["Permisos"]
)

@router.put(
    "/editar",
    dependencies=[Depends(require_role("PERMISO_EDITAR_SUBMODULOS"))]
)
async def editar_submodulo_endpoint(
    submodulo_nombre: str,
    data: EditSubmoduleRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Edita un submódulo existente.
    
    Parámetros:
    - submodulo_nombre: Nombre del submódulo a editar
    - data: Datos a actualizar (todos opcionales)
    """
    
    try:
        resultado = await editar_submodulo(
            submodulo_nombre=submodulo_nombre,
            modulo_padre=data.modulo_padre,
            path=data.path,
            icono=data.icono
        )
        
        return resultado
    
    except Exception as e:
        error_str = str(e)
        
        if "no existe" in error_str:
            raise HTTPException(
                status_code=404,
                detail=error_str
            )
        
        if "ya está siendo utilizado" in error_str:
            raise HTTPException(
                status_code=400,
                detail=error_str
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error al editar submódulo: {error_str}"
        )
