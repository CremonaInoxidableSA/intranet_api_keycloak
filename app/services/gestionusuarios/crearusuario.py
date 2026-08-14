import httpx
from sqlalchemy import text
from typing import Optional, List

from app.services.funcioneskeycloak.get_admin_base_url import get_admin_base_url
from app.services.funcioneskeycloak.get_admin_token import get_admin_token

from app.services.gestionpermisos.listagrupos import obtener_grupos_realm
from app.config.db import SessionLocal
from app.models.usuarios import Usuarios
from app.core.config import settings

from app.services.funcioneskeycloak.verificar_conexiones import verificar_conexiones

async def crear_usuario(
    username: str,
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    habilitado: bool = True,
    dni: int | None = None,
    legajo: int | None = None,
    grupos: Optional[List[str]] = None
):
    """
    Crea un usuario en Keycloak y luego en MySQL.
    Verifica conexiones antes de crear.
    """
    
    await verificar_conexiones()
    
    try:
        token = await get_admin_token()

        url = (
            f"{get_admin_base_url()}"
            "/users"
        )

        body = {
            "username": username,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "enabled": habilitado,
            "emailVerified": False,
            "requiredActions": [
                "UPDATE_PASSWORD"
            ],
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": True
                }
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=body,
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )

            response.raise_for_status()

            location = response.headers["Location"]

        user_id = location.split("/")[-1]
    
    except Exception as e:
        raise Exception(f"Falla en creación general: {str(e)}")
    
    if grupos is not None:
        try:
            token = await get_admin_token()
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            # Obtener TODOS los grupos disponibles (sin paginación)
            all_grupos_url = f"{get_admin_base_url()}/groups"
            async with httpx.AsyncClient() as client:
                all_grupos_response = await client.get(
                    all_grupos_url,
                    headers=headers
                )
                all_grupos_response.raise_for_status()
                
                all_grupos = all_grupos_response.json()
                grupos_disponibles_names = {
                    g["name"]
                    for g in all_grupos
                    if g["name"].startswith("GRUPO_")
                }
            
            grupos_invalidos = [
                g for g in grupos
                if g not in grupos_disponibles_names
            ]
            
            if grupos_invalidos:
                raise Exception(f"Los siguientes grupos no existen: {', '.join(grupos_invalidos)}")
            
            # Mapeo de nombres de grupos a IDs
            grupos_disponibles = {
                g["name"]: g["id"]
                for g in all_grupos
            }
            
            # Asignar grupos al usuario
            grupos_url = f"{get_admin_base_url()}/users/{user_id}/groups"
            async with httpx.AsyncClient() as client:
                for grupo_name in grupos:
                    if grupo_name in grupos_disponibles:
                        grupo_id = grupos_disponibles[grupo_name]
                        join_response = await client.put(
                            f"{grupos_url}/{grupo_id}",
                            headers=headers
                        )
                        join_response.raise_for_status()
        
        except Exception as e:
            raise Exception(f"Error al asignar grupos: {str(e)}")
    
    if dni is not None and legajo is not None:
        db = SessionLocal()
        try:
            nuevo_usuario = Usuarios(
                id=user_id,
                dni=dni,
                legajo=legajo
            )
            
            db.add(nuevo_usuario)
            db.commit()
            db.close()
            
        except Exception as db_error:
            db.close()
            raise Exception(f"Falla en creación en base de datos: {str(db_error)}")
    
    return {
        "detail": "Creación correcta",
        "id": user_id,
        "email": email,
        "dni": dni,
        "legajo": legajo,
        "habilitado": habilitado
    }