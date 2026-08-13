from fastapi import APIRouter, HTTPException, Depends

from app.schemas.delete_user import DeleteUserRequest

from app.services.gestionproduccion.eliminarusuario import eliminar_usuario

from app.security.permissions import require_role


router = APIRouter(
    prefix="/usuarios-produccion",
    tags=["Produccion"]
)

@router.post(
    "/eliminar",
    dependencies=[Depends(require_role("PERMISO_CREAR_USUARIOS_PRODUCCION"))]
)
async def eliminar_usuario_grupos(
    data: DeleteUserRequest
):

    try:
        resultado = await eliminar_usuario(
            user_id=data.id
        )

        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )