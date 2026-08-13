import httpx

from app.services.funcioneskeycloak.get_admin_base_url import get_admin_base_url
from app.services.funcioneskeycloak.get_admin_token import get_admin_token


async def eliminar_usuario(user_id: str):
    """
    Elimina los grupos de producción del usuario en Keycloak.
    """
    
    GRUPOS_PERMITIDOS = {"GRUPO_ENCARGADO_PRODUCCION", "GRUPO_OPERARIO_PRODUCCION"}
    
    try:
        token = await get_admin_token()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        grupos_usuario_url = f"{get_admin_base_url()}/users/{user_id}/groups"
        async with httpx.AsyncClient() as client:
            grupos_usuario_response = await client.get(
                grupos_usuario_url,
                headers=headers
            )
            grupos_usuario_response.raise_for_status()
            
            grupos_actuales = grupos_usuario_response.json()
        
        async with httpx.AsyncClient() as client:
            for grupo_actual in grupos_actuales:
                if grupo_actual["name"] in GRUPOS_PERMITIDOS:
                    delete_url = f"{get_admin_base_url()}/users/{user_id}/groups/{grupo_actual['id']}"
                    delete_response = await client.delete(
                        delete_url,
                        headers=headers
                    )
                    delete_response.raise_for_status()
        
        return {
            "success": True,
            "detail": "Grupos de producción eliminados correctamente del usuario",
            "user_id": user_id
        }
    
    except Exception as e:
        raise Exception(f"Error al eliminar grupos del usuario: {str(e)}")