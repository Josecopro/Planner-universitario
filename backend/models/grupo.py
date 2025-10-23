"""
Modelo de Grupo
Representa una instancia específica de un Curso en un semestre/periodo.
"""
from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from db.base import Base


class EstadoGrupo(str, enum.Enum):
    """Estado de un grupo en el semestre"""
    PROGRAMADO = "Programado"
    ABIERTO = "Abierto"
    CERRADO = "Cerrado"
    EN_CURSO = "En Curso"
    FINALIZADO = "Finalizado"
    CANCELADO = "Cancelado"


class Grupo(Base):
    """
    Modelo de Grupo.
    
    Representa una instancia específica de un Curso en un semestre/periodo,
    con un profesor asignado y cupos de estudiantes.
    
    Relaciones:
    - Pertenece a un Curso (N:1)
    - Pertenece a un Profesor (N:1) - opcional
    - Tiene muchos Horarios (1:N) - bloques de día/hora/salón
    - Tiene muchas Inscripciones (1:N) - estudiantes inscritos
    - Tiene muchas ActividadesEvaluativas (1:N) - tareas, exámenes
    - Tiene muchas Asistencias (1:N) - registros de asistencia
    """
    
    __tablename__ = "grupo" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    curso_id = Column(
        Integer,
        ForeignKey("curso.id", ondelete="CASCADE"),
        nullable=False,
        comment="Curso que se está dictando"
    )
    profesor_id = Column(
        Integer,
        ForeignKey("profesor.id", ondelete="SET NULL"),
        nullable=True,
        comment="Profesor asignado al grupo (puede estar sin asignar)"
    )
    semestre = Column(
        String(20),
        nullable=False,
        comment="Periodo académico, ej: 2025-1, 2025-2"
    )
    cupo_maximo = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Número máximo de estudiantes permitidos"
    )
    cupo_actual = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Número actual de estudiantes inscritos"
    )
    estado = Column(
        SQLEnum(EstadoGrupo, name="estado_grupo"),
        nullable=False,
        default=EstadoGrupo.PROGRAMADO,
        comment="Estado actual del grupo"
    )
    
    __table_args__ = (
        CheckConstraint(
            "cupo_actual >= 0 AND cupo_maximo >= cupo_actual",
            name="chk_cupos_logicos"
        ),
    )
    
    curso = relationship(
        "Curso",
        back_populates="grupos"
    )
    profesor = relationship(
        "Profesor",
        back_populates="grupos"
    )
    horarios = relationship(
        "Horario",
        back_populates="grupo",
        cascade="all, delete-orphan"
    )
    inscripciones = relationship(
        "Inscripcion",
        back_populates="grupo",
        cascade="all, delete-orphan"
    )
    actividades_evaluativas = relationship(
        "ActividadEvaluativa",
        back_populates="grupo",
        cascade="all, delete-orphan"
    )
    asistencias = relationship(
        "Asistencia",
        back_populates="grupo",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return (
            f"Grupo(id={self.id}, curso_id={self.curso_id}, "
            f"semestre='{self.semestre}', estado={self.estado.value}, "
            f"cupo_actual={self.cupo_actual}/{self.cupo_maximo})"
        )
