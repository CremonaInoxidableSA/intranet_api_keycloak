from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.config.db import Base

class Usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(String(255), primary_key=True, nullable=False)
    legajo = Column(Integer, nullable=True, unique=True)
    dni = Column(Integer, nullable=True, unique=True)