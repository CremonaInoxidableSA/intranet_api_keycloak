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

logger = logging.getLogger(__name__)

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

    GRUPOS_PERMITIDOS = {"GRUPO_ENCARGADOS_PRODUCCION", "GRUPO_OPERARIOS_PRODUCCION"}
    if grupo is not None:
        if grupo not in GRUPOS_PERMITIDOS:
            raise Exception(f"El grupo '{grupo}' no es permitido. Solo se permiten: {', '.join(GRUPOS_PERMITIDOS)}")
    
    logger.info(f"Iniciando creación de usuario - Username: {username}, Email: {email}, Nombre: {first_name}, Apellido: {last_name}, DNI: {dni}, Legajo: {legajo}, Grupo: {grupo}")
    
    db = SessionLocal()
    try:
        logger.debug(f"Consultando base de datos - DNI: {dni}, Legajo: {legajo}")
        query = db.query(Usuarios)
        
        if dni is not None and legajo is not None:
            logger.debug(f"Búsqueda por DNI y Legajo")
            usuario_existente = query.filter(
                (Usuarios.dni == dni) | (Usuarios.legajo == legajo)
            ).first()
        elif dni is not None:
            logger.debug(f"Búsqueda por DNI: {dni}")
            usuario_existente = query.filter(Usuarios.dni == dni).first()
        else:
            logger.debug(f"Búsqueda por Legajo: {legajo}")
            usuario_existente = query.filter(Usuarios.legajo == legajo).first()
        
        db.close()
        
        if usuario_existente:
            logger.info(f"Usuario existente encontrado en BD - ID: {usuario_existente.id}, DNI: {usuario_existente.dni}, Legajo: {usuario_existente.legajo}")
            
            # Verificar si el usuario tiene grupos de producción en Keycloak
            try:
                token = await get_admin_token()
                headers = {
                    "Authorization": f"Bearer {token}"
                }
                
                grupos_url = f"{get_admin_base_url()}/users/{usuario_existente.id}/groups"
                logger.debug(f"Consultando grupos del usuario en Keycloak - URL: {grupos_url}")
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        grupos_url,
                        headers=headers
                    )
                    response.raise_for_status()
                    
                    grupos = response.json()
                    nombres_grupos = {g.get("name") for g in grupos}
                    logger.debug(f"Grupos obtenidos: {nombres_grupos}")
                    
                    tiene_grupo_produccion = bool(nombres_grupos.intersection(GRUPOS_PERMITIDOS))
                    logger.debug(f"¿Tiene grupo de Producción?: {tiene_grupo_produccion}")
                
                if tiene_grupo_produccion:
                    logger.warning(f"Usuario existente en Producción - Code: EXISTE_PRODUCCION")
                    return {
                        "success": False,
                        "code": "EXISTE_PRODUCCION",
                        "detail": f"El DNI o LEGAJO ingresado ya se encuentra asignado a un usuario perteneciente al sistema de Producción.",
                        "id": usuario_existente.id
                    }
            except Exception as e:
                logger.warning(f"Error al consultar grupos en Keycloak (ID: {usuario_existente.id}): {str(e)}")
                # Si hay error al consultar grupos, asumir que no es de producción
                pass
            
            logger.warning(f"Usuario existente General - Code: EXISTE_GENERAL")
            return {
                "success": False,
                "code": "EXISTE_GENERAL",
                "detail": f"El DNI o LEGAJO ingresado ya se encuentra asignado a un usuario perteneciente a la intranet.",
                "id": usuario_existente.id
            }
    except Exception as e:
        logger.error(f"Error verificando usuarios existentes - DNI: {dni}, Legajo: {legajo}, Error: {str(e)}", exc_info=True)
        db.close()
        raise Exception(f"Error verificando usuarios existentes: {str(e)}")
    
    try:
        token = await get_admin_token()

        url = (
            f"{get_admin_base_url()}"
            "/users"
        )
        
        logger.debug(f"Verificando si el email ya existe en Keycloak: {email}")
        
        # Verificar si el email ya existe EN KEYCLOAK
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
                logger.warning(f"Email duplicado encontrado en Keycloak - Email: {email}, Usuarios encontrados: {len(usuarios_con_email)}")
                return {
                    "success": False,
                    "code": "EMAIL_DUPLICADO",
                    "detail": f"El email '{email}' ya se encuentra registrado en el sistema."
                }
        
        logger.debug(f"Email disponible. Procediendo a crear usuario en Keycloak")
        
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
        logger.info(f"Usuario creado en Keycloak - ID: {user_id}, Email: {email}")
    
    except Exception as e:
        logger.error(f"Error al crear usuario en Keycloak - Email: {email}, Error: {str(e)}", exc_info=True)
        raise Exception(f"Falla en creación general: {str(e)}")
    
    if grupo is not None:
        try:
            logger.debug(f"Asignando grupo '{grupo}' al usuario {user_id}")
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
                    logger.error(f"El grupo '{grupo}' no existe en Keycloak")
                    raise Exception(f"El grupo '{grupo}' no existe en Keycloak")
            
            grupo_id = grupo_encontrado["id"]
            logger.debug(f"Grupo encontrado - Nombre: {grupo}, ID: {grupo_id}")
            
            grupos_url = f"{get_admin_base_url()}/users/{user_id}/groups/{grupo_id}"
            async with httpx.AsyncClient() as client:
                join_response = await client.put(
                    grupos_url,
                    headers=headers
                )
                join_response.raise_for_status()
            
            logger.info(f"Grupo asignado exitosamente - Usuario: {user_id}, Grupo: {grupo}")
        
        except Exception as e:
            logger.error(f"Error al asignar grupo - Usuario: {user_id}, Grupo: {grupo}, Error: {str(e)}", exc_info=True)
            raise Exception(f"Error al asignar grupo: {str(e)}")
    
    if dni is not None and legajo is not None:
        db = SessionLocal()
        try:
            logger.debug(f"Guardando datos en BD - User ID: {user_id}, DNI: {dni}, Legajo: {legajo}")
            nuevo_usuario = Usuarios(
                id=user_id,
                dni=dni,
                legajo=legajo
            )
            
            db.add(nuevo_usuario)
            db.commit()
            db.close()
            
            logger.info(f"Usuario guardado en BD - ID: {user_id}, DNI: {dni}, Legajo: {legajo}")
            
        except Exception as db_error:
            db.close()
            logger.error(f"Error al guardar usuario en BD - User ID: {user_id}, DNI: {dni}, Legajo: {legajo}, Error: {str(db_error)}", exc_info=True)
            raise Exception(f"Falla en creación en base de datos: {str(db_error)}")
    
    logger.info(f"Usuario creado exitosamente - ID: {user_id}, Email: {email}, DNI: {dni}, Legajo: {legajo}")

    return {
        "success": True,
        "detail": "Creación correcta"
    }