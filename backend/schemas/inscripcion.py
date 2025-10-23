"""
Schemas de Pydantic para Inscripción
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

from models.inscripcion import EstadoInscripcion


class InscripcionBase(BaseModel):
    """
    Schema base con los campos comunes de Inscripción.
    Otros schemas heredan de este.
    """
    pass


class InscripcionCreate(BaseModel):
    """
    Schema para crear una nueva inscripción.
    
    Usado en: POST /api/v1/inscripciones
              POST /api/v1/grupos/{id}/inscribir
    """
    estudiante_id: int = Field(..., gt=0, description="ID del estudiante")
    grupo_id: int = Field(..., gt=0, description="ID del grupo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estudiante_id": 10,
                "grupo_id": 1
            }
        }
    )


class InscripcionCreateBulk(BaseModel):
    """
    Schema para inscribir múltiples estudiantes en un grupo.
    
    Usado en: POST /api/v1/grupos/{id}/inscribir-multiples
    """
    grupo_id: int = Field(..., gt=0, description="ID del grupo")
    estudiante_ids: list[int] = Field(
        ...,
        min_length=1,
        description="Lista de IDs de estudiantes a inscribir"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grupo_id": 1,
                "estudiante_ids": [10, 11, 12, 13, 14]
            }
        }
    )


class InscripcionUpdate(BaseModel):
    """
    Schema para actualizar una inscripción existente.
    
    Usado en: PUT/PATCH /api/v1/inscripciones/{id}
    
    Permite cambiar el estado o nota definitiva.
    """
    estado: Optional[EstadoInscripcion] = Field(
        None,
        description="Cambiar estado de la inscripción"
    )
    nota_definitiva: Optional[Decimal] = Field(
        None,
        ge=0.0,
        le=5.0,
        description="Nota definitiva del estudiante"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "Aprobado",
                "nota_definitiva": 4.2
            }
        }
    )


class InscripcionEstadoUpdate(BaseModel):
    """
    Schema para cambiar solo el estado de una inscripción.
    
    Usado en: PATCH /api/v1/inscripciones/{id}/estado
    
    Operación específica para retirar o cancelar inscripción.
    """
    estado: EstadoInscripcion = Field(
        ...,
        description="Nuevo estado de la inscripción"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "Retirado"
            }
        }
    )


class InscripcionInDB(InscripcionBase):
    """
    Schema que representa una inscripción en la base de datos.
    
    Incluye todos los campos del modelo.
    """
    id: int
    estudiante_id: int
    grupo_id: int
    fecha_inscripcion: datetime
    estado: EstadoInscripcion
    nota_definitiva: Optional[Decimal]
    
    model_config = ConfigDict(from_attributes=True)


class InscripcionPublic(InscripcionInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "estudiante_id": 10,
                "grupo_id": 1,
                "fecha_inscripcion": "2025-01-15T10:30:00Z",
                "estado": "Inscrito",
                "nota_definitiva": None
            }
        }
    )


class InscripcionConDetalles(InscripcionPublic):
    """
    Schema extendido con información del estudiante y grupo.
    
    Usado en: GET /api/v1/inscripciones/{id}/detalles
    """
    # Información del estudiante
    estudiante_codigo: str = Field(..., description="Código del estudiante")
    estudiante_nombre: str = Field(..., description="Nombre del estudiante")
    estudiante_apellido: str = Field(..., description="Apellido del estudiante")
    
    # Información del grupo
    grupo_semestre: str = Field(..., description="Semestre del grupo")
    
    # Información del curso
    curso_codigo: str = Field(..., description="Código del curso")
    curso_nombre: str = Field(..., description="Nombre del curso")
    creditos: int = Field(..., description="Créditos del curso")
    
    # Información del profesor (opcional)
    profesor_nombre: Optional[str] = Field(None, description="Nombre del profesor")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "estudiante_id": 10,
                "grupo_id": 1,
                "fecha_inscripcion": "2025-01-15T10:30:00Z",
                "estado": "Inscrito",
                "nota_definitiva": None,
                "estudiante_codigo": "2024001",
                "estudiante_nombre": "Juan",
                "estudiante_apellido": "Pérez",
                "grupo_semestre": "2025-1",
                "curso_codigo": "IS-101",
                "curso_nombre": "Introducción a la Programación",
                "creditos": 3,
                "profesor_nombre": "Carlos Gómez"
            }
        }
    )


class InscripcionList(BaseModel):
    """
    Schema para listar inscripciones con información resumida.
    
    Usado en: GET /api/v1/inscripciones
              GET /api/v1/grupos/{id}/estudiantes
    """
    id: int
    estudiante_codigo: str
    estudiante_nombre_completo: str
    curso_codigo: str
    curso_nombre: str
    semestre: str
    estado: EstadoInscripcion
    nota_definitiva: Optional[Decimal]
    
    model_config = ConfigDict(from_attributes=True)


class InscripcionEstudiante(BaseModel):
    """
    Schema de inscripción desde la perspectiva del estudiante.
    
    Usado en: GET /api/v1/estudiantes/me/inscripciones
              GET /api/v1/estudiantes/me/cursos-actuales
    """
    id: int
    grupo_id: int
    fecha_inscripcion: datetime
    estado: EstadoInscripcion
    nota_definitiva: Optional[Decimal]
    
    # Información del curso y grupo
    curso_codigo: str
    curso_nombre: str
    creditos: int
    semestre: str
    profesor_nombre: Optional[str]
    
    # Información académica
    total_actividades: int = Field(..., description="Total de actividades del grupo")
    actividades_entregadas: int = Field(..., description="Actividades entregadas por el estudiante")
    porcentaje_asistencia: Optional[float] = Field(
        None,
        description="Porcentaje de asistencia del estudiante"
    )
    promedio_parcial: Optional[Decimal] = Field(
        None,
        description="Promedio calculado hasta el momento"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "grupo_id": 1,
                "fecha_inscripcion": "2025-01-15T10:30:00Z",
                "estado": "Inscrito",
                "nota_definitiva": None,
                "curso_codigo": "IS-101",
                "curso_nombre": "Introducción a la Programación",
                "creditos": 3,
                "semestre": "2025-1",
                "profesor_nombre": "Carlos Gómez",
                "total_actividades": 8,
                "actividades_entregadas": 6,
                "porcentaje_asistencia": 95.0,
                "promedio_parcial": 4.1
            }
        }
    )


class InscripcionRendimiento(BaseModel):
    """
    Schema con información de rendimiento del estudiante en la inscripción.
    
    Usado en: GET /api/v1/inscripciones/{id}/rendimiento
    """
    inscripcion_id: int
    estudiante_nombre: str
    curso_nombre: str
    
    # Asistencia
    sesiones_realizadas: int
    sesiones_asistidas: int
    porcentaje_asistencia: float
    
    # Actividades y entregas
    total_actividades: int
    actividades_entregadas: int
    actividades_pendientes: int
    entregas_a_tiempo: int
    entregas_tarde: int
    
    # Notas
    promedio_parcial: Optional[Decimal]
    nota_minima: Optional[Decimal]
    nota_maxima: Optional[Decimal]
    nota_definitiva: Optional[Decimal]
    
    # Estado
    estado: EstadoInscripcion
    en_riesgo: bool = Field(
        ...,
        description="Indica si el estudiante está en riesgo de reprobar"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "inscripcion_id": 1,
                "estudiante_nombre": "Juan Pérez",
                "curso_nombre": "Introducción a la Programación",
                "sesiones_realizadas": 25,
                "sesiones_asistidas": 24,
                "porcentaje_asistencia": 96.0,
                "total_actividades": 8,
                "actividades_entregadas": 7,
                "actividades_pendientes": 1,
                "entregas_a_tiempo": 5,
                "entregas_tarde": 2,
                "promedio_parcial": 4.1,
                "nota_minima": 3.5,
                "nota_maxima": 4.8,
                "nota_definitiva": None,
                "estado": "Inscrito",
                "en_riesgo": False
            }
        }
    )


class InscripcionProfesor(BaseModel):
    """
    Schema de inscripción desde la perspectiva del profesor.
    
    Usado en: GET /api/v1/grupos/{id}/estudiantes-detalles
    """
    id: int
    estudiante_id: int
    estudiante_codigo: str
    estudiante_nombre: str
    estudiante_apellido: str
    estudiante_email: str
    fecha_inscripcion: datetime
    estado: EstadoInscripcion
    
    # Rendimiento
    porcentaje_asistencia: Optional[float]
    actividades_entregadas: int
    total_actividades: int
    promedio_parcial: Optional[Decimal]
    nota_definitiva: Optional[Decimal]
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "estudiante_id": 10,
                "estudiante_codigo": "2024001",
                "estudiante_nombre": "Juan",
                "estudiante_apellido": "Pérez",
                "estudiante_email": "juan.perez@universidad.edu",
                "fecha_inscripcion": "2025-01-15T10:30:00Z",
                "estado": "Inscrito",
                "porcentaje_asistencia": 96.0,
                "actividades_entregadas": 7,
                "total_actividades": 8,
                "promedio_parcial": 4.1,
                "nota_definitiva": None
            }
        }
    )


class InscripcionEstadisticas(BaseModel):
    """
    Schema para estadísticas de inscripciones de un grupo.
    
    Usado en: GET /api/v1/grupos/{id}/estadisticas-inscripciones
    """
    grupo_id: int
    
    # Contadores por estado
    total_inscripciones: int
    inscritos: int
    retirados: int
    aprobados: int
    reprobados: int
    cancelados: int
    
    # Promedios
    promedio_grupo: Optional[Decimal] = Field(
        None,
        description="Promedio general del grupo"
    )
    promedio_asistencia: Optional[float] = Field(
        None,
        description="Promedio de asistencia del grupo"
    )
    
    # Distribución de notas
    estudiantes_excelente: int = Field(..., description="Nota >= 4.5")
    estudiantes_bueno: int = Field(..., description="Nota >= 4.0 y < 4.5")
    estudiantes_aceptable: int = Field(..., description="Nota >= 3.0 y < 4.0")
    estudiantes_insuficiente: int = Field(..., description="Nota < 3.0")
    estudiantes_sin_nota: int = Field(..., description="Sin nota definitiva aún")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grupo_id": 1,
                "total_inscripciones": 30,
                "inscritos": 27,
                "retirados": 1,
                "aprobados": 25,
                "reprobados": 2,
                "cancelados": 0,
                "promedio_grupo": 4.1,
                "promedio_asistencia": 92.5,
                "estudiantes_excelente": 10,
                "estudiantes_bueno": 8,
                "estudiantes_aceptable": 7,
                "estudiantes_insuficiente": 2,
                "estudiantes_sin_nota": 3
            }
        }
    )


class InscripcionResumenEstudiante(BaseModel):
    """
    Schema con resumen de todas las inscripciones de un estudiante.
    
    Usado en: GET /api/v1/estudiantes/{id}/resumen-inscripciones
    
    Historial académico resumido del estudiante.
    """
    estudiante_id: int
    estudiante_nombre: str
    
    # Contadores
    total_cursos_inscritos: int
    cursos_activos: int
    cursos_aprobados: int
    cursos_reprobados: int
    cursos_retirados: int
    
    # Promedios
    promedio_acumulado: Optional[Decimal] = Field(
        None,
        description="Promedio de todos los cursos con nota"
    )
    creditos_aprobados: int = Field(
        ...,
        description="Total de créditos aprobados"
    )
    
    # Semestre actual
    cursos_semestre_actual: int
    creditos_semestre_actual: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estudiante_id": 10,
                "estudiante_nombre": "Juan Pérez",
                "total_cursos_inscritos": 15,
                "cursos_activos": 5,
                "cursos_aprobados": 8,
                "cursos_reprobados": 1,
                "cursos_retirados": 1,
                "promedio_acumulado": 4.0,
                "creditos_aprobados": 24,
                "cursos_semestre_actual": 5,
                "creditos_semestre_actual": 15
            }
        }
    )


class InscripcionValidacion(BaseModel):
    """
    Schema para validar si un estudiante puede inscribirse en un grupo.
    
    Usado en: POST /api/v1/inscripciones/validar
    """
    puede_inscribirse: bool = Field(
        ...,
        description="Indica si el estudiante puede inscribirse"
    )
    razones: list[str] = Field(
        default_factory=list,
        description="Razones por las que no puede inscribirse (si aplica)"
    )
    advertencias: list[str] = Field(
        default_factory=list,
        description="Advertencias que el estudiante debe conocer"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "puede_inscribirse": False,
                "razones": [
                    "No hay cupos disponibles en el grupo",
                    "Existe conflicto de horario con IS-102"
                ],
                "advertencias": []
            }
        }
    )


class InscripcionFiltros(BaseModel):
    """
    Schema para filtrar inscripciones en consultas.
    
    Usado en: GET /api/v1/inscripciones?filters
    """
    estudiante_id: Optional[int] = Field(None, gt=0, description="Filtrar por estudiante")
    grupo_id: Optional[int] = Field(None, gt=0, description="Filtrar por grupo")
    curso_id: Optional[int] = Field(None, gt=0, description="Filtrar por curso")
    semestre: Optional[str] = Field(None, description="Filtrar por semestre")
    estado: Optional[EstadoInscripcion] = Field(None, description="Filtrar por estado")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "semestre": "2025-1",
                "estado": "Inscrito"
            }
        }
    )
