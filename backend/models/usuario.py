"""
Modelo de Usuario
Entidad central para la identidad y autenticación de los usuarios.
"""
from sqlalchemy import (
    Column, Integer, String,
    ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from db.base import Base


class EstadoUsuario(str, enum.Enum):
    """Estado de la cuenta de usuario"""
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    PENDIENTE_DE_VERIFICACION = "Pendiente de Verificacion"


class Usuario(Base):
    """
    Modelo de Usuario.
    
    Entidad central para la identidad y autenticación de los usuarios.
    Almacena datos de login y información básica del usuario.
    
    Relaciones:
    - Pertenece a un Rol (N:1)
    - Puede tener un perfil de Profesor (1:1) - opcional
    - Puede tener un perfil de Estudiante (1:1) - opcional
    """
    
    __tablename__ = "usuario" # type: ignore
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(
        String(100),
        nullable=False,
        comment="Nombre(s) del usuario"
    )
    apellido = Column(
        String(100),
        nullable=False,
        comment="Apellido(s) del usuario"
    )
    correo = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Correo electrónico único del usuario (usado para login)"
    )
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hash de la contraseña, nunca la contraseña en texto plano"
    )
    rol_id = Column(
        Integer,
        ForeignKey("rol.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Rol del usuario (Superadmin, Profesor, Estudiante)"
    )
    avatar_url = Column(
        String(255),
        nullable=True,
        comment="URL de la imagen de perfil del usuario"
    )
    estado = Column(
        SQLEnum(EstadoUsuario, name="estado_usuario"),
        nullable=False,
        default=EstadoUsuario.PENDIENTE_DE_VERIFICACION,
        comment="Estado de la cuenta del usuario"
    )
    fecha_creacion = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment="Fecha y hora de creación de la cuenta"
    )
    ultimo_acceso = Column(
        TIMESTAMP(timezone=True),
        nullable=True,
        comment="Fecha y hora del último acceso del usuario"
    )
    
    __table_args__ = (
        Index("idx_usuario_correo", "correo"),
    )
    
    rol = relationship(
        "Rol",
        back_populates="usuarios"
    )
    profesor = relationship(
        "Profesor",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )
    estudiante = relationship(
        "Estudiante",
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return (
            f"Usuario(id={self.id}, nombre='{self.nombre}', "
            f"apellido='{self.apellido}', correo='{self.correo}', "
            f"rol_id={self.rol_id}, estado={self.estado.value})"
        )
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del usuario"""
        return f"{self.nombre} {self.apellido}"
