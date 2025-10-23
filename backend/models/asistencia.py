"""
Modelo de Asistencia
Registra la asistencia de estudiantes a las sesiones de clase.
"""
from sqlalchemy import (
    Column, Integer, Date, ForeignKey,
    Enum as SQLEnum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
import enum

from db.base import Base


class EstadoAsistencia(str, enum.Enum):
    """Estado de asistencia de un estudiante"""
    PRESENTE = "Presente"
    AUSENTE = "Ausente"
    JUSTIFICADO = "Justificado"
    TARDANZA = "Tardanza"


class Asistencia(Base):
    """
    Modelo de Asistencia.
    
    Registra la asistencia (Presente, Ausente, etc.) de un estudiante
    en una fecha específica para un grupo.
    
    Relaciones:
    - Pertenece a una Inscripción (N:1) - el estudiante en el grupo
    - Pertenece a un Grupo (N:1) - denormalizado para optimizar consultas
    """
    
    __tablename__ = "asistencia" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    inscripcion_id = Column(
        Integer,
        ForeignKey("inscripcion.id", ondelete="CASCADE"),
        nullable=False,
        comment="Referencia a la inscripción (el estudiante en el grupo)"
    )
    fecha = Column(
        Date,
        nullable=False,
        comment="Día específico de la toma de asistencia"
    )
    estado = Column(
        SQLEnum(EstadoAsistencia, name="estado_asistencia"),
        nullable=False
    )
    grupo_id = Column(
        Integer,
        ForeignKey("grupo.id", ondelete="CASCADE"),
        nullable=False,
        comment="Referencia denormalizada al grupo para optimizar consultas de lista de asistencia"
    )
    
    __table_args__ = (
        UniqueConstraint(
            "inscripcion_id", "fecha",
            name="uq_asistencia_estudiante_fecha"
        ),
        
        Index("idx_asistencia_grupo_fecha", "grupo_id", "fecha"),
    )
    
    inscripcion = relationship(
        "Inscripcion",
        back_populates="asistencias"
    )
    grupo = relationship(
        "Grupo",
        back_populates="asistencias"
    )
    
    def __repr__(self) -> str:
        return (
            f"Asistencia(id={self.id}, inscripcion_id={self.inscripcion_id}, "
            f"fecha={self.fecha}, estado={self.estado.value})"
        )
