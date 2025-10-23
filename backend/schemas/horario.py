"""
Schemas de Pydantic para Horario
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from datetime import time


class HorarioBase(BaseModel):
    """
    Schema base con los campos comunes de Horario.
    Otros schemas heredan de este.
    """
    dia: str = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Día de la semana (Lunes, Martes, Miércoles, etc.)"
    )
    hora_inicio: time = Field(..., description="Hora de inicio de la clase")
    hora_fin: time = Field(..., description="Hora de finalización de la clase")
    salon: Optional[str] = Field(
        None,
        max_length=50,
        description="Salón o ubicación, ej: Bloque 5 - 101, Virtual"
    )
    
    @field_validator('dia')
    @classmethod
    def validar_dia(cls, v: str) -> str:
        """Valida que el día sea uno de los días de la semana válidos"""
        dias_validos = [
            'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'
        ]
        if v not in dias_validos:
            raise ValueError(f'El día debe ser uno de: {", ".join(dias_validos)}')
        return v
    
    @field_validator('hora_fin')
    @classmethod
    def validar_hora_fin(cls, v: time, info) -> time:
        """Valida que hora_fin sea mayor que hora_inicio"""
        if 'hora_inicio' in info.data and v <= info.data['hora_inicio']:
            raise ValueError('La hora de finalización debe ser mayor que la hora de inicio')
        return v


class HorarioCreate(HorarioBase):
    """
    Schema para crear un nuevo horario.
    
    Usado en: POST /api/v1/horarios
              POST /api/v1/grupos/{id}/horarios
    """
    grupo_id: int = Field(..., gt=0, description="ID del grupo al que pertenece")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grupo_id": 1,
                "dia": "Lunes",
                "hora_inicio": "08:00:00",
                "hora_fin": "10:00:00",
                "salon": "Bloque 5 - 101"
            }
        }
    )


class HorarioCreateBulk(BaseModel):
    """
    Schema para crear múltiples horarios de un grupo a la vez.
    
    Usado en: POST /api/v1/grupos/{id}/horarios/bulk
    
    Permite crear varios bloques de horario en una sola operación.
    """
    grupo_id: int = Field(..., gt=0, description="ID del grupo")
    horarios: list[HorarioBase] = Field(
        ...,
        min_length=1,
        description="Lista de bloques de horario a crear"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "grupo_id": 1,
                "horarios": [
                    {
                        "dia": "Lunes",
                        "hora_inicio": "08:00:00",
                        "hora_fin": "10:00:00",
                        "salon": "Bloque 5 - 101"
                    },
                    {
                        "dia": "Miércoles",
                        "hora_inicio": "08:00:00",
                        "hora_fin": "10:00:00",
                        "salon": "Bloque 5 - 101"
                    }
                ]
            }
        }
    )


class HorarioUpdate(BaseModel):
    """
    Schema para actualizar un horario existente.
    
    Usado en: PUT/PATCH /api/v1/horarios/{id}
    """
    dia: Optional[str] = Field(None, min_length=1, max_length=15)
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    salon: Optional[str] = Field(None, max_length=50)
    
    @field_validator('dia')
    @classmethod
    def validar_dia(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el día sea uno de los días válidos si se proporciona"""
        if v is None:
            return v
        dias_validos = [
            'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'
        ]
        if v not in dias_validos:
            raise ValueError(f'El día debe ser uno de: {", ".join(dias_validos)}')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "salon": "Bloque 3 - 205",
                "hora_inicio": "14:00:00",
                "hora_fin": "16:00:00"
            }
        }
    )


class HorarioInDB(HorarioBase):
    """
    Schema que representa un horario en la base de datos.
    
    Incluye todos los campos del modelo.
    """
    id: int
    grupo_id: int
    
    model_config = ConfigDict(from_attributes=True)


class HorarioPublic(HorarioInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "grupo_id": 1,
                "dia": "Lunes",
                "hora_inicio": "08:00:00",
                "hora_fin": "10:00:00",
                "salon": "Bloque 5 - 101"
            }
        }
    )


class HorarioConGrupo(HorarioPublic):
    """
    Schema extendido que incluye información del grupo.
    
    Usado en: GET /api/v1/horarios/{id}/detalles
    """
    # Información del grupo
    grupo_semestre: str = Field(..., description="Semestre del grupo")
    
    # Información del curso
    curso_codigo: str = Field(..., description="Código del curso")
    curso_nombre: str = Field(..., description="Nombre del curso")
    
    # Información del profesor (opcional)
    profesor_nombre: Optional[str] = Field(None, description="Nombre del profesor")
    profesor_apellido: Optional[str] = Field(None, description="Apellido del profesor")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "grupo_id": 1,
                "dia": "Lunes",
                "hora_inicio": "08:00:00",
                "hora_fin": "10:00:00",
                "salon": "Bloque 5 - 101",
                "grupo_semestre": "2025-1",
                "curso_codigo": "IS-101",
                "curso_nombre": "Introducción a la Programación",
                "profesor_nombre": "Carlos",
                "profesor_apellido": "Gómez"
            }
        }
    )


