from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from app.schemas.edit_group import EditGroupRequest
from app.services.gestionpermisos.editargrupos import editar_grupo
from app.security.permissions import require_role
from app.security.dependencies import get_current_user
from app.schemas.authenticated_user import AuthenticatedUser

router = APIRouter(
    prefix="/grupos",
    tags=["Permisos"]
)

@router.put(
    "/editar",
    dependencies=[Depends(require_role("PERMISO_EDITAR_GRUPOS"))]
)
async def editar_grupo_endpoint(
    grupo_nombre: str,
    data: EditGroupRequest = None,
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Edita un grupo en Keycloak.
    """
    
    if data is None:
        data = EditGroupRequest()
    
    try:
        resultado = await editar_grupo(
            nombre=grupo_nombre,
            permisos=data.permisos,
            modulos=data.modulos,
            submodulos=data.submodulos
        )
        
        return resultado
    
    except Exception as e:
        error_str = str(e)
        
        if "no existe" in error_str:
            raise HTTPException(
                status_code=404,
                detail=error_str
            )
        
        if "Error al" in error_str:
            raise HTTPException(
                status_code=500,
                detail=error_str
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error al editar grupo: {error_str}"
        )
