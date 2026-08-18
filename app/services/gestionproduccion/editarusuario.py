import httpx
from typing import Optional

from app.services.funcioneskeycloak.get_admin_base_url import get_admin_base_url
from app.services.funcioneskeycloak.get_admin_token import get_admin_token
from app.services.funcioneskeycloak.get_user import get_user

from app.config.db import SessionLocal
from app.models.usuarios import Usuarios

async def editar_usuario(
    user_id: str,
    email: Optional[str] = None,
    nombre: Optional[str] = None,
    apellido: Optional[str] = None,
    legajo: Optional[int] = None,
    dni: Optional[int] = None,
    grupo: Optional[str] = None
):
    
    if grupo is not None:
        GRUPOS_PERMITIDOS = {"GRUPO_ENCARGADOS_PRODUCCION", "GRUPO_OPERARIOS_PRODUCCION"}
        
        if grupo not in GRUPOS_PERMITIDOS:
            raise Exception(f"El grupo '{grupo}' no es permitido. Solo se permiten: {', '.join(GRUPOS_PERMITIDOS)}")
    
    if dni is not None or legajo is not None:
        db = SessionLocal()
        try:
            query = db.query(Usuarios).filter(Usuarios.id != user_id)
            
            if dni is not None and legajo is not None:
                usuario_duplicado = query.filter(
                    (Usuarios.dni == dni) | (Usuarios.legajo == legajo)
                ).first()
            elif dni is not None:
                usuario_duplicado = query.filter(Usuarios.dni == dni).first()
            else:
                usuario_duplicado = query.filter(Usuarios.legajo == legajo).first()
            
            db.close()
            
            if usuario_duplicado:
                return {
                    "success": False,
                    "detail": "No se puede asignar este DNI o legajo debido a que ya pertenecen a otro usuario registrado."
                }
        except Exception as e:
            db.close()
            raise Exception(f"Error verificando duplicados: {str(e)}")
    
    token = await get_admin_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    user_url = f"{get_admin_base_url()}/users/{user_id}"
    body = {}
    
    if email is not None:
        body["email"] = email
    
    if nombre is not None:
        body["firstName"] = nombre
    
    if apellido is not None:
        body["lastName"] = apellido
    
    if body:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                user_url,
                json=body,
                headers=headers
            )
            response.raise_for_status()
    
    if grupo is not None:
        GRUPOS_PERMITIDOS = {"GRUPO_ENCARGADOS_PRODUCCION", "GRUPO_OPERARIOS_PRODUCCION"}
        
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
                raise Exception(f"El grupo '{grupo}' no existe o no es permitido")
        
        grupos_url = f"{get_admin_base_url()}/users/{user_id}/groups"
        
        async with httpx.AsyncClient() as client:
            grupos_response = await client.get(
                grupos_url,
                headers=headers
            )
            grupos_response.raise_for_status()
            
            grupos_actuales = grupos_response.json()
            
            # Eliminar grupos permitidos anteriores
            for grupo_actual in grupos_actuales:
                if grupo_actual["name"] in GRUPOS_PERMITIDOS:
                    delete_response = await client.delete(
                        f"{grupos_url}/{grupo_actual['id']}",
                        headers=headers
                    )
                    delete_response.raise_for_status()
            
            # Asignar el nuevo grupo
            grupo_id = grupo_encontrado["id"]
            join_response = await client.put(
                f"{grupos_url}/{grupo_id}",
                headers=headers
            )
            join_response.raise_for_status()
    
    if legajo is not None or dni is not None:
        try:
            db = SessionLocal()
            usuario_db = db.query(Usuarios).filter(Usuarios.id == user_id).first()
            
            if usuario_db:
                if legajo is not None:
                    usuario_db.legajo = legajo
                if dni is not None:
                    usuario_db.dni = dni
                
                db.commit()
            
            db.close()
        except Exception as e:
            raise Exception(f"Error al actualizar datos en base de datos: {str(e)}")
    
    return {
        "id": user_id,
        "detail": "Usuario actualizado exitosamente"
    }