import httpx
from sqlalchemy import text
from typing import Optional
import logging

from app.services.funcioneskeycloak.get_admin_base_url import get_admin_base_url
from app.services.funcioneskeycloak.get_admin_token import get_admin_token
from app.services.funcioneskeycloak.get_user import get_user

from app.services.funcioneskeycloak.verificar_conexiones import verificar_conexiones

from app.services.gestionpermisos.listagrupos import obtener_grupos_realm
from app.config.db import SessionLocal
from app.models.usuarios import Usuarios
from app.core.config import settings

async def crear_usuario(
    username: str,
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    habilitado: bool = True,
    dni: int | None = None,
    legajo: int | None = None,
    grupo: Optional[str] = None
):
    """
    Crea un usuario en Keycloak y luego en MySQL.
    Verifica conexiones antes de crear.
    """
    
    await verificar_conexiones()

    GRUPOS_PERMITIDOS = {"GRUPO_ENCARGADO_PRODUCCION", "GRUPO_OPERARIO_PRODUCCION"}
    if grupo is not None:
        if grupo not in GRUPOS_PERMITIDOS:
            raise Exception(f"El grupo '{grupo}' no es permitido. Solo se permiten: {', '.join(GRUPOS_PERMITIDOS)}")
        
    try:
        token = await get_admin_token()

        url = (
            f"{get_admin_base_url()}"
            "/users"
        )
            
        async with httpx.AsyncClient() as client:
            check_email_response = await client.get(
                f"{url}?email={email}",
                headers={
                    "Authorization": f"Bearer {token}"
                }
            )
            check_email_response.raise_for_status()
            
            usuarios_con_email = check_email_response.json()
            
            if usuarios_con_email:
                return {
                    "success": False,
                    "code": "EMAIL_DUPLICADO",
                    "detail": f"El email '{email}' ya se encuentra registrado en el sistema."
                }    
    except Exception as e:
        raise Exception(f"Error verificando email: {str(e)}")
    
    db = SessionLocal()
    try:
        query = db.query(Usuarios)
        
        if dni is not None and legajo is not None:
            usuario_existente = query.filter(
                (Usuarios.dni == dni) | (Usuarios.legajo == legajo)
            ).first()
        elif dni is not None:
            usuario_existente = query.filter(Usuarios.dni == dni).first()
        else:
            usuario_existente = query.filter(Usuarios.legajo == legajo).first()
        
        db.close()
        
        if usuario_existente:
            return {
                "success": False,
                "code": "EXISTE_GENERAL",
                "detail": f"El DNI o LEGAJO ingresado ya se encuentra asignado a un usuario perteneciente a la intranet.",
                "id": usuario_existente.id
            }
    except Exception as e:
        db.close()
        raise Exception(f"Error verificando usuarios existentes: {str(e)}")
    
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
    
    if grupo is not None:
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
                
                # Buscar el grupo
                grupo_encontrado = None
                for g in all_grupos:
                    if g["name"] == grupo:
                        grupo_encontrado = g
                        break
                
                if not grupo_encontrado:
                    raise Exception(f"El grupo '{grupo}' no existe en Keycloak")
            
            grupo_id = grupo_encontrado["id"]
            
            grupos_url = f"{get_admin_base_url()}/users/{user_id}/groups/{grupo_id}"
            async with httpx.AsyncClient() as client:
                join_response = await client.put(
                    grupos_url,
                    headers=headers
                )
                join_response.raise_for_status()
            
        
        except Exception as e:
            raise Exception(f"Error al asignar grupo: {str(e)}")
    
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
        "success": True,
        "detail": "Creación correcta"
    }