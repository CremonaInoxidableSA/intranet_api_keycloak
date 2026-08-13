from fastapi import APIRouter, HTTPException, Depends

from app.schemas.userproduccion import CreateUserProduccionRequest

from app.services.funcioneskeycloak.get_user import get_user

from app.services.gestionproduccion.crearusuario import crear_usuario

from app.security.permissions import require_role
from app.schemas.authenticated_user import AuthenticatedUser
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/usuarios-produccion",
    tags=["Produccion"]
)

@router.post(
    "/crear",
    dependencies=[Depends(require_role("PERMISO_CREAR_USUARIOS_PRODUCCION"))]
)
async def create_new_user(
    data: CreateUserProduccionRequest
):

    try:
        resultado = await crear_usuario(
            username=data.email,
            email=data.email,
            first_name=data.nombre,
            last_name=data.apellido,
            password="12345678",
            habilitado=data.habilitado,
            dni=data.dni,
            legajo=data.legajo,
            grupo=data.grupo
        )

        return resultado

    except Exception as e:
        error_str = str(e)
        
        if "Falla en creación general" in error_str:
            raise HTTPException(
                status_code=400,
                detail=error_str
            )
        elif "Falla en creación en base de datos" in error_str:
            raise HTTPException(
                status_code=400,
                detail=error_str
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )