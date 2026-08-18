from fastapi import FastAPI, Depends

from app.core.config import settings

from app.routers.usuarios import detalles
from app.routers.usuarios import usuarios
from app.routers.usuarios import estadousuarios
from app.routers.usuarios import reestablecercontraseña
from app.routers.usuarios import gestionpersonal
from app.routers.usuarios import listausuarios
from app.routers.usuarios import detalleusuario
from app.routers.usuarios import editarusuario
from app.routers.usuarios import eliminarusuario
from app.routers.usuarios import modulospersonales
from app.routers.usuarios import submodulospersonales


from app.routers.permisos import listagrupos
from app.routers.permisos import listamodulos
from app.routers.permisos import listasubmodulos
from app.routers.permisos import listapermisos
from app.routers.permisos import crearmodulos
from app.routers.permisos import crearsubmodulos
from app.routers.permisos import crearpermiso
from app.routers.permisos import editarmodulos
from app.routers.permisos import editarsubmodulos
from app.routers.permisos import editarpermisos
from app.routers.permisos import creargrupos
from app.routers.permisos import editargrupos
from app.routers.permisos import estadomodulos
from app.routers.permisos import estadosubmodulos
from app.routers.permisos import detallegrupos
from app.routers.permisos import detallemodulos
from app.routers.permisos import detallesubmodulos
from app.routers.permisos import detallepermisos
from app.routers.permisos import eliminargrupos
from app.routers.permisos import eliminarmodulos
from app.routers.permisos import eliminarsubmodulos
from app.routers.permisos import eliminarpermisos

from app.routers.produccion import detallesusuariosproduccion
from app.routers.produccion import crearusuarioproduccion
from app.routers.produccion import listausuariosproduccion
from app.routers.produccion import editarusuarioproduccion
from app.routers.produccion import asignargrupoproduccion
from app.routers.produccion import eliminarusuarioproduccion

#Cosas MYSQL
from sqlalchemy import create_engine, text 
from urllib.parse import quote_plus
from app.config import db
from app.config.sql_loader import cargar_datos_iniciales

import os
from dotenv import load_dotenv

from app.models.usuarios import Usuarios
from app.models.modulos import Modulos
from app.models.submodulos import Submodulos

load_dotenv()

with create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{quote_plus(os.getenv('DB_PASSWORD', ''))}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
).connect() as connection:
    connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}"))
    print(f"✓ Base de datos '{os.getenv('DB_NAME')}' verificada o creada exitosamente")

#db.Base.metadata.drop_all(bind=db.engine)
#db.Base.metadata.create_all(bind=db.engine)
#cargar_datos_iniciales()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

app.include_router(detalles.router)
app.include_router(gestionpersonal.router)


app.include_router(detallesusuariosproduccion.router)
app.include_router(listausuariosproduccion.router)
app.include_router(crearusuarioproduccion.router)
app.include_router(asignargrupoproduccion.router)
app.include_router(eliminarusuarioproduccion.router)
app.include_router(editarusuarioproduccion.router)


app.include_router(usuarios.router)
app.include_router(estadousuarios.router)
app.include_router(editarusuario.router)
app.include_router(reestablecercontraseña.router)
app.include_router(listausuarios.router)
app.include_router(detalleusuario.router)
app.include_router(eliminarusuario.router)


app.include_router(modulospersonales.router)
app.include_router(submodulospersonales.router)
app.include_router(listagrupos.router)
app.include_router(listamodulos.router)
app.include_router(listasubmodulos.router)
app.include_router(listapermisos.router)
app.include_router(detallegrupos.router)
app.include_router(detallemodulos.router)
app.include_router(detallesubmodulos.router)
app.include_router(detallepermisos.router)
app.include_router(creargrupos.router)
app.include_router(crearmodulos.router)
app.include_router(crearsubmodulos.router)
app.include_router(crearpermiso.router)
app.include_router(editargrupos.router)
app.include_router(editarmodulos.router)
app.include_router(editarsubmodulos.router)
app.include_router(editarpermisos.router)
app.include_router(estadomodulos.router)
app.include_router(estadosubmodulos.router)
app.include_router(eliminargrupos.router)
app.include_router(eliminarmodulos.router)
app.include_router(eliminarsubmodulos.router)
app.include_router(eliminarpermisos.router)