from fastapi import APIRouter, HTTPException, Depends, Query

from app.services.gestionproduccion.listausuarios import obtener_lista_usuarios
from app.security.permissions import require_role
from app.schemas.authenticated_user import AuthenticatedUser
from app.security.dependencies import get_current_user

router = APIRouter(
    prefix="/usuarios-produccion",
    tags=["Produccion"]
)

@router.get(
    "/lista",
    dependencies=[Depends(require_role("PERMISO_CONSULTAR_USUARIOS_PRODUCCION"))]
)
async def listar_usuarios(
    filtro: str = Query("0", description="Filtro para buscar por email, nombre o apellido"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Obtiene la lista de usuarios del sistema con filtro.
    """
    
    try:
        if filtro == "0" or filtro == None:
            filtro = None
        
        usuarios = await obtener_lista_usuarios(
            filtro=filtro
        )
        
        return usuarios
    
    except Exception as e:
        error_str = str(e)
        
        if "Error al conectar con Keycloak" in error_str:
            raise HTTPException(
                status_code=503,
                detail="Error al conectar con el servidor de autenticación"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=error_str
            )
