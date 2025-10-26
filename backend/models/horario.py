"""
Modelo de Horario
Almacena los bloques de día/hora/lugar para un Grupo.
"""
from sqlalchemy import (
    Column, Integer, String, Time,
    ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship

from db.base import Base


class Horario(Base):
    """
    Modelo de Horario.
    
    Almacena los bloques de día/hora/salón para un grupo específico.
    Un grupo puede tener múltiples entradas de horario
    (ej. Lunes y Miércoles de 8:00 a 10:00).
    
    Relaciones:
    - Pertenece a un Grupo (N:1)
    """
    
    __tablename__ = "horario" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    grupo_id = Column(
        Integer,
        ForeignKey("grupo.id", ondelete="CASCADE"),
        nullable=False,
        comment="Grupo al que pertenece este bloque de horario"
    )
    dia = Column(
        String(15),
        nullable=False,
        comment="Día de la semana, ej: Lunes, Martes, Miércoles"
    )
    hora_inicio = Column(
        Time,
        nullable=False,
        comment="Hora de inicio de la clase"
    )
    hora_fin = Column(
        Time,
        nullable=False,
        comment="Hora de finalización de la clase"
    )
    salon = Column(
        String(50),
        nullable=True,
        comment="Salón o ubicación, ej: Bloque 5 - 101, Virtual"
    )
    
    __table_args__ = (
        CheckConstraint(
            "hora_fin > hora_inicio",
            name="chk_horas_validas"
        ),
    )
    
    grupo = relationship(
        "Grupo",
        back_populates="horarios"
    )
    
    def __repr__(self) -> str:
        return (
            f"Horario(id={self.id}, grupo_id={self.grupo_id}, "
            f"dia='{self.dia}', {self.hora_inicio}-{self.hora_fin}, "
            f"salon='{self.salon}')"
        )
