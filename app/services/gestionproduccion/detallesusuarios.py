import httpx
import asyncio

from app.services.funcioneskeycloak.get_admin_base_url import get_admin_base_url
from app.services.funcioneskeycloak.get_admin_token import get_admin_token
from app.config.db import SessionLocal
from app.models.usuarios import Usuarios

def obtener_campo_usuario(user_id: str, campo: str):
    """
    Obtiene un campo específico del usuario desde la base de datos.
    """
    valor = None
    
    try:
        db = SessionLocal()
        usuario_db = db.query(Usuarios).filter(Usuarios.id == user_id).first()
        db.close()
        
        if usuario_db:
            valor = getattr(usuario_db, campo, None)
    
    except Exception:
        pass
    
    return valor

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
    
    GRUPOS_PERMITIDOS = {"GRUPO_ENCARGADOS_PRODUCCION", "GRUPO_OPERARIOS_PRODUCCION"}
    
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
            legajo = obtener_campo_usuario(usuario.get("id"), "legajo")
            
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





async def obtener_detalle_usuario(user_id: str):
    """
    Obtiene los detalles de un usuario específico de producción.
    Combina datos de Keycloak (email, nombre, apellido) con datos de la BD (DNI).
    """
    
    GRUPOS_PERMITIDOS = {"GRUPO_ENCARGADOS_PRODUCCION", "GRUPO_OPERARIOS_PRODUCCION"}
    
    try:
        token = await get_admin_token()
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        url = f"{get_admin_base_url()}/users/{user_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers
            )
            
            response.raise_for_status()
            usuario = response.json()
        
        async with httpx.AsyncClient() as client:
            grupos = await obtener_grupos_usuario(client, user_id, headers)
        
        nombres_grupos = {g["nombre"] for g in grupos}
        grupos_interseccion = nombres_grupos.intersection(GRUPOS_PERMITIDOS)
        
        if not grupos_interseccion:
            raise Exception("El usuario no pertenece a los grupos de producción permitidos")
        
        grupo_del_usuario = next(iter(grupos_interseccion))
        
        dni = obtener_campo_usuario(user_id, "dni")
        
        usuario_detalle = {
            "id": usuario.get("id"),
            "nombre": usuario.get("firstName"),
            "apellido": usuario.get("lastName"),
            "email": usuario.get("email"),
            "grupo": grupo_del_usuario,
            "dni": dni
        }
        
        return usuario_detalle
    
    except httpx.HTTPError as e:
        raise Exception(f"Error al conectar con Keycloak: {str(e)}")
    except Exception as e:
        raise Exception(f"Error al obtener detalle del usuario: {str(e)}")
