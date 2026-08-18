from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.schemas.authenticated_user import AuthenticatedUser
from app.security.dependencies import get_current_user
from app.security.permissions import require_role
from app.services.gestionpermisos.estadomodulos import habilitar_modulo, deshabilitar_modulo


router = APIRouter(
    prefix="/modulos",
    tags=["Permisos"]
)


@router.put("/habilitar")
async def put_habilitar_modulo(
    modulo_nombre: str = Query(..., description="Nombre del módulo a habilitar"),
    usuario: AuthenticatedUser = Depends(require_role("PERMISO_EDITAR_MODULOS"))
):
    """
    Habilita un módulo.
    """
    try:
        resultado = habilitar_modulo(modulo_nombre)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/deshabilitar")
async def put_deshabilitar_modulo(
    modulo_nombre: str = Query(..., description="Nombre del módulo a deshabilitar"),
    usuario: AuthenticatedUser = Depends(require_role("PERMISO_EDITAR_MODULOS"))
):
    """
    Deshabilita un módulo.
    """
    try:
        resultado = deshabilitar_modulo(modulo_nombre)
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
