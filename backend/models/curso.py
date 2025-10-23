"""
Modelo de Curso
Representa las materias o asignaturas del plan de estudios.
"""
from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from db.base import Base


class EstadoCurso(str, enum.Enum):
    """Estado de un curso en el catálogo"""
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    EN_REVISION = "En Revision"


class Curso(Base):
    """
    Modelo de Curso.
    
    Representa una materia o asignatura del plan de estudios
    (ej. Cálculo I, Introducción a la Programación).
    
    Relaciones:
    - Pertenece a una Facultad (N:1)
    - Tiene muchos Grupos (1:N) - instancias del curso en diferentes semestres
    
    Nota: Un Curso es la definición general de la materia.
    Un Grupo es una instancia específica del curso en un semestre con un profesor.
    """
    
    __tablename__ = "curso" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(
        String(30),
        unique=True,
        nullable=False,
        comment="Código único de la asignatura, ej: IS-101"
    )
    nombre = Column(
        String(200),
        nullable=False,
        comment="Nombre del curso, ej: Cálculo I"
    )
    facultad_id = Column(
        Integer,
        ForeignKey("facultad.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Facultad a la que pertenece el curso"
    )
    estado = Column(
        SQLEnum(EstadoCurso, name="estado_curso"),
        nullable=False,
        default=EstadoCurso.ACTIVO,
        comment="Estado del curso en el catálogo"
    )
    
    facultad = relationship(
        "Facultad",
        back_populates="cursos"
    )
    grupos = relationship(
        "Grupo",
        back_populates="curso",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return (
            f"Curso(id={self.id}, codigo='{self.codigo}', "
            f"nombre='{self.nombre}', estado={self.estado.value})"
        )
