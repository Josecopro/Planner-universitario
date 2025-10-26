"""
Schemas de Pydantic para Grupo
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional

from models.grupo import EstadoGrupo


class GrupoBase(BaseModel):
    """
    Schema base con los campos comunes de Grupo.
    Otros schemas heredan de este.
    """
    semestre: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Periodo académico, ej: 2025-1, 2025-2"
    )
    cupo_maximo: int = Field(
        ...,
        ge=0,
        description="Número máximo de estudiantes permitidos"
    )
    
    @field_validator('semestre')
    @classmethod
    def validar_formato_semestre(cls, v: str) -> str:
        """Valida el formato del semestre (YYYY-N)"""
        import re
        if not re.match(r'^\d{4}-[1-3]$', v):
            raise ValueError('El semestre debe tener el formato YYYY-N (ej: 2025-1)')
        return v


class GrupoCreate(GrupoBase):
    """
    Schema para crear un nuevo grupo.
    
    Usado en: POST /api/v1/grupos
    """
    curso_id: int = Field(..., gt=0, description="ID del curso que se va a dictar")
    profesor_id: Optional[int] = Field(None, gt=0, description="ID del profesor (opcional)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "curso_id": 1,
                "profesor_id": 5,
                "semestre": "2025-1",
                "cupo_maximo": 35
            }
        }
    )


class GrupoUpdate(BaseModel):
    """
    Schema para actualizar un grupo existente.
    
    Usado en: PUT/PATCH /api/v1/grupos/{id}
    """
    profesor_id: Optional[int] = Field(None, gt=0, description="Cambiar profesor")
    semestre: Optional[str] = Field(None, min_length=1, max_length=20)
    cupo_maximo: Optional[int] = Field(None, ge=0, description="Ajustar cupo máximo")
    estado: Optional[EstadoGrupo] = Field(None, description="Cambiar estado del grupo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "cupo_maximo": 40,
                "estado": "Abierto"
            }
        }
    )


class GrupoInDB(GrupoBase):
    """
    Schema que representa un grupo en la base de datos.
    
    Incluye todos los campos del modelo.
    """
    id: int
    curso_id: int
    profesor_id: Optional[int]
    cupo_actual: int
    estado: EstadoGrupo
    
    model_config = ConfigDict(from_attributes=True)


class GrupoPublic(GrupoInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "curso_id": 1,
                "profesor_id": 5,
                "semestre": "2025-1",
                "cupo_maximo": 35,
                "cupo_actual": 28,
                "estado": "En Curso"
            }
        }
    )


class GrupoConDetalles(GrupoPublic):
    """
    Schema extendido que incluye información del curso y profesor.
    
    Usado en: GET /api/v1/grupos/{id}/detalles
    """
    # Información del curso
    curso_codigo: str = Field(..., description="Código del curso")
    curso_nombre: str = Field(..., description="Nombre del curso")
    
    # Información del profesor (opcional)
    profesor_nombre: Optional[str] = Field(None, description="Nombre del profesor")
    profesor_apellido: Optional[str] = Field(None, description="Apellido del profesor")
    
    # Información calculada
    cupos_disponibles: int = Field(..., description="Cupos disponibles")
    porcentaje_ocupacion: float = Field(..., description="Porcentaje de ocupación del grupo")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "curso_id": 1,
                "profesor_id": 5,
                "semestre": "2025-1",
                "cupo_maximo": 35,
                "cupo_actual": 28,
                "estado": "En Curso",
                "curso_codigo": "IS-101",
                "curso_nombre": "Introducción a la Programación",
                "profesor_nombre": "Carlos",
                "profesor_apellido": "Gómez",
                "cupos_disponibles": 7,
                "porcentaje_ocupacion": 80.0
            }
        }
    )


class GrupoList(BaseModel):
    """
    Schema para listar grupos con información resumida.
    
    Usado en: GET /api/v1/grupos?curso_id=X&semestre=Y
    
    Versión ligera para listados.
    """
    id: int
    curso_codigo: str
    curso_nombre: str
    semestre: str
    profesor_nombre: Optional[str]
    cupo_actual: int
    cupo_maximo: int
    estado: EstadoGrupo
    
    model_config = ConfigDict(from_attributes=True)


class GrupoConHorarios(GrupoConDetalles):
    """
    Schema que incluye los horarios del grupo.
    
    Usado en: GET /api/v1/grupos/{id}/horarios
    
    Muestra el grupo con sus bloques de horario.
    """
    horarios: list[dict] = Field(
        ...,
        description="Lista de bloques de horario (día, hora_inicio, hora_fin, salon)"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "curso_codigo": "IS-101",
                "curso_nombre": "Introducción a la Programación",
                "semestre": "2025-1",
                "cupo_actual": 28,
                "cupo_maximo": 35,
                "estado": "En Curso",
                "profesor_nombre": "Carlos",
                "profesor_apellido": "Gómez",
                "horarios": [
                    {
                        "dia": "Lunes",
                        "hora_inicio": "08:00",
                        "hora_fin": "10:00",
                        "salon": "Bloque 5 - 101"
                    },
                    {
                        "dia": "Miércoles",
                        "hora_inicio": "08:00",
                        "hora_fin": "10:00",
                        "salon": "Bloque 5 - 101"
                    }
                ]
            }
        }
    )


class GrupoEstudiante(GrupoConHorarios):
    """
    Schema de grupo desde la perspectiva del estudiante.
    
    Usado en: GET /api/v1/estudiantes/grupos-disponibles
    """
    puede_inscribirse: bool = Field(
        ...,
        description="Indica si el estudiante puede inscribirse en este grupo"
    )
    motivo_no_inscripcion: Optional[str] = Field(
        None,
        description="Razón por la que no puede inscribirse (si aplica)"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "curso_codigo": "IS-101",
                "curso_nombre": "Introducción a la Programación",
                "semestre": "2025-1",
                "cupo_actual": 28,
                "cupo_maximo": 35,
                "estado": "Abierto",
                "horarios": [],
                "puede_inscribirse": True,
                "motivo_no_inscripcion": None
            }
        }
    )


class GrupoProfesor(GrupoConDetalles):
    """
    Schema de grupo desde la perspectiva del profesor.
    
    Usado en: GET /api/v1/profesores/me/grupos
    
    Vista completa para el profesor de sus grupos.
    """
    total_actividades: int = Field(..., description="Total de actividades creadas")
    total_entregas_pendientes: int = Field(..., description="Entregas sin calificar")
    promedio_asistencia: Optional[float] = Field(
        None,
        description="Porcentaje promedio de asistencia del grupo"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "curso_codigo": "IS-101",
                "curso_nombre": "Introducción a la Programación",
                "semestre": "2025-1",
                "cupo_actual": 28,
                "cupo_maximo": 35,
                "estado": "En Curso",
                "total_actividades": 8,
                "total_entregas_pendientes": 12,
                "promedio_asistencia": 92.5
            }
        }
    )


class GrupoEstadisticas(BaseModel):
    """
    Schema para estadísticas de un grupo.
    
    Usado en: GET /api/v1/grupos/{id}/estadisticas
    
    Dashboard del grupo para el profesor.
    """
    grupo_id: int
    
    # Estudiantes
    total_estudiantes: int
    estudiantes_activos: int
    estudiantes_retirados: int
    
    # Asistencia
    sesiones_realizadas: int
    promedio_asistencia: float
    
    # Actividades
    total_actividades: int
    actividades_pendientes: int
    actividades_calificadas: int
    
    # Notas
    promedio_grupo: Optional[float] = Field(None, description="Promedio general del grupo")
    estudiantes_aprobando: int = Field(..., description="Estudiantes con nota >= 3.0")
    estudiantes_reprobando: int = Field(..., description="Estudiantes con nota < 3.0")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grupo_id": 1,
                "total_estudiantes": 28,
                "estudiantes_activos": 27,
                "estudiantes_retirados": 1,
                "sesiones_realizadas": 25,
                "promedio_asistencia": 92.5,
                "total_actividades": 8,
                "actividades_pendientes": 2,
                "actividades_calificadas": 6,
                "promedio_grupo": 4.1,
                "estudiantes_aprobando": 25,
                "estudiantes_reprobando": 2
            }
        }
    )


class GrupoEstadoUpdate(BaseModel):
    """
    Schema para cambiar el estado de un grupo.
    
    Usado en: PATCH /api/v1/grupos/{id}/estado
    """
    estado: EstadoGrupo = Field(..., description="Nuevo estado del grupo")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "Abierto"
            }
        }
    )


class GrupoFiltros(BaseModel):
    """
    Schema para filtrar grupos en consultas.
    
    Usado en: GET /api/v1/grupos?filters
    """
    curso_id: Optional[int] = Field(None, gt=0, description="Filtrar por curso")
    profesor_id: Optional[int] = Field(None, gt=0, description="Filtrar por profesor")
    semestre: Optional[str] = Field(None, description="Filtrar por semestre")
    estado: Optional[EstadoGrupo] = Field(None, description="Filtrar por estado")
    con_cupos: Optional[bool] = Field(None, description="Solo grupos con cupos disponibles")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "semestre": "2025-1",
                "estado": "Abierto",
                "con_cupos": True
            }
        }
    )
