"""
Schemas de Pydantic para Profesor
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from decimal import Decimal


class ProfesorBase(BaseModel):
    """
    Schema base con los campos comunes de Profesor.
    Otros schemas heredan de este.
    """
    documento: Optional[str] = Field(None, max_length=50, description="Número de documento")
    tipo_documento: Optional[str] = Field(
        None,
        max_length=50,
        description="Tipo de documento (Cédula, Pasaporte, TI, etc.)"
    )
    facultad_id: Optional[int] = Field(None, gt=0, description="Facultad a la que pertenece")
    titulo_academico: Optional[str] = Field(
        None,
        max_length=255,
        description="Título académico del profesor"
    )
    
    @field_validator('tipo_documento')
    @classmethod
    def validar_tipo_documento(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el tipo de documento sea uno de los válidos"""
        if v is None:
            return v
        tipos_validos = ['Cédula', 'Pasaporte', 'TI', 'Cédula de Extranjería', 'PEP']
        if v not in tipos_validos:
            raise ValueError(f'El tipo de documento debe ser uno de: {", ".join(tipos_validos)}')
        return v


class ProfesorCreate(ProfesorBase):
    """
    Schema para crear un nuevo perfil de profesor.
    
    Usado en: POST /api/v1/profesores
    """
    usuario_id: int = Field(..., gt=0, description="ID del usuario asociado")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "usuario_id": 5,
                "documento": "1234567890",
                "tipo_documento": "Cédula",
                "facultad_id": 1,
                "titulo_academico": "Magíster en Ingeniería de Sistemas"
            }
        }
    )


