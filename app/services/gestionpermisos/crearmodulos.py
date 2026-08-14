import httpx
from sqlalchemy import text

from app.services.funcioneskeycloak.create_realm_role import create_realm_role
from app.services.funcioneskeycloak.get_admin_base_url import get_admin_base_url
from app.services.funcioneskeycloak.get_admin_token import get_admin_token
from app.services.funcioneskeycloak.get_realm_role import get_realm_role

from app.services.funcioneskeycloak.verificar_conexiones import verificar_conexiones

from app.config.db import SessionLocal
from app.models.modulos import Modulos
from app.core.config import settings


async def crear_modulo(
    nombre: str,
    subdominio: str,
    path: str,
    icono: str | None = None,
    habilitado: bool = True
):
    """
    Crea un módulo en Keycloak y MySQL.
    """
    
    await verificar_conexiones()
    
    if not nombre.startswith("MODULO_"):
        raise Exception("El módulo debe contar con 'MODULO_' de prefijo.")
    
    role_name = nombre.upper()
    
    try:
        await get_realm_role(role_name)
        raise Exception("El módulo ya existe en Keycloak.")
    except Exception as e:
        if "ya existe en Keycloak" in str(e):
            raise
    
    db = SessionLocal()
    try:
        modulo_existente = db.query(Modulos).filter(
            (Modulos.nombre == role_name) & (Modulos.path == path)
        ).first()
        
        if modulo_existente:
            db.close()
            raise Exception("El módulo/path ya existe en la base de datos.")
    finally:
        db.close()
    
    try:
        await create_realm_role(
            role_name=role_name
        )
    except Exception as e:
        error_str = str(e)
        if "409" in error_str or "Conflict" in error_str:
            raise Exception("El módulo ya existe en Keycloak.")
        else:
            raise Exception(f"Error en Keycloak: {error_str}")
    
    db = SessionLocal()
    try:
        nuevo_modulo = Modulos(
            nombre=role_name,
            subdominio=subdominio,
            path=path,
            icono=icono,
            habilitado=habilitado
        )
        
        db.add(nuevo_modulo)
        db.commit()
        
        modulo_id = nuevo_modulo.id
        
        db.close()
        
    except Exception as db_error:
        db.close()
        error_str = str(db_error)
        if "Duplicate entry" in error_str or "1062" in error_str:
            raise Exception("El módulo ya existe en la base de datos.")
        else:
            raise Exception(f"Error en base de datos: {error_str}")
    
    return {
        "id": modulo_id,
        "nombre": role_name,
        "subdominio": subdominio,
        "path": path,
        "icono": icono,
        "habilitado": habilitado
    }
