"""
Servicios - Lógica de Negocio

Los servicios contienen la lógica de negocio de la aplicación.
Son independientes de HTTP y se encargan de:
- Validaciones de negocio
- Interacciones con la base de datos
- Procesamiento de datos
- Aplicación de reglas de negocio
"""

from services import usuario_service
from services import profesor_service

__all__ = [
    "usuario_service",
    "profesor_service",
]
