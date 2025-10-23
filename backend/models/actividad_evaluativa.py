"""
Modelo de Actividad Evaluativa
Representa las tareas, exámenes y demás actividades calificables de un grupo.
"""
from sqlalchemy import (
    Column, Integer, String, Text, Numeric,
    ForeignKey, CheckConstraint, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from db.base import Base


# =================================================================
#  ENUMS
# =================================================================

class EstadoActividad(str, enum.Enum):
    """Estado de una actividad evaluativa"""
    PROGRAMADA = "Programada"  # Creada por el profesor, no visible aún
    PUBLICADA = "Publicada"    # Visible para estudiantes, no acepta entregas
    ABIERTA = "Abierta"        # Aceptando entregas
    CERRADA = "Cerrada"        # Fecha de entrega pasada
    CANCELADA = "Cancelada"


class TipoActividad(str, enum.Enum):
    """Tipo de actividad evaluativa"""
    TAREA = "Tarea"
    QUIZ = "Quiz"
    EXAMEN_PARCIAL = "Examen Parcial"
    EXAMEN_FINAL = "Examen Final"
    PROYECTO = "Proyecto"
    LABORATORIO = "Laboratorio"
    OTRO = "Otro"


class PrioridadActividad(str, enum.Enum):
    """Prioridad de la actividad"""
    BAJA = "Baja"
    MEDIA = "Media"
    ALTA = "Alta"


# =================================================================
#  MODELO
# =================================================================

class ActividadEvaluativa(Base):
    """
    Modelo de Actividad Evaluativa.
    
    Representa una tarea, examen o cualquier actividad calificable
    asignada a un grupo específico.
    
    Relaciones:
    - Pertenece a un Grupo (N:1)
    - Tiene muchas Entregas (1:N)
    """
    
    __tablename__ = "actividadevaluativa" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    grupo_id = Column(
        Integer,
        ForeignKey("grupo.id", ondelete="CASCADE"),
        nullable=False
    )
    titulo = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    estado = Column(
        SQLEnum(EstadoActividad, name="estado_actividad"),
        nullable=False,
        default=EstadoActividad.PROGRAMADA
    )
    fecha_entrega = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        comment="Fecha y hora límite para la entrega de la actividad"
    )
    tipo = Column(
        SQLEnum(TipoActividad, name="tipo_actividad"),
        nullable=False,
        default=TipoActividad.TAREA
    )
    prioridad = Column(
        SQLEnum(PrioridadActividad, name="prioridad_actividad"),
        nullable=False,
        default=PrioridadActividad.MEDIA
    )
    porcentaje = Column(
        Numeric(5, 2),
        nullable=False,
        default=0.0,
        comment="Porcentaje que vale esta actividad en la nota final del curso"
    )
    
    __table_args__ = (
        CheckConstraint(
            "porcentaje >= 0.0 AND porcentaje <= 100.0",
            name="chk_porcentaje"
        ),
    )
    
    grupo = relationship(
        "Grupo",
        back_populates="actividades_evaluativas"
    )
    entregas = relationship(
        "Entrega",
        back_populates="actividad",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return (
            f"ActividadEvaluativa(id={self.id}, titulo='{self.titulo}', "
            f"tipo={self.tipo.value}, estado={self.estado.value}, "
            f"fecha_entrega={self.fecha_entrega})"
        )
