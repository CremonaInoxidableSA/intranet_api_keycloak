from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.schemas.authenticated_user import AuthenticatedUser
from app.security.dependencies import get_current_user
from app.security.permissions import require_role
from app.services.gestionpermisos.estadosubmodulos import habilitar_submodulo, deshabilitar_submodulo


router = APIRouter(
    prefix="/submodulos",
    tags=["Permisos"]
)


@router.put("/habilitar")
async def put_habilitar_submodulo(
    submodulo_nombre: str = Query(..., description="Nombre del submódulo a habilitar"),
    usuario: AuthenticatedUser = Depends(require_role("PERMISO_EDITAR_SUBMODULOS"))
):
    """
    Habilita un submódulo.
    """
    try:
        resultado = habilitar_submodulo(submodulo_nombre)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/deshabilitar")
async def put_deshabilitar_submodulo(
    submodulo_nombre: str = Query(..., description="Nombre del submódulo a deshabilitar"),
    usuario: AuthenticatedUser = Depends(require_role("PERMISO_EDITAR_SUBMODULOS"))
):
    """
    Deshabilita un submódulo.
    """
    try:
        resultado = deshabilitar_submodulo(submodulo_nombre)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
