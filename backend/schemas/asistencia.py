"""
Schemas de Pydantic para Asistencia
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional, Any

from models.asistencia import EstadoAsistencia


class AsistenciaBase(BaseModel):
    """
    Schema base con los campos comunes de Asistencia.
    Otros schemas heredan de este.
    """
    fecha: date = Field(..., description="Fecha de la sesión de clase")
    estado: EstadoAsistencia = Field(..., description="Estado de asistencia del estudiante")


class AsistenciaCreate(AsistenciaBase):
    """
    Schema para registrar asistencia de un estudiante.
    
    Usado en: POST /api/v1/asistencias
    """
    inscripcion_id: int = Field(..., gt=0, description="ID de la inscripción (estudiante en el grupo)")
    grupo_id: int = Field(..., gt=0, description="ID del grupo (denormalizado para optimización)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "inscripcion_id": 5,
                "grupo_id": 1,
                "fecha": "2025-10-22",
                "estado": "Presente"
            }
        }
    )


class AsistenciaCreateBulk(BaseModel):
    """
    Schema para registrar asistencia de múltiples estudiantes a la vez.
    
    Usado en: POST /api/v1/asistencias/bulk
    """
    grupo_id: int = Field(..., gt=0, description="ID del grupo")
    fecha: date = Field(..., description="Fecha de la sesión")
    asistencias: list[dict[str, Any]] = Field(
        ...,
        description="Lista de asistencias [{inscripcion_id: int, estado: str}]"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grupo_id": 1,
                "fecha": "2025-10-22",
                "asistencias": [
                    {"inscripcion_id": 1, "estado": "Presente"},
                    {"inscripcion_id": 2, "estado": "Ausente"},
                    {"inscripcion_id": 3, "estado": "Tardanza"},
                    {"inscripcion_id": 4, "estado": "Presente"}
                ]
            }
        }
    )


class AsistenciaUpdate(BaseModel):
    """
    Schema para actualizar un registro de asistencia.
    
    Usado en: PUT/PATCH /api/v1/asistencias/{id}
    """
    estado: Optional[EstadoAsistencia] = Field(None, description="Nuevo estado de asistencia")
    fecha: Optional[date] = Field(None, description="Nueva fecha (si se equivocó)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "Justificado"
            }
        }
    )


class AsistenciaInDB(AsistenciaBase):
    """
    Schema que representa una asistencia en la base de datos.
    
    Incluye todos los campos del modelo, incluyendo los generados automáticamente.
    """
    id: int
    inscripcion_id: int
    grupo_id: int
    
    model_config = ConfigDict(from_attributes=True)


class AsistenciaPublic(AsistenciaInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "inscripcion_id": 5,
                "grupo_id": 1,
                "fecha": "2025-10-22",
                "estado": "Presente"
            }
        }
    )


class AsistenciaConEstudiante(AsistenciaPublic):
    """
    Schema extendido que incluye información del estudiante.
    
    Usado en: GET /api/v1/asistencias?grupo_id=X&fecha=Y
    """
    estudiante_nombre: str = Field(..., description="Nombre completo del estudiante")
    estudiante_documento: Optional[str] = Field(None, description="Documento del estudiante")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "inscripcion_id": 5,
                "grupo_id": 1,
                "fecha": "2025-10-22",
                "estado": "Presente",
                "estudiante_nombre": "Juan Pérez García",
                "estudiante_documento": "1234567890"
            }
        }
    )


class AsistenciaResumenEstudiante(BaseModel):
    """
    Schema para el resumen de asistencia de un estudiante.
    
    Usado en: GET /api/v1/asistencias/resumen/estudiante/{inscripcion_id}
    """
    inscripcion_id: int
    total_sesiones: int = Field(..., description="Total de sesiones registradas")
    presentes: int = Field(..., description="Número de asistencias presentes")
    ausentes: int = Field(..., description="Número de ausencias")
    justificados: int = Field(..., description="Número de ausencias justificadas")
    tardanzas: int = Field(..., description="Número de tardanzas")
    porcentaje_asistencia: float = Field(..., ge=0.0, le=100.0, description="Porcentaje de asistencia")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "inscripcion_id": 5,
                "total_sesiones": 20,
                "presentes": 18,
                "ausentes": 1,
                "justificados": 1,
                "tardanzas": 0,
                "porcentaje_asistencia": 90.0
            }
        }
    )


class AsistenciaResumenGrupo(BaseModel):
    """
    Schema para el resumen de asistencia de un grupo en una fecha.
    
    Usado en: GET /api/v1/asistencias/resumen/grupo/{grupo_id}?fecha=YYYY-MM-DD
    """
    grupo_id: int
    fecha: date
    total_estudiantes: int = Field(..., description="Total de estudiantes inscritos")
    presentes: int
    ausentes: int
    justificados: int
    tardanzas: int
    porcentaje_asistencia: float = Field(..., ge=0.0, le=100.0)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grupo_id": 1,
                "fecha": "2025-10-22",
                "total_estudiantes": 30,
                "presentes": 27,
                "ausentes": 2,
                "justificados": 1,
                "tardanzas": 0,
                "porcentaje_asistencia": 90.0
            }
        }
    )


class AsistenciaFiltros(BaseModel):
    """
    Schema para filtrar asistencias en consultas.
    
    Usado en: GET /api/v1/asistencias?filters
    
    Permite filtrar por grupo, fecha, rango de fechas, estado.
    """
    grupo_id: Optional[int] = Field(None, gt=0, description="Filtrar por grupo")
    inscripcion_id: Optional[int] = Field(None, gt=0, description="Filtrar por inscripción")
    fecha: Optional[date] = Field(None, description="Filtrar por fecha específica")
    fecha_inicio: Optional[date] = Field(None, description="Fecha de inicio del rango")
    fecha_fin: Optional[date] = Field(None, description="Fecha de fin del rango")
    estado: Optional[EstadoAsistencia] = Field(None, description="Filtrar por estado")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grupo_id": 1,
                "fecha_inicio": "2025-10-01",
                "fecha_fin": "2025-10-31",
                "estado": "Ausente"
            }
        }
    )
