"""
Modelo de Calificación
Representa la nota y retroalimentación asignada a una entrega.
"""
from sqlalchemy import (
    Column, Integer, Numeric, Text,
    ForeignKey, CheckConstraint
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime

from db.base import Base


class Calificacion(Base):
    """
    Modelo de Calificación.
    
    Representa la nota y retroalimentación asignada por un profesor
    a una entrega específica.
    
    Relaciones:
    - Pertenece a una Entrega (1:1) - cada entrega tiene máximo una calificación
    
    Nota: La relación con Entrega es 1:1, lo que significa que una entrega
    solo puede ser calificada una vez (aunque la calificación puede actualizarse).
    """
    
    __tablename__ = "calificacion" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    entrega_id = Column(
        Integer,
        ForeignKey("entrega.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Referencia única a la entrega que se está calificando (Relación 1 a 1)"
    )
    nota_obtenida = Column(
        Numeric(5, 2),
        nullable=False,
        comment="Nota obtenida por el estudiante en esta entrega"
    )
    fecha_calificacion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Fecha y hora en que se realizó la calificación"
    )
    retroalimentacion = Column(
        Text,
        nullable=True,
        comment="Comentarios y feedback del profesor sobre la entrega"
    )
    
    __table_args__ = (
        CheckConstraint(
            "nota_obtenida >= 0.0",
            name="chk_nota_valida"
        ),
    )
    
    entrega = relationship(
        "Entrega",
        back_populates="calificacion",
        uselist=False
    )
    
    def __repr__(self) -> str:
        return (
            f"Calificacion(id={self.id}, entrega_id={self.entrega_id}, "
            f"nota_obtenida={self.nota_obtenida}, fecha_calificacion={self.fecha_calificacion})"
        )
