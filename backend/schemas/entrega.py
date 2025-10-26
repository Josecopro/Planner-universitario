"""
Schemas de Pydantic para Entrega
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

from models.entrega import EstadoEntrega


class EntregaBase(BaseModel):
    """
    Schema base con los campos comunes de Entrega.
    Otros schemas heredan de este.
    """
    texto_entrega: Optional[str] = Field(
        None,
        description="Contenido de texto de la entrega (descripción o respuesta)"
    )
    archivos_adjuntos: Optional[list[str]] = Field(
        None,
        description="Lista de URLs o rutas de archivos adjuntados"
    )


class EntregaCreate(EntregaBase):
    """
    Schema para crear una entrega (estudiante entrega una actividad).
    
    Usado en: POST /api/v1/entregas
    """
    actividad_id: int = Field(..., gt=0, description="ID de la actividad que se está entregando")
    inscripcion_id: int = Field(..., gt=0, description="ID de la inscripción del estudiante")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "actividad_id": 5,
                "inscripcion_id": 10,
                "texto_entrega": "Adjunto el código fuente de la implementación de listas enlazadas con todas las operaciones requeridas.",
                "archivos_adjuntos": [
                    "https://storage.example.com/entregas/linked_list.py",
                    "https://storage.example.com/entregas/test_linked_list.py"
                ]
            }
        }
    )


class EntregaUpdate(BaseModel):
    """
    Schema para actualizar una entrega existente.
    
    Usado en: PUT/PATCH /api/v1/entregas/{id}
    """
    texto_entrega: Optional[str] = Field(None, description="Nuevo texto de la entrega")
    archivos_adjuntos: Optional[list[str]] = Field(None, description="Nuevos archivos adjuntos")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "texto_entrega": "Actualización: Corregí un bug en la función de eliminación.",
                "archivos_adjuntos": [
                    "https://storage.example.com/entregas/linked_list_v2.py",
                    "https://storage.example.com/entregas/test_linked_list_v2.py"
                ]
            }
        }
    )


class EntregaInDB(EntregaBase):
    """
    Schema que representa una entrega en la base de datos.
    
    Incluye todos los campos del modelo, incluyendo los generados automáticamente.
    """
    id: int
    actividad_id: int
    inscripcion_id: int
    fecha_entrega: datetime
    estado: EstadoEntrega
    
    model_config = ConfigDict(from_attributes=True)


class EntregaPublic(EntregaInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    
    Incluye toda la información de la entrega.
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "actividad_id": 5,
                "inscripcion_id": 10,
                "fecha_entrega": "2025-11-10T22:45:00Z",
                "estado": "Entregada",
                "texto_entrega": "Adjunto el código fuente de la implementación.",
                "archivos_adjuntos": [
                    "https://storage.example.com/entregas/linked_list.py"
                ]
            }
        }
    )


class EntregaConDetalles(EntregaPublic):
    """
    Schema extendido que incluye información de la actividad y estudiante.
    
    Usado en: GET /api/v1/entregas/{id}/detalles
    
    Útil para mostrar la entrega con contexto completo.
    """
    # Información de la actividad
    actividad_titulo: str = Field(..., description="Título de la actividad")
    actividad_tipo: str = Field(..., description="Tipo de actividad")
    actividad_fecha_limite: datetime = Field(..., description="Fecha límite de la actividad")
    
    # Información del estudiante
    estudiante_nombre: str = Field(..., description="Nombre completo del estudiante")
    estudiante_documento: Optional[str] = Field(None, description="Documento del estudiante")
    
    # Información de calificación (si existe)
    tiene_calificacion: bool = Field(..., description="Indica si ya fue calificada")
    nota_obtenida: Optional[float] = Field(None, description="Nota (si ya fue calificada)")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "actividad_id": 5,
                "inscripcion_id": 10,
                "fecha_entrega": "2025-11-10T22:45:00Z",
                "estado": "Calificada",
                "texto_entrega": "Adjunto el código fuente.",
                "archivos_adjuntos": ["https://storage.example.com/entregas/file.py"],
                "actividad_titulo": "Taller de Estructuras de Datos",
                "actividad_tipo": "Tarea",
                "actividad_fecha_limite": "2025-11-11T23:59:00Z",
                "estudiante_nombre": "Juan Pérez García",
                "estudiante_documento": "1234567890",
                "tiene_calificacion": True,
                "nota_obtenida": 4.5
            }
        }
    )


class EntregaList(BaseModel):
    """
    Schema para listar entregas con información resumida.
    
    Usado en: GET /api/v1/entregas?actividad_id=X
    """
    id: int
    actividad_id: int
    inscripcion_id: int
    fecha_entrega: datetime
    estado: EstadoEntrega
    tiene_archivos: bool = Field(..., description="Indica si tiene archivos adjuntos")
    
    model_config = ConfigDict(from_attributes=True)


class EntregaEstudiante(EntregaPublic):
    """
    Schema de entrega desde la perspectiva del estudiante.
    
    Usado en: GET /api/v1/estudiantes/me/entregas
    """
    actividad_titulo: str
    actividad_tipo: str
    actividad_fecha_limite: datetime
    dias_para_entrega: Optional[int] = Field(
        None,
        description="Días restantes para entregar (negativo si está atrasado)"
    )
    puede_actualizar: bool = Field(
        ...,
        description="Indica si el estudiante puede actualizar la entrega"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "actividad_id": 5,
                "inscripcion_id": 10,
                "fecha_entrega": "2025-11-10T22:45:00Z",
                "estado": "Entregada",
                "texto_entrega": "Mi respuesta...",
                "archivos_adjuntos": ["https://..."],
                "actividad_titulo": "Taller de Estructuras de Datos",
                "actividad_tipo": "Tarea",
                "actividad_fecha_limite": "2025-11-11T23:59:00Z",
                "dias_para_entrega": 1,
                "puede_actualizar": True
            }
        }
    )


class EntregaProfesor(EntregaConDetalles):
    """
    Schema de entrega desde la perspectiva del profesor.
    
    Usado en: GET /api/v1/profesores/actividades/{id}/entregas
    """
    es_tardia: bool = Field(
        ...,
        description="Indica si la entrega fue realizada después de la fecha límite"
    )
    dias_retraso: Optional[int] = Field(
        None,
        description="Días de retraso (solo si es tardía)"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "actividad_id": 5,
                "inscripcion_id": 10,
                "fecha_entrega": "2025-11-12T10:30:00Z",
                "estado": "Entregada Tarde",
                "texto_entrega": "Adjunto el trabajo.",
                "archivos_adjuntos": ["https://..."],
                "actividad_titulo": "Taller de Estructuras de Datos",
                "actividad_tipo": "Tarea",
                "actividad_fecha_limite": "2025-11-11T23:59:00Z",
                "estudiante_nombre": "Juan Pérez García",
                "estudiante_documento": "1234567890",
                "tiene_calificacion": False,
                "nota_obtenida": None,
                "es_tardia": True,
                "dias_retraso": 1
            }
        }
    )


class EntregaEstadisticasActividad(BaseModel):
    """
    Schema para estadísticas de entregas de una actividad.
    
    Usado en: GET /api/v1/entregas/estadisticas/actividad/{actividad_id}
    """
    actividad_id: int
    total_estudiantes: int = Field(..., description="Total de estudiantes inscritos")
    total_entregas: int = Field(..., description="Entregas realizadas")
    pendientes: int = Field(..., description="Estudiantes sin entregar")
    entregadas_tiempo: int = Field(..., description="Entregas a tiempo")
    entregadas_tarde: int = Field(..., description="Entregas tardías")
    calificadas: int = Field(..., description="Entregas ya calificadas")
    porcentaje_entrega: float = Field(..., description="Porcentaje de estudiantes que entregaron")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "actividad_id": 5,
                "total_estudiantes": 30,
                "total_entregas": 28,
                "pendientes": 2,
                "entregadas_tiempo": 25,
                "entregadas_tarde": 3,
                "calificadas": 20,
                "porcentaje_entrega": 93.33
            }
        }
    )


class EntregaFiltros(BaseModel):
    """
    Schema para filtrar entregas en consultas.
    
    Usado en: GET /api/v1/entregas?filters
    """
    actividad_id: Optional[int] = Field(None, gt=0, description="Filtrar por actividad")
    inscripcion_id: Optional[int] = Field(None, gt=0, description="Filtrar por estudiante")
    estado: Optional[EstadoEntrega] = Field(None, description="Filtrar por estado")
    fecha_desde: Optional[datetime] = Field(None, description="Entregas desde esta fecha")
    fecha_hasta: Optional[datetime] = Field(None, description="Entregas hasta esta fecha")
    solo_tardias: Optional[bool] = Field(None, description="Solo entregas tardías")
    solo_sin_calificar: Optional[bool] = Field(None, description="Solo entregas sin calificar")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "actividad_id": 5,
                "estado": "Entregada",
                "solo_sin_calificar": True
            }
        }
    )
