"""
Modelo de Profesor
Representa el perfil con datos específicos para usuarios con rol de Profesor.
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db.base import Base


class Profesor(Base):
    """
    Modelo de Profesor (Perfil).
    
    Almacena los datos específicos del perfil de un usuario con rol de Profesor.
    Esta es una relación 1:1 con Usuario.
    
    Relaciones:
    - Pertenece a un Usuario (1:1)
    - Pertenece a una Facultad (N:1) - opcional
    - Tiene muchos Grupos (1:N) - grupos que dicta
    """
    
    __tablename__ = "profesor" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuario.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Referencia única al usuario (relación 1:1)"
    )
    documento = Column(
        String(50),
        nullable=True,
        comment="Número de documento de identidad del profesor"
    )
    tipo_documento = Column(
        String(50),
        nullable=True,
        comment="Tipo de documento (ej: Cédula, Pasaporte, TI)"
    )
    facultad_id = Column(
        Integer,
        ForeignKey("facultad.id", ondelete="SET NULL"),
        nullable=True,
        comment="Facultad a la que está adscrito el profesor (opcional)"
    )
    titulo_academico = Column(
        String(255),
        nullable=True,
        comment="Título académico del profesor (ej: PhD en Matemáticas, Magíster en Ingeniería)"
    )
    
    usuario = relationship(
        "Usuario",
        back_populates="profesor",
        uselist=False
    )
    facultad = relationship(
        "Facultad",
        back_populates="profesores"
    )
    grupos = relationship(
        "Grupo",
        back_populates="profesor"
    )
    
    def __repr__(self) -> str:
        return (
            f"Profesor(id={self.id}, usuario_id={self.usuario_id}, "
            f"facultad_id={self.facultad_id}, titulo_academico='{self.titulo_academico}')"
        )
