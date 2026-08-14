import httpx
from sqlalchemy import text

from app.config.db import SessionLocal
from app.core.config import settings

async def verificar_conexiones():
    try:
        url = (
            f"{settings.KEYCLOAK_URL}"
            f"/realms/{settings.KEYCLOAK_REALM}"
            "/.well-known/openid-configuration"
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=5.0)
            response.raise_for_status()
    except Exception as e:
        raise Exception(f"Error de conexión con Keycloak: {str(e)}")
    
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        raise Exception(f"Error de conexión con Base de Datos: {str(e)}")