"""
Modelo de Facultad
Representa las divisiones académicas principales de la institución.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base


class Facultad(Base):
    """
    Modelo de Facultad.
    
    Representa las facultades o escuelas de la institución
    (ej. Facultad de Ingeniería, Facultad de Ciencias, etc.).
    
    Relaciones:
    - Tiene muchos ProgramasAcademicos (1:N) - carreras de la facultad
    - Tiene muchos Cursos (1:N) - materias ofrecidas por la facultad
    - Tiene muchos Profesores (1:N) - docentes adscritos a la facultad
    """
    
    __tablename__ = "facultad" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(
        String(20),
        unique=True,
        nullable=False,
        comment="Código único de la facultad, ej: ING, CIEN, ADMIN"
    )
    nombre = Column(
        String(150),
        unique=True,
        nullable=False,
        comment="Nombre completo de la facultad"
    )
    
    programas_academicos = relationship(
        "ProgramaAcademico",
        back_populates="facultad",
        cascade="all, delete-orphan"
    )
    cursos = relationship(
        "Curso",
        back_populates="facultad",
        cascade="all, delete-orphan"
    )
    profesores = relationship(
        "Profesor",
        back_populates="facultad"
    )
    
    def __repr__(self) -> str:
        return (
            f"Facultad(id={self.id}, codigo='{self.codigo}', "
            f"nombre='{self.nombre}')"
        )
