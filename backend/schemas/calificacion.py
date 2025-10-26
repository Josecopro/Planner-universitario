"""
Schemas de Pydantic para Calificación
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class CalificacionBase(BaseModel):
    """
    Schema base con los campos comunes de Calificación.
    Otros schemas heredan de este.
    """
    nota_obtenida: float = Field(
        ...,
        ge=0.0,
        description="Nota obtenida por el estudiante (debe ser >= 0)"
    )
    retroalimentacion: Optional[str] = Field(
        None,
        description="Comentarios y feedback del profesor sobre la entrega"
    )


class CalificacionCreate(CalificacionBase):
    """
    Schema para crear una calificación (calificar una entrega).
    
    Usado en: POST /api/v1/calificaciones
    """
    entrega_id: int = Field(..., gt=0, description="ID de la entrega que se está calificando")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "entrega_id": 15,
                "nota_obtenida": 4.5,
                "retroalimentacion": "Excelente trabajo. La implementación es correcta y el código está bien documentado. Sin embargo, podrías mejorar la eficiencia del algoritmo."
            }
        }
    )



class CalificacionUpdate(BaseModel):
    """
    Schema para actualizar una calificación existente.
    
    Usado en: PUT/PATCH /api/v1/calificaciones/{id}
    """
    nota_obtenida: Optional[float] = Field(
        None,
        ge=0.0,
        description="Nueva nota"
    )
    retroalimentacion: Optional[str] = Field(
        None,
        description="Nueva retroalimentación"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nota_obtenida": 4.7,
                "retroalimentacion": "Después de revisar nuevamente, te subo la nota por la creatividad en la solución."
            }
        }
    )


class CalificacionInDB(CalificacionBase):
    """
    Schema que representa una calificación en la base de datos.
    
    Incluye todos los campos del modelo, incluyendo los generados automáticamente.
    """
    id: int
    entrega_id: int
    fecha_calificacion: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CalificacionPublic(CalificacionInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    
    Incluye toda la información de la calificación.
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "entrega_id": 15,
                "nota_obtenida": 4.5,
                "fecha_calificacion": "2025-10-22T14:30:00Z",
                "retroalimentacion": "Excelente trabajo. La implementación es correcta."
            }
        }
    )


class CalificacionConDetalles(CalificacionPublic):
    """
    Schema extendido que incluye información de la entrega y actividad.
    
    Usado en: GET /api/v1/calificaciones/{id}/detalles
    """
    actividad_titulo: str = Field(..., description="Título de la actividad evaluativa")
    actividad_tipo: str = Field(..., description="Tipo de actividad")
    actividad_porcentaje: float = Field(..., description="Porcentaje de la actividad")
    
    estudiante_nombre: str = Field(..., description="Nombre completo del estudiante")
    estudiante_documento: Optional[str] = Field(None, description="Documento del estudiante")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "entrega_id": 15,
                "nota_obtenida": 4.5,
                "fecha_calificacion": "2025-10-22T14:30:00Z",
                "retroalimentacion": "Excelente trabajo.",
                "actividad_titulo": "Taller de Estructuras de Datos",
                "actividad_tipo": "Tarea",
                "actividad_porcentaje": 15.0,
                "estudiante_nombre": "Juan Pérez García",
                "estudiante_documento": "1234567890"
            }
        }
    )


class CalificacionItem(BaseModel):
    """
    Schema para un item de calificación en calificación masiva.
    """
    entrega_id: int = Field(..., gt=0, description="ID de la entrega")
    nota_obtenida: float = Field(..., ge=0.0, description="Nota")
    retroalimentacion: Optional[str] = Field(None, description="Feedback opcional")


class CalificacionCreateBulk(BaseModel):
    """
    Schema para calificar múltiples entregas a la vez.
    
    Usado en: POST /api/v1/calificaciones/bulk
    
    Nota: Útil para que el profesor califique todas las entregas
    de una actividad de una vez (por ejemplo, desde una planilla).
    """
    calificaciones: list[CalificacionItem] = Field(
        ...,
        min_length=1,
        description="Lista de calificaciones a crear"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "calificaciones": [
                    {
                        "entrega_id": 15,
                        "nota_obtenida": 4.5,
                        "retroalimentacion": "Excelente trabajo"
                    },
                    {
                        "entrega_id": 16,
                        "nota_obtenida": 3.8,
                        "retroalimentacion": "Buen intento, pero falta profundizar"
                    },
                    {
                        "entrega_id": 17,
                        "nota_obtenida": 5.0,
                        "retroalimentacion": "¡Perfecto!"
                    }
                ]
            }
        }
    )


class CalificacionBulkResponse(BaseModel):
    """
    Schema para la respuesta de calificación masiva.
    """
    total: int = Field(..., description="Total de calificaciones intentadas")
    exitosas: int = Field(..., description="Número de calificaciones creadas exitosamente")
    fallidas: int = Field(..., description="Número de calificaciones que fallaron")
    detalles: list[dict] = Field(..., description="Detalles de cada operación")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 3,
                "exitosas": 3,
                "fallidas": 0,
                "detalles": [
                    {"entrega_id": 15, "status": "success", "calificacion_id": 1},
                    {"entrega_id": 16, "status": "success", "calificacion_id": 2},
                    {"entrega_id": 17, "status": "success", "calificacion_id": 3}
                ]
            }
        }
    )


class CalificacionEstadisticas(BaseModel):
    """
    Schema para estadísticas de calificaciones de una actividad.
    
    Usado en: GET /api/v1/calificaciones/estadisticas/actividad/{actividad_id}
    
    Muestra estadísticas generales de las calificaciones.
    """
    actividad_id: int
    total_entregas: int = Field(..., description="Total de entregas")
    total_calificadas: int = Field(..., description="Entregas ya calificadas")
    pendientes: int = Field(..., description="Entregas pendientes de calificar")
    nota_promedio: Optional[float] = Field(None, description="Promedio de notas")
    nota_maxima: Optional[float] = Field(None, description="Nota más alta")
    nota_minima: Optional[float] = Field(None, description="Nota más baja")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "actividad_id": 5,
                "total_entregas": 30,
                "total_calificadas": 25,
                "pendientes": 5,
                "nota_promedio": 4.2,
                "nota_maxima": 5.0,
                "nota_minima": 2.5
            }
        }
    )


class CalificacionResumenEstudiante(BaseModel):
    """
    Schema para el resumen de calificaciones de un estudiante.
    
    Usado en: GET /api/v1/calificaciones/resumen/estudiante/{inscripcion_id}
    
    Muestra todas las calificaciones de un estudiante en un grupo.
    """
    inscripcion_id: int
    total_actividades: int = Field(..., description="Total de actividades del grupo")
    actividades_calificadas: int = Field(..., description="Actividades ya calificadas")
    actividades_pendientes: int = Field(..., description="Actividades sin calificar")
    nota_acumulada: float = Field(..., description="Suma ponderada de notas")
    porcentaje_completado: float = Field(..., description="Porcentaje del curso calificado")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "inscripcion_id": 5,
                "total_actividades": 10,
                "actividades_calificadas": 7,
                "actividades_pendientes": 3,
                "nota_acumulada": 4.3,
                "porcentaje_completado": 65.0
            }
        }
    )
