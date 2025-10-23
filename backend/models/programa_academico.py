"""
Modelo de Programa Académico
Representa las carreras o programas de estudio ofrecidos por las facultades.
"""
from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from db.base import Base


class EstadoPrograma(str, enum.Enum):
    """Estado de un programa académico"""
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    EN_LIQUIDACION = "En Liquidacion"


class ProgramaAcademico(Base):
    """
    Modelo de Programa Académico.
    
    Representa las carreras o programas de estudio ofrecidos por las facultades
    (ej. Ingeniería de Sistemas, Ingeniería Civil, Medicina).
    
    Relaciones:
    - Pertenece a una Facultad (N:1)
    - Tiene muchos Estudiantes (1:N) - estudiantes inscritos en el programa
    """
    
    __tablename__ = "programaacademico" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(
        String(200),
        nullable=False,
        comment="Nombre del programa, ej: Ingeniería de Sistemas"
    )
    codigo = Column(
        String(30),
        unique=True,
        nullable=False,
        comment="Código único del programa, ej: IS, IC, MED"
    )
    facultad_id = Column(
        Integer,
        ForeignKey("facultad.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Facultad a la que pertenece el programa"
    )
    duracion_semestres = Column(
        Integer,
        nullable=True,
        comment="Duración del programa en semestres, ej: 10, 12"
    )
    estado = Column(
        SQLEnum(EstadoPrograma, name="estado_programa"),
        nullable=False,
        default=EstadoPrograma.ACTIVO,
        comment="Estado del programa académico"
    )
    
    facultad = relationship(
        "Facultad",
        back_populates="programas_academicos"
    )
    estudiantes = relationship(
        "Estudiante",
        back_populates="programa",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return (
            f"ProgramaAcademico(id={self.id}, codigo='{self.codigo}', "
            f"nombre='{self.nombre}', duracion_semestres={self.duracion_semestres}, "
            f"estado={self.estado.value})"
        )
