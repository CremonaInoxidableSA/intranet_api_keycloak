from fastapi import APIRouter, HTTPException, Depends, Query

from app.services.gestionpermisos.listagrupos import obtener_grupos_realm
from app.security.permissions import require_role
from app.security.dependencies import get_current_user
from app.schemas.authenticated_user import AuthenticatedUser

router = APIRouter(
    prefix="/grupos",
    tags=["Permisos"]
)

@router.get(
    "/lista",
    dependencies=[Depends(require_role("PERMISO_CONSULTAR_GRUPOS"))]
)
async def listar_grupos(
    numero_pagina: int = Query(1, ge=1, description="Número de página (empezando desde 1)"),
    filtro: str = Query("0", description="Filtro para buscar por nombre de grupo"),
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    """
    Retorna la lista de todos los grupos disponibles en el realm con paginación.
    """
    
    try:
        if filtro == "0" or filtro == None:
            filtro = None
        
        grupos, total = await obtener_grupos_realm(
            numero_pagina=numero_pagina,
            filtro=filtro
        )
        
        grupos_por_pagina = 10
        total_paginas = (total + grupos_por_pagina - 1) // grupos_por_pagina
        
        if total > 0 and numero_pagina > total_paginas:
            raise HTTPException(
                status_code=404,
                detail=f"Página {numero_pagina} no existe."
            )
        
        return {
            "data": grupos,
            "paginacion": {
                "total_paginas": total_paginas,
                "total_registros": total
            }
        }
    
    except HTTPException:
        raise
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