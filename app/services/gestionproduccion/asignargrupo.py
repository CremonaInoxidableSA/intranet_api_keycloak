import httpx

from app.services.funcioneskeycloak.get_admin_base_url import get_admin_base_url
from app.services.funcioneskeycloak.get_admin_token import get_admin_token


async def asignar_grupo(user_id: str, grupo: str):
    """
    Asigna un grupo permitido a un usuario en Keycloak.
    """
    
    GRUPOS_PERMITIDOS = {"GRUPO_ENCARGADO_PRODUCCION", "GRUPO_OPERARIO_PRODUCCION"}
    
    if grupo not in GRUPOS_PERMITIDOS:
        raise Exception(f"El grupo '{grupo}' no es permitido. Solo se permiten: {', '.join(GRUPOS_PERMITIDOS)}")
    
    try:
        token = await get_admin_token()
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        all_grupos_url = f"{get_admin_base_url()}/groups"
        async with httpx.AsyncClient() as client:
            all_grupos_response = await client.get(
                all_grupos_url,
                headers=headers
            )
            all_grupos_response.raise_for_status()
            
            all_grupos = all_grupos_response.json()
            
            grupos_disponibles = {g["name"]: g["id"] for g in all_grupos}
            
            grupo_encontrado = None
            for g in all_grupos:
                if g["name"] == grupo:
                    grupo_encontrado = g
                    break
            
            if not grupo_encontrado:
                raise Exception(f"El grupo '{grupo}' no existe en Keycloak")
        
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
        
        grupo_id = grupo_encontrado["id"]
        grupos_url = f"{get_admin_base_url()}/users/{user_id}/groups/{grupo_id}"
        async with httpx.AsyncClient() as client:
            join_response = await client.put(
                grupos_url,
                headers=headers
            )
            join_response.raise_for_status()
        
        return {
            "success": True,
            "detail": f"Grupo '{grupo}' asignado correctamente al usuario",
            "user_id": user_id,
            "grupo": grupo
        }
    
    except Exception as e:
        raise Exception(f"Error al asignar grupo: {str(e)}")