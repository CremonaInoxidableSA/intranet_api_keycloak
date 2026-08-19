import asyncio
from app.config.db import SessionLocal
from app.models.modulos import Modulos
from app.models.submodulos import Submodulos


def obtener_datos_submodulos_db(nombres_submodulos: list[str], modulo_padre: str):
    """
    Obtiene los datos de submodulos específicos de la base de datos
    filtrando por nombre y módulo padre.
    """
    try:
        db = SessionLocal()
        
        submodulos = db.query(Submodulos).filter(
            Submodulos.nombre.in_(nombres_submodulos),
            Submodulos.modulo_padre == modulo_padre,
            Submodulos.habilitado == 1
        ).all()
        
        modulo_padre_data = db.query(Modulos).filter(
            Modulos.nombre == modulo_padre
        ).first()
        
        db.close()
        
        submodulos_dict = {}
        for submodulo in submodulos:
            submodulos_dict[submodulo.nombre] = {
                "path": submodulo.path,
                "icono": submodulo.icono,
                "subdominio": modulo_padre_data.subdominio if modulo_padre_data else ""
            }
        
        return submodulos_dict
    
    except Exception as e:
        return {}


async def obtener_submodulos_usuario(roles: list[str], modulo_padre: str):
    """
    Obtiene los submodulos asignados al usuario basado en sus roles
    y filtrando por el módulo padre especificado.
    """
    
    try:
        submodulos_usuario = [rol for rol in roles if rol.startswith("SUBMODULO_")]
        
        if not submodulos_usuario:
            return {}
        
        submodulos_db = await asyncio.to_thread(
            obtener_datos_submodulos_db,
            submodulos_usuario,
            modulo_padre
        )
        
        resultado = {}
        for submodulo_nombre in submodulos_usuario:
            if submodulo_nombre in submodulos_db:
                db_data = submodulos_db[submodulo_nombre]
                resultado[submodulo_nombre] = {
                    "path": f"{db_data['path']}",
                    "icono": db_data["icono"]
                }
        
        return resultado
    
    except Exception as e:
        raise Exception(f"Error al obtener submodulos personales: {str(e)}")