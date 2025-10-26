"""
Schemas de Pydantic para Actividad Evaluativa
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

from models.actividad_evaluativa import (
    EstadoActividad,
    TipoActividad,
    PrioridadActividad
)


class ActividadEvaluativaBase(BaseModel):
    """
    Schema base con los campos comunes de ActividadEvaluativa.
    Otros schemas heredan de este.
    """
    titulo: str = Field(..., min_length=1, max_length=255, description="Título de la actividad")
    descripcion: Optional[str] = Field(None, description="Descripción detallada de la actividad")
    tipo: TipoActividad = Field(default=TipoActividad.TAREA, description="Tipo de actividad")
    prioridad: PrioridadActividad = Field(default=PrioridadActividad.MEDIA, description="Prioridad de la actividad")
    porcentaje: float = Field(..., ge=0.0, le=100.0, description="Porcentaje en la nota final (0-100)")
    fecha_entrega: datetime = Field(..., description="Fecha y hora límite para la entrega")


class ActividadEvaluativaCreate(ActividadEvaluativaBase):
    """
    Schema para crear una nueva actividad evaluativa.
    
    Usado en: POST /api/v1/actividades-evaluativas
    """
    grupo_id: int = Field(..., gt=0, description="ID del grupo al que pertenece la actividad")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grupo_id": 1,
                "titulo": "Taller de Programación - Estructuras de Datos",
                "descripcion": "Implementar listas enlazadas, pilas y colas en Python",
                "tipo": "Tarea",
                "prioridad": "Alta",
                "porcentaje": 15.0,
                "fecha_entrega": "2025-11-15T23:59:00Z"
            }
        }
    )


class ActividadEvaluativaUpdate(BaseModel):
    """
    Schema para actualizar una actividad evaluativa.
    
    Usado en: PUT/PATCH /api/v1/actividades-evaluativas/{id}
    """
    titulo: Optional[str] = Field(None, min_length=1, max_length=255)
    descripcion: Optional[str] = None
    estado: Optional[EstadoActividad] = None
    tipo: Optional[TipoActividad] = None
    prioridad: Optional[PrioridadActividad] = None
    porcentaje: Optional[float] = Field(None, ge=0.0, le=100.0)
    fecha_entrega: Optional[datetime] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "titulo": "Taller de Programación - Estructuras de Datos (Actualizado)",
                "estado": "Abierta",
                "fecha_entrega": "2025-11-20T23:59:00Z"
            }
        }
    )


class ActividadEvaluativaInDB(ActividadEvaluativaBase):
    """
    Schema que representa una actividad evaluativa en la base de datos.
    
    Incluye todos los campos del modelo, incluyendo los generados automáticamente.
    """
    id: int
    grupo_id: int
    estado: EstadoActividad
    
    model_config = ConfigDict(from_attributes=True)


class ActividadEvaluativaPublic(ActividadEvaluativaInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    
    Incluye toda la información que el cliente necesita ver.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "grupo_id": 1,
                "titulo": "Taller de Programación - Estructuras de Datos",
                "descripcion": "Implementar listas enlazadas, pilas y colas en Python",
                "estado": "Abierta",
                "tipo": "Tarea",
                "prioridad": "Alta",
                "porcentaje": 15.0,
                "fecha_entrega": "2025-11-15T23:59:00Z"
            }
        }
    )


class ActividadEvaluativaList(BaseModel):
    """
    Schema para listar actividades evaluativas con información resumida.
    
    Usado en: GET /api/v1/actividades-evaluativas?grupo_id=X
    """
    id: int
    grupo_id: int
    titulo: str
    tipo: TipoActividad
    prioridad: PrioridadActividad
    estado: EstadoActividad
    porcentaje: float
    fecha_entrega: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ActividadEvaluativaEstadoUpdate(BaseModel):
    """
    Schema para cambiar solo el estado de una actividad.
    
    Usado en: PATCH /api/v1/actividades-evaluativas/{id}/estado
    """
    estado: EstadoActividad = Field(..., description="Nuevo estado de la actividad")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "Abierta"
            }
        }
    )
