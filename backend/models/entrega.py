"""
Modelo de Entrega
Representa la sumisión de un estudiante para una actividad evaluativa.
"""
from sqlalchemy import (
    Column, Integer, Text, ForeignKey,
    Enum as SQLEnum, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from db.base import Base


class EstadoEntrega(str, enum.Enum):
    """Estado de una entrega"""
    PENDIENTE = "Pendiente"
    ENTREGADA = "Entregada"
    ENTREGADA_TARDE = "Entregada Tarde"
    CALIFICADA = "Calificada"


class Entrega(Base):
    """
    Modelo de Entrega.
    
    Representa la sumisión de un estudiante para una actividad evaluativa.
    Incluye el contenido de la entrega, archivos adjuntos y metadata.
    
    Relaciones:
    - Pertenece a una ActividadEvaluativa (N:1)
    - Pertenece a una Inscripción (N:1) - identifica al estudiante
    - Tiene una Calificación (1:1) - opcional, solo si ya fue calificada
    
    Restricción única: Un estudiante (inscripción) solo puede entregar
    una vez por actividad.
    """
    
    __tablename__ = "entrega" # type: ignore
    
    # Columnas
    id = Column(Integer, primary_key=True, autoincrement=True)
    actividad_id = Column(
        Integer,
        ForeignKey("actividadevaluativa.id", ondelete="CASCADE"),
        nullable=False,
        comment="Actividad que se está entregando"
    )
    inscripcion_id = Column(
        Integer,
        ForeignKey("inscripcion.id", ondelete="CASCADE"),
        nullable=False,
        comment="Referencia a la inscripción del estudiante en el grupo"
    )
    fecha_entrega = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Fecha y hora en que se realizó la entrega"
    )
    estado = Column(
        SQLEnum(EstadoEntrega, name="estado_entrega"),
        nullable=False,
        default=EstadoEntrega.ENTREGADA,
        comment="Estado de la entrega"
    )
    texto_entrega = Column(
        Text,
        nullable=True,
        comment="Contenido de texto de la entrega (puede ser una descripción o respuesta)"
    )
    archivos_adjuntos = Column(
        ARRAY(Text),
        nullable=True,
        comment="Array de strings (rutas o URLs) de los archivos adjuntados por el estudiante"
    )
    
    __table_args__ = (
        UniqueConstraint(
            "actividad_id", "inscripcion_id",
            name="uq_actividad_inscripcion"
        ),
    )
    
    actividad = relationship(
        "ActividadEvaluativa",
        back_populates="entregas"
    )
    inscripcion = relationship(
        "Inscripcion",
        back_populates="entregas"
    )
    calificacion = relationship(
        "Calificacion",
        back_populates="entrega",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return (
            f"Entrega(id={self.id}, actividad_id={self.actividad_id}, "
            f"inscripcion_id={self.inscripcion_id}, estado={self.estado.value}, "
            f"fecha_entrega={self.fecha_entrega})"
        )
