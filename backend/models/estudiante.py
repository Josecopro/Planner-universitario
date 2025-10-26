"""
Modelo de Estudiante
Representa el perfil con datos específicos para usuarios con rol de Estudiante.
"""
from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from db.base import Base


class EstadoAcademicoEstudiante(str, enum.Enum):
    """Estado académico de un estudiante"""
    MATRICULADO = "Matriculado"
    RETIRADO = "Retirado"
    GRADUADO = "Graduado"
    EN_PRUEBA_ACADEMICA = "En Prueba Academica"


class Estudiante(Base):
    """
    Modelo de Estudiante (Perfil).
    
    Almacena los datos específicos del perfil de un usuario con rol de Estudiante.
    Esta es una relación 1:1 con Usuario.
    
    Relaciones:
    - Pertenece a un Usuario (1:1)
    - Pertenece a un ProgramaAcademico (N:1)
    - Tiene muchas Inscripciones (1:N) - inscripciones a grupos
    """
    
    __tablename__ = "estudiante" # type: ignore
    
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
        comment="Número de documento de identidad del estudiante"
    )
    tipo_documento = Column(
        String(50),
        nullable=True,
        comment="Tipo de documento (ej: Cédula, Pasaporte, TI)"
    )
    programa_id = Column(
        Integer,
        ForeignKey("programaacademico.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Programa académico en el que está inscrito el estudiante"
    )
    estado_academico = Column(
        SQLEnum(EstadoAcademicoEstudiante, name="estado_academico_estudiante"),
        nullable=False,
        default=EstadoAcademicoEstudiante.MATRICULADO,
        comment="Estado académico actual del estudiante"
    )
    
    usuario = relationship(
        "Usuario",
        back_populates="estudiante",
        uselist=False
    )
    programa = relationship(
        "ProgramaAcademico",
        back_populates="estudiantes"
    )
    inscripciones = relationship(
        "Inscripcion",
        back_populates="estudiante",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return (
            f"Estudiante(id={self.id}, usuario_id={self.usuario_id}, "
            f"programa_id={self.programa_id}, estado_academico={self.estado_academico.value})"
        )
