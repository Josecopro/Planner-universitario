"""
Modelo de Rol
Catálogo de roles para el control de acceso en el sistema.
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from db.base import Base


class Rol(Base):
    """
    Modelo de Rol.
    
    Catálogo de roles para el control de acceso en el sistema
    (Superadmin, Profesor, Estudiante, etc.).
    
    Relaciones:
    - Tiene muchos Usuarios (1:N) - usuarios con este rol
    """
    
    __tablename__ = "rol" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(
        String(50),
        unique=True,
        nullable=False,
        comment="Nombre único del rol, ej: Superadmin, Profesor, Estudiante"
    )
    descripcion = Column(
        Text,
        nullable=True,
        comment="Descripción detallada de los permisos y funciones del rol"
    )
    
    usuarios = relationship(
        "Usuario",
        back_populates="rol"
    )
    
    def __repr__(self) -> str:
        return f"Rol(id={self.id}, nombre='{self.nombre}')"