class HorarioSemanal(BaseModel):
    """
    Schema para visualización de horario semanal.
    
    Usado en: GET /api/v1/estudiantes/me/horario-semanal
              GET /api/v1/profesores/me/horario-semanal
    """
    dia: str
    bloques: list[dict] = Field(
        ...,
        description="Bloques de clase en este día (hora_inicio, hora_fin, curso, grupo, salon)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "dia": "Lunes",
                "bloques": [
                    {
                        "hora_inicio": "08:00:00",
                        "hora_fin": "10:00:00",
                        "curso_codigo": "IS-101",
                        "curso_nombre": "Introducción a la Programación",
                        "grupo_id": 1,
                        "salon": "Bloque 5 - 101",
                        "profesor": "Carlos Gómez"
                    },
                    {
                        "hora_inicio": "14:00:00",
                        "hora_fin": "16:00:00",
                        "curso_codigo": "IS-201",
                        "curso_nombre": "Estructuras de Datos",
                        "grupo_id": 5,
                        "salon": "Laboratorio 2",
                        "profesor": "Ana Torres"
                    }
                ]
            }
        }
    )


class HorarioConflicto(BaseModel):
    """
    Schema para detectar conflictos de horarios.
    
    Usado en: POST /api/v1/horarios/validar-conflictos
    
    Identifica solapamientos de horario para un profesor o estudiante.
    """
    tiene_conflicto: bool = Field(..., description="Indica si hay conflicto")
    horarios_conflictivos: list[dict] = Field(
        default_factory=list,
        description="Lista de horarios que se solapan"
    )
    mensaje: str = Field(..., description="Descripción del conflicto o confirmación")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tiene_conflicto": True,
                "horarios_conflictivos": [
                    {
                        "horario_id": 1,
                        "dia": "Lunes",
                        "hora_inicio": "08:00:00",
                        "hora_fin": "10:00:00",
                        "curso": "IS-101",
                        "salon": "Bloque 5 - 101"
                    },
                    {
                        "horario_id": 12,
                        "dia": "Lunes",
                        "hora_inicio": "09:00:00",
                        "hora_fin": "11:00:00",
                        "curso": "IS-102",
                        "salon": "Bloque 3 - 205"
                    }
                ],
                "mensaje": "Conflicto detectado: Los horarios se solapan el Lunes de 09:00 a 10:00"
            }
        }
    )


class HorarioEstudiante(BaseModel):
    """
    Schema de horario desde la perspectiva del estudiante.
    
    Usado en: GET /api/v1/estudiantes/me/horarios
    """
    id: int
    dia: str
    hora_inicio: time
    hora_fin: time
    salon: Optional[str]
    curso_codigo: str
    curso_nombre: str
    profesor_nombre: Optional[str]
    grupo_id: int
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "dia": "Lunes",
                "hora_inicio": "08:00:00",
                "hora_fin": "10:00:00",
                "salon": "Bloque 5 - 101",
                "curso_codigo": "IS-101",
                "curso_nombre": "Introducción a la Programación",
                "profesor_nombre": "Carlos Gómez",
                "grupo_id": 1
            }
        }
    )


class HorarioProfesor(BaseModel):
    """
    Schema de horario desde la perspectiva del profesor.
    
    Usado en: GET /api/v1/profesores/me/horarios
    """
    id: int
    dia: str
    hora_inicio: time
    hora_fin: time
    salon: Optional[str]
    curso_codigo: str
    curso_nombre: str
    grupo_id: int
    total_estudiantes: int = Field(..., description="Estudiantes inscritos en el grupo")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "dia": "Lunes",
                "hora_inicio": "08:00:00",
                "hora_fin": "10:00:00",
                "salon": "Bloque 5 - 101",
                "curso_codigo": "IS-101",
                "curso_nombre": "Introducción a la Programación",
                "grupo_id": 1,
                "total_estudiantes": 28
            }
        }
    )


class HorarioFiltros(BaseModel):
    """
    Schema para filtrar horarios en consultas.
    
    Usado en: GET /api/v1/horarios?filters
    """
    grupo_id: Optional[int] = Field(None, gt=0, description="Filtrar por grupo")
    dia: Optional[str] = Field(None, description="Filtrar por día")
    salon: Optional[str] = Field(None, description="Filtrar por salón")
    hora_desde: Optional[time] = Field(None, description="Horarios después de esta hora")
    hora_hasta: Optional[time] = Field(None, description="Horarios antes de esta hora")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "dia": "Lunes",
                "hora_desde": "08:00:00",
                "hora_hasta": "12:00:00"
            }
        }
    )


class DisponibilidadSalon(BaseModel):
    """
    Schema para consultar disponibilidad de salones.
    
    Usado en: GET /api/v1/horarios/salones/disponibilidad
    
    Muestra qué salones están ocupados en un día/hora específicos.
    """
    salon: str
    dia: str
    hora_inicio: time
    hora_fin: time
    disponible: bool = Field(..., description="Indica si el salón está libre")
    ocupado_por: Optional[str] = Field(
        None,
        description="Nombre del curso que ocupa el salón (si aplica)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "salon": "Bloque 5 - 101",
                "dia": "Lunes",
                "hora_inicio": "08:00:00",
                "hora_fin": "10:00:00",
                "disponible": False,
                "ocupado_por": "IS-101 - Introducción a la Programación"
            }
        }
    )
