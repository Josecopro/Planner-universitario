"""
Modelo de Inscripción
Tabla de unión que registra qué estudiante está en qué grupo (M2M).
"""
from sqlalchemy import (
    Column, Integer, Numeric,
    ForeignKey, CheckConstraint, UniqueConstraint,
    Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from db.base import Base


class EstadoInscripcion(str, enum.Enum):
    """Estado de una inscripción"""
    INSCRITO = "Inscrito"
    RETIRADO = "Retirado"
    APROBADO = "Aprobado"
    REPROBADO = "Reprobado"
    CANCELADO = "Cancelado"


class Inscripcion(Base):
    """
    Modelo de Inscripción.
    
    Tabla de unión que registra qué estudiante está inscrito en qué grupo.
    Implementa la relación Many-to-Many entre Estudiante y Grupo.
    
    Relaciones:
    - Pertenece a un Estudiante (N:1)
    - Pertenece a un Grupo (N:1)
    - Tiene muchas Entregas (1:N) - entregas del estudiante en actividades del grupo
    - Tiene muchas Asistencias (1:N) - registros de asistencia del estudiante
    
    Restricción única: Un estudiante no puede inscribirse dos veces en el mismo grupo.
    """
    
    __tablename__ = "inscripcion" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    estudiante_id = Column(
        Integer,
        ForeignKey("estudiante.id", ondelete="CASCADE"),
        nullable=False,
        comment="Estudiante que se inscribe en el grupo"
    )
    grupo_id = Column(
        Integer,
        ForeignKey("grupo.id", ondelete="CASCADE"),
        nullable=False,
        comment="Grupo en el que se inscribe el estudiante"
    )
    fecha_inscripcion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Fecha y hora en que se realizó la inscripción"
    )
    estado = Column(
        SQLEnum(EstadoInscripcion, name="estado_inscripcion"),
        nullable=False,
        default=EstadoInscripcion.INSCRITO,
        comment="Estado actual de la inscripción"
    )
    nota_definitiva = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Nota final del estudiante en el grupo, calculada al finalizar el semestre"
    )
    
    __table_args__ = (
        UniqueConstraint(
            "estudiante_id", "grupo_id",
            name="uq_estudiante_grupo"
        ),
        CheckConstraint(
            "nota_definitiva IS NULL OR nota_definitiva >= 0.0",
            name="chk_nota_definitiva_logica"
        ),
    )
    
    estudiante = relationship(
        "Estudiante",
        back_populates="inscripciones"
    )
    grupo = relationship(
        "Grupo",
        back_populates="inscripciones"
    )
    entregas = relationship(
        "Entrega",
        back_populates="inscripcion",
        cascade="all, delete-orphan"
    )
    asistencias = relationship(
        "Asistencia",
        back_populates="inscripcion",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return (
            f"Inscripcion(id={self.id}, estudiante_id={self.estudiante_id}, "
            f"grupo_id={self.grupo_id}, estado={self.estado.value}, "
            f"nota_definitiva={self.nota_definitiva})"
        )
