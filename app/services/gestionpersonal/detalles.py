import httpx
from app.schemas.authenticated_user import AuthenticatedUser

from app.services.funcioneskeycloak.get_admin_base_url import get_admin_base_url
from app.services.funcioneskeycloak.get_admin_token import get_admin_token

from app.config.db import SessionLocal
from app.models.usuarios import Usuarios

async def procesar_detalles(user: AuthenticatedUser): 
    roles = user.roles if user.roles else []
    
    permisos = []
    
    for rol in roles:
        if rol.startswith("PERMISO_"):
            permisos.append({"nombre": rol})
    
    grupos = []
    try:
        token = await get_admin_token()
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        grupos_url = (
            f"{get_admin_base_url()}"
            f"/users/{user.id}/groups"
        )
        
        async with httpx.AsyncClient() as client:
            grupos_response = await client.get(
                grupos_url,
                headers=headers
            )
            
            grupos_response.raise_for_status()
        
        grupos = [
            {"nombre": grupo["name"]}
            for grupo in grupos_response.json()
        ]
    
    except Exception as e:
        grupos = []
    
    legajo = 0
    dni = 0
    
    try:
        db = SessionLocal()
        usuario_db = db.query(Usuarios).filter(Usuarios.id == user.id).first()
        db.close()
        
        if usuario_db:
            legajo = usuario_db.legajo if usuario_db.legajo is not None else 0
            dni = usuario_db.dni if usuario_db.dni is not None else 0
    
    except Exception as e:
        legajo = 0
        dni = 0
    
    return {
        "id": user.id,
        "email": user.email,
        "nombre": user.first_name,
        "apellido": user.last_name,
        "legajo": legajo,
        "dni": dni,
        "grupos": grupos,
        "permisos": permisos
    }
