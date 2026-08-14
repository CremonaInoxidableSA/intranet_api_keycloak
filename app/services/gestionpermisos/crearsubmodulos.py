import httpx
from sqlalchemy import text

from app.services.funcioneskeycloak.create_realm_role import create_realm_role
from app.services.funcioneskeycloak.get_admin_base_url import get_admin_base_url
from app.services.funcioneskeycloak.get_admin_token import get_admin_token
from app.services.funcioneskeycloak.get_realm_role import get_realm_role

from app.services.funcioneskeycloak.verificar_conexiones import verificar_conexiones

from app.config.db import SessionLocal
from app.models.submodulos import Submodulos
from app.core.config import settings
from app.models.modulos import Modulos

async def crear_submodulo(
    modulo_padre: str,
    nombre: str,
    path: str,
    icono: str | None = None,
    habilitado: bool = True
):
    """
    Crea un submódulo en Keycloak y MySQL.
    """
    
    await verificar_conexiones()
    
    if not nombre.startswith("SUBMODULO_"):
        raise Exception("El submódulo debe contar con 'SUBMODULO_' de prefijo.")
    
    role_name = nombre.upper()
    
    try:
        await get_realm_role(role_name)
        raise Exception("El submódulo ya existe en Keycloak.")
    except Exception as e:
        if "ya existe en Keycloak" in str(e):
            raise
    
    db = SessionLocal()
    try:
        submodulo_existente = db.query(Submodulos).filter(
            (Submodulos.nombre == role_name) & (Submodulos.path == path)
        ).first()
        
        if submodulo_existente:
            db.close()
            raise Exception("El submódulo/path ya existe en la base de datos.")
        
        modulo_padre_existente = db.query(Modulos).filter(
            Modulos.nombre == modulo_padre
        ).first()

        if not modulo_padre_existente:
            db.close()
            raise Exception("El módulo padre no existe en la base de datos.")

    finally:
        db.close()
    
    try:
        await create_realm_role(
            role_name=role_name
        )
    except Exception as e:
        error_str = str(e)
        if "409" in error_str or "Conflict" in error_str:
            raise Exception("El submódulo ya existe en Keycloak.")
        else:
            raise Exception(f"Error en Keycloak: {error_str}")
    
    db = SessionLocal()
    try:
        nuevo_submodulo = Submodulos(
            modulo_padre=modulo_padre,
            nombre=role_name,
            path=path,
            icono=icono,
            habilitado=habilitado
        )
        
        db.add(nuevo_submodulo)
        db.commit()
        
        submodulo_id = nuevo_submodulo.id
        
        db.close()
        
    except Exception as db_error:
        db.close()
        error_str = str(db_error)
        if "Duplicate entry" in error_str or "1062" in error_str:
            raise Exception("El submódulo ya existe en la base de datos.")
        else:
            raise Exception(f"Error en base de datos: {error_str}")
    
    return {
        "id": submodulo_id,
        "modulo_padre": modulo_padre,
        "nombre": role_name,
        "path": path,
        "icono": icono,
        "habilitado": habilitado 
    }
