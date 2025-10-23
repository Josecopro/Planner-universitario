"""
Base declarativa de SQLAlchemy
Todos los modelos deben heredar de esta clase Base
"""
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr
from typing import Any


class Base(DeclarativeBase):
    """
    Clase base para todos los modelos de SQLAlchemy.
    
    Proporciona:
    - Generación automática de nombres de tablas
    - Configuración común para todos los modelos
    - Métodos útiles que pueden ser heredados
    """
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Genera automáticamente el nombre de la tabla en snake_case
        a partir del nombre de la clase.
        
        UsuarioModel -> usuario_model
        """
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', cls.__name__)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()
    
    def dict(self) -> dict[str, Any]:
        """
        Convierte el modelo a un diccionario.
        Útil para serialización y debugging.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """
        Representación en string del modelo para debugging
        """
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self.dict().items()
        )
        return f"{self.__class__.__name__}({attrs})"


__all__ = ["Base"]
