from fastapi import APIRouter, HTTPException, Depends

from app.schemas.asignar_grupo import AssignGroupRequest

from app.services.gestionproduccion.asignargrupo import asignar_grupo

from app.security.permissions import require_role

router = APIRouter(
    prefix="/usuarios-produccion",
    tags=["Produccion"]
)

@router.post(
    "/asignar-grupo",
    dependencies=[Depends(require_role("PERMISO_CREAR_USUARIOS_PRODUCCION"))]
)
async def assign_group_to_user(
    data: AssignGroupRequest
):

    try:
        resultado = await asignar_grupo(
            user_id=data.id,
            grupo=data.grupo
        )

        return resultado

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )