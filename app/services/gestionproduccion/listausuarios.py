import httpx
import asyncio

from app.services.funcioneskeycloak.get_admin_base_url import get_admin_base_url
from app.services.funcioneskeycloak.get_admin_token import get_admin_token
from app.config.db import SessionLocal
from app.models.usuarios import Usuarios

def obtener_legajo_usuario(user_id: str):
    """
    Obtiene el legajo del usuario desde la base de datos.
    """
    legajo = None
    
    try:
        db = SessionLocal()
        usuario_db = db.query(Usuarios).filter(Usuarios.id == user_id).first()
        db.close()
        
        if usuario_db and usuario_db.legajo is not None:
            legajo = usuario_db.legajo
    
    except Exception:
        pass
    
    return legajo

async def obtener_grupos_usuario(client: httpx.AsyncClient, user_id: str, headers: dict):
    """
    Obtiene los grupos de un usuario específico.
    """
    grupos_url = f"{get_admin_base_url()}/users/{user_id}/groups"
    
    try:
        response = await client.get(
            grupos_url,
            headers=headers
        )
        response.raise_for_status()
        
        grupos = [
            {"nombre": grupo.get("name")}
            for grupo in response.json()
        ]
        return grupos
    except Exception:
        return []

async def obtener_lista_usuarios(filtro: str = None):
    """
    Obtiene la lista de usuarios de Keycloak con filtro.
    """
    
    GRUPOS_PERMITIDOS = {"GRUPO_ENCARGADO_PRODUCCION", "GRUPO_OPERARIO_PRODUCCION"}
    
    try:
        token = await get_admin_token()
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        url = (
            f"{get_admin_base_url()}"
            f"/users"
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers
            )
            
            response.raise_for_status()
            
            usuarios = response.json()
        
        usuarios_filtrados = []
        
        for usuario in usuarios:
            if filtro:
                nombre = usuario.get("firstName", "").lower()
                apellido = usuario.get("lastName", "").lower()
                filtro_lower = filtro.lower()
                
                if not (filtro_lower in nombre or filtro_lower in apellido):
                    continue
            
            usuarios_filtrados.append(usuario)
        
        async with httpx.AsyncClient() as client:
            tareas = [
                obtener_grupos_usuario(client, usuario.get("id"), headers)
                for usuario in usuarios_filtrados
            ]
            
            grupos_list = await asyncio.gather(*tareas)
        
        usuarios_procesados = []
        
        for usuario, grupos in zip(usuarios_filtrados, grupos_list):
            nombres_grupos = {g["nombre"] for g in grupos}
            grupos_interseccion = nombres_grupos.intersection(GRUPOS_PERMITIDOS)
            if not grupos_interseccion:
                continue
            
            grupo_del_usuario = next(iter(grupos_interseccion))
            
            # Obtener legajo desde la base de datos
            legajo = obtener_legajo_usuario(usuario.get("id"))
            
            usuario_procesado = {
                "id": usuario.get("id"),
                "nombre": usuario.get("firstName"),
                "apellido": usuario.get("lastName"),
                "grupo": grupo_del_usuario,
                "legajo": legajo
            }
            
            usuarios_procesados.append(usuario_procesado)
        
        return usuarios_procesados
    
    except httpx.HTTPError as e:
        raise Exception(f"Error al conectar con Keycloak: {str(e)}")
    except Exception as e:
        raise Exception(f"Error al obtener lista de usuarios: {str(e)}")