class ProfesorUpdate(BaseModel):
    """
    Schema para actualizar un profesor existente.
    
    Usado en: PUT/PATCH /api/v1/profesores/{id}
              PATCH /api/v1/profesores/me
    """
    documento: Optional[str] = Field(None, max_length=50)
    tipo_documento: Optional[str] = Field(None, max_length=50)
    facultad_id: Optional[int] = Field(None, gt=0)
    titulo_academico: Optional[str] = Field(None, max_length=255)
    
    @field_validator('tipo_documento')
    @classmethod
    def validar_tipo_documento(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el tipo de documento sea uno de los válidos"""
        if v is None:
            return v
        tipos_validos = ['Cédula', 'Pasaporte', 'TI', 'Cédula de Extranjería', 'PEP']
        if v not in tipos_validos:
            raise ValueError(f'El tipo de documento debe ser uno de: {", ".join(tipos_validos)}')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "titulo_academico": "Doctor en Ciencias de la Computación",
                "facultad_id": 2
            }
        }
    )


class ProfesorInDB(ProfesorBase):
    """
    Schema que representa un profesor en la base de datos.
    
    Incluye todos los campos del modelo.
    """
    id: int
    usuario_id: int
    
    model_config = ConfigDict(from_attributes=True)


class ProfesorPublic(ProfesorInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "usuario_id": 5,
                "documento": "1234567890",
                "tipo_documento": "Cédula",
                "facultad_id": 1,
                "titulo_academico": "Magíster en Ingeniería de Sistemas"
            }
        }
    )


class ProfesorConUsuario(ProfesorPublic):
    """
    Schema extendido que incluye información del usuario.
    
    Usado en: GET /api/v1/profesores/{id}/detalles
    """
    # Información del usuario
    usuario_nombre: str = Field(..., description="Nombre del usuario")
    usuario_apellido: str = Field(..., description="Apellido del usuario")
    usuario_email: str = Field(..., description="Email del usuario")
    usuario_telefono: Optional[str] = Field(None, description="Teléfono del usuario")
    usuario_estado: str = Field(..., description="Estado del usuario")
    
    # Información de la facultad (opcional)
    facultad_nombre: Optional[str] = Field(None, description="Nombre de la facultad")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "usuario_id": 5,
                "documento": "1234567890",
                "tipo_documento": "Cédula",
                "facultad_id": 1,
                "titulo_academico": "Magíster en Ingeniería de Sistemas",
                "usuario_nombre": "Carlos",
                "usuario_apellido": "Gómez",
                "usuario_email": "carlos.gomez@universidad.edu",
                "usuario_telefono": "+57 300 123 4567",
                "usuario_estado": "Activo",
                "facultad_nombre": "Facultad de Ingeniería"
            }
        }
    )


class ProfesorList(BaseModel):
    """
    Schema para listar profesores con información resumida.
    
    Usado en: GET /api/v1/profesores
              GET /api/v1/facultades/{id}/profesores
    """
    id: int
    usuario_nombre: str
    usuario_apellido: str
    usuario_email: str
    titulo_academico: Optional[str]
    facultad_nombre: Optional[str]
    total_grupos: int = Field(..., description="Cantidad de grupos asignados")
    
    model_config = ConfigDict(from_attributes=True)


class ProfesorPerfil(ProfesorConUsuario):
    """
    Schema de perfil completo del profesor.
    
    Usado en: GET /api/v1/profesores/me
    
    Vista completa del profesor autenticado.
    """
    # Estadísticas
    total_grupos_activos: int = Field(..., description="Grupos en curso")
    total_grupos_historicos: int = Field(..., description="Total de grupos dictados")
    total_estudiantes_actuales: int = Field(..., description="Estudiantes actuales")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "usuario_id": 5,
                "documento": "1234567890",
                "tipo_documento": "Cédula",
                "facultad_id": 1,
                "titulo_academico": "Magíster en Ingeniería de Sistemas",
                "usuario_nombre": "Carlos",
                "usuario_apellido": "Gómez",
                "usuario_email": "carlos.gomez@universidad.edu",
                "usuario_telefono": "+57 300 123 4567",
                "usuario_estado": "Activo",
                "facultad_nombre": "Facultad de Ingeniería",
                "total_grupos_activos": 3,
                "total_grupos_historicos": 15,
                "total_estudiantes_actuales": 85
            }
        }
    )


class ProfesorGrupos(BaseModel):
    """
    Schema con los grupos asignados al profesor.
    
    Usado en: GET /api/v1/profesores/{id}/grupos
              GET /api/v1/profesores/me/grupos
    
    Lista de grupos del profesor con información relevante.
    """
    profesor_id: int
    profesor_nombre: str
    grupos: list[dict] = Field(
        ...,
        description="Lista de grupos asignados con detalles"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profesor_id": 1,
                "profesor_nombre": "Carlos Gómez",
                "grupos": [
                    {
                        "grupo_id": 1,
                        "curso_codigo": "IS-101",
                        "curso_nombre": "Introducción a la Programación",
                        "semestre": "2025-1",
                        "total_estudiantes": 28,
                        "estado": "En Curso",
                        "horarios": [
                            {"dia": "Lunes", "hora_inicio": "08:00", "hora_fin": "10:00"}
                        ]
                    },
                    {
                        "grupo_id": 5,
                        "curso_codigo": "IS-201",
                        "curso_nombre": "Estructuras de Datos",
                        "semestre": "2025-1",
                        "total_estudiantes": 30,
                        "estado": "En Curso",
                        "horarios": [
                            {"dia": "Martes", "hora_inicio": "14:00", "hora_fin": "16:00"}
                        ]
                    }
                ]
            }
        }
    )


class ProfesorCargaAcademica(BaseModel):
    """
    Schema con la carga académica del profesor.
    
    Usado en: GET /api/v1/profesores/{id}/carga-academica
              GET /api/v1/profesores/me/carga-academica
    
    Resumen de la carga de trabajo del profesor.
    """
    profesor_id: int
    profesor_nombre: str
    semestre: str
    
    # Carga
    total_grupos: int
    total_estudiantes: int
    total_horas_clase: float = Field(..., description="Horas semanales de clase")
    
    # Cursos
    cursos: list[dict] = Field(
        ...,
        description="Lista de cursos con cantidad de grupos"
    )
    
    # Estado de trabajo pendiente
    actividades_sin_calificar: int = Field(
        ...,
        description="Total de entregas pendientes de calificar"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profesor_id": 1,
                "profesor_nombre": "Carlos Gómez",
                "semestre": "2025-1",
                "total_grupos": 3,
                "total_estudiantes": 85,
                "total_horas_clase": 12.0,
                "cursos": [
                    {
                        "curso_codigo": "IS-101",
                        "curso_nombre": "Introducción a la Programación",
                        "grupos": 2,
                        "estudiantes": 55
                    },
                    {
                        "curso_codigo": "IS-301",
                        "curso_nombre": "Bases de Datos",
                        "grupos": 1,
                        "estudiantes": 30
                    }
                ],
                "actividades_sin_calificar": 23
            }
        }
    )


class ProfesorEstadisticas(BaseModel):
    """
    Schema para estadísticas del profesor.
    
    Usado en: GET /api/v1/profesores/{id}/estadisticas
              GET /api/v1/profesores/me/estadisticas
    
    Dashboard completo del profesor.
    """
    profesor_id: int
    profesor_nombre: str
    
    # Grupos
    grupos_activos: int
    grupos_finalizados_semestre: int
    total_estudiantes_actuales: int
    
    # Promedios
    promedio_general_grupos: Optional[Decimal] = Field(
        None,
        description="Promedio general de todos los grupos actuales"
    )
    promedio_asistencia_grupos: Optional[float] = Field(
        None,
        description="Promedio de asistencia en todos los grupos"
    )
    
    # Actividades
    total_actividades_creadas: int
    actividades_pendientes_calificar: int
    actividades_calificadas: int
    
    # Rendimiento estudiantil
    estudiantes_excelente: int = Field(..., description="Promedio >= 4.5")
    estudiantes_bueno: int = Field(..., description="Promedio >= 4.0 y < 4.5")
    estudiantes_aceptable: int = Field(..., description="Promedio >= 3.0 y < 4.0")
    estudiantes_en_riesgo: int = Field(..., description="Promedio < 3.0")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profesor_id": 1,
                "profesor_nombre": "Carlos Gómez",
                "grupos_activos": 3,
                "grupos_finalizados_semestre": 0,
                "total_estudiantes_actuales": 85,
                "promedio_general_grupos": 4.1,
                "promedio_asistencia_grupos": 91.5,
                "total_actividades_creadas": 24,
                "actividades_pendientes_calificar": 23,
                "actividades_calificadas": 145,
                "estudiantes_excelente": 28,
                "estudiantes_bueno": 35,
                "estudiantes_aceptable": 18,
                "estudiantes_en_riesgo": 4
            }
        }
    )


class ProfesorRendimientoHistorico(BaseModel):
    """
    Schema con el rendimiento histórico del profesor.
    
    Usado en: GET /api/v1/profesores/{id}/rendimiento-historico
    
    Historial de desempeño del profesor por semestres.
    """
    profesor_id: int
    profesor_nombre: str
    historial: list[dict] = Field(
        ...,
        description="Rendimiento por semestre"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profesor_id": 1,
                "profesor_nombre": "Carlos Gómez",
                "historial": [
                    {
                        "semestre": "2024-2",
                        "grupos": 3,
                        "estudiantes": 82,
                        "promedio_grupos": 4.0,
                        "tasa_aprobacion": 92.7,
                        "promedio_asistencia": 90.5
                    },
                    {
                        "semestre": "2024-1",
                        "grupos": 2,
                        "estudiantes": 55,
                        "promedio_grupos": 4.2,
                        "tasa_aprobacion": 94.5,
                        "promedio_asistencia": 91.8
                    }
                ]
            }
        }
    )


class ProfesorDisponibilidad(BaseModel):
    """
    Schema para consultar disponibilidad horaria del profesor.
    
    Usado en: GET /api/v1/profesores/{id}/disponibilidad
    
    Muestra los bloques ocupados y libres del profesor.
    """
    profesor_id: int
    profesor_nombre: str
    semestre: str
    horario_ocupado: list[dict] = Field(
        ...,
        description="Bloques de horario donde el profesor tiene clase"
    )
    horas_ocupadas: float = Field(..., description="Total de horas semanales ocupadas")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "profesor_id": 1,
                "profesor_nombre": "Carlos Gómez",
                "semestre": "2025-1",
                "horario_ocupado": [
                    {
                        "dia": "Lunes",
                        "hora_inicio": "08:00",
                        "hora_fin": "10:00",
                        "curso": "IS-101",
                        "grupo_id": 1,
                        "salon": "Bloque 5 - 101"
                    },
                    {
                        "dia": "Martes",
                        "hora_inicio": "14:00",
                        "hora_fin": "16:00",
                        "curso": "IS-201",
                        "grupo_id": 5,
                        "salon": "Laboratorio 2"
                    }
                ],
                "horas_ocupadas": 12.0
            }
        }
    )


class ProfesorFiltros(BaseModel):
    """
    Schema para filtrar profesores en consultas.
    
    Usado en: GET /api/v1/profesores?filters
    """
    facultad_id: Optional[int] = Field(None, gt=0, description="Filtrar por facultad")
    titulo_academico: Optional[str] = Field(
        None,
        description="Filtrar por título (búsqueda parcial)"
    )
    con_grupos_disponibles: Optional[bool] = Field(
        None,
        description="Solo profesores con grupos activos"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "facultad_id": 1,
                "con_grupos_disponibles": True
            }
        }
    )
