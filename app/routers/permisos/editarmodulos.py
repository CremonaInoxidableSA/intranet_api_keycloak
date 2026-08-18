from fastapi import APIRouter, HTTPException, Depends

from app.schemas.edit_module import EditModuleRequest
from app.services.gestionpermisos.editarmodulos import editar_modulo
from app.security.permissions import require_role
from app.security.dependencies import get_current_user
from app.schemas.authenticated_user import AuthenticatedUser

router = APIRouter(
    prefix="/modulos",
    tags=["Permisos"]
)

@router.put(
    "/editar",
    dependencies=[Depends(require_role("PERMISO_EDITAR_MODULOS"))]
)
async def editar_modulo_endpoint(
    modulo_nombre: str,
    data: EditModuleRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Edita un módulo existente.
    
    Parámetros:
    - modulo_nombre: Nombre del módulo a editar
    - data: Datos a actualizar (todos opcionales)
    """
    
    try:
        resultado = await editar_modulo(
            modulo_nombre=modulo_nombre,
            subdominio=data.subdominio,
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
            detail=f"Error al editar módulo: {error_str}"
        )
