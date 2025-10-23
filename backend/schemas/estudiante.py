"""
Schemas de Pydantic para Estudiante
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal

from models.estudiante import EstadoAcademicoEstudiante


class EstudianteBase(BaseModel):
    """
    Schema base con los campos comunes de Estudiante.
    Otros schemas heredan de este.
    """
    documento: Optional[str] = Field(
        None,
        max_length=50,
        description="Número de documento de identidad"
    )
    tipo_documento: Optional[str] = Field(
        None,
        max_length=50,
        description="Tipo de documento (Cédula, Pasaporte, TI)"
    )


class EstudianteCreate(EstudianteBase):
    """
    Schema para crear un perfil de estudiante.
    
    Usado en: POST /api/v1/estudiantes
    """
    usuario_id: int = Field(..., gt=0, description="ID del usuario asociado")
    programa_id: int = Field(..., gt=0, description="ID del programa académico")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "usuario_id": 5,
                "programa_id": 1,
                "documento": "1234567890",
                "tipo_documento": "Cédula"
            }
        }
    )


class EstudianteUpdate(BaseModel):
    """
    Schema para actualizar el perfil de un estudiante.
    
    Usado en: PUT/PATCH /api/v1/estudiantes/{id}
    """
    documento: Optional[str] = Field(None, max_length=50)
    tipo_documento: Optional[str] = Field(None, max_length=50)
    programa_id: Optional[int] = Field(None, gt=0, description="Cambiar de programa")
    estado_academico: Optional[EstadoAcademicoEstudiante] = Field(
        None,
        description="Actualizar estado académico"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado_academico": "En Prueba Academica"
            }
        }
    )


class EstudianteInDB(EstudianteBase):
    """
    Schema que representa un estudiante en la base de datos.
    
    Incluye todos los campos del modelo.
    """
    id: int
    usuario_id: int
    programa_id: int
    estado_academico: EstadoAcademicoEstudiante
    
    model_config = ConfigDict(from_attributes=True)


class EstudiantePublic(EstudianteInDB):
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
                "programa_id": 1,
                "documento": "1234567890",
                "tipo_documento": "Cédula",
                "estado_academico": "Matriculado"
            }
        }
    )


class EstudianteConUsuario(EstudiantePublic):
    """
    Schema extendido que incluye información del usuario.
    
    Usado en: GET /api/v1/estudiantes/{id}/detalles
    
    Incluye datos de identidad del usuario asociado.
    """
    # Información del usuario
    usuario_nombre: str = Field(..., description="Nombre del usuario")
    usuario_apellido: str = Field(..., description="Apellido del usuario")
    usuario_correo: str = Field(..., description="Correo electrónico")
    usuario_avatar_url: Optional[str] = Field(None, description="URL del avatar")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "usuario_id": 5,
                "programa_id": 1,
                "documento": "1234567890",
                "tipo_documento": "Cédula",
                "estado_academico": "Matriculado",
                "usuario_nombre": "Juan",
                "usuario_apellido": "Pérez García",
                "usuario_correo": "juan.perez@universidad.edu",
                "usuario_avatar_url": "https://storage.example.com/avatars/juan.jpg"
            }
        }
    )


class EstudianteCompleto(EstudianteConUsuario):
    """
    Schema completo que incluye información del programa académico.
    
    Usado en: GET /api/v1/estudiantes/{id}/completo
    
    Vista completa con usuario y programa.
    """
    # Información del programa
    programa_nombre: str = Field(..., description="Nombre del programa académico")
    programa_codigo: str = Field(..., description="Código del programa")
    facultad_nombre: str = Field(..., description="Nombre de la facultad")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "usuario_id": 5,
                "programa_id": 1,
                "documento": "1234567890",
                "tipo_documento": "Cédula",
                "estado_academico": "Matriculado",
                "usuario_nombre": "Juan",
                "usuario_apellido": "Pérez García",
                "usuario_correo": "juan.perez@universidad.edu",
                "usuario_avatar_url": "https://...",
                "programa_nombre": "Ingeniería de Sistemas",
                "programa_codigo": "IS",
                "facultad_nombre": "Facultad de Ingeniería"
            }
        }
    )


class EstudiantePerfil(EstudianteCompleto):
    """
    Schema del perfil del estudiante autenticado.
    
    Usado en: GET /api/v1/estudiantes/me
    
    Vista completa del perfil propio con estadísticas.
    """
    # Estadísticas académicas
    total_grupos_inscritos: int = Field(..., description="Total de grupos en este semestre")
    total_creditos_actuales: int = Field(..., description="Créditos inscritos actualmente")
    promedio_acumulado: Optional[Decimal] = Field(
        None,
        description="Promedio académico acumulado"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "usuario_id": 5,
                "programa_id": 1,
                "documento": "1234567890",
                "tipo_documento": "Cédula",
                "estado_academico": "Matriculado",
                "usuario_nombre": "Juan",
                "usuario_apellido": "Pérez García",
                "usuario_correo": "juan.perez@universidad.edu",
                "programa_nombre": "Ingeniería de Sistemas",
                "programa_codigo": "IS",
                "facultad_nombre": "Facultad de Ingeniería",
                "total_grupos_inscritos": 5,
                "total_creditos_actuales": 15,
                "promedio_acumulado": 4.2
            }
        }
    )


class EstudianteList(BaseModel):
    """
    Schema para listar estudiantes con información resumida.
    
    Usado en: GET /api/v1/estudiantes
    """
    id: int
    usuario_nombre: str
    usuario_apellido: str
    documento: Optional[str]
    programa_nombre: str
    estado_academico: EstadoAcademicoEstudiante
    
    model_config = ConfigDict(from_attributes=True)


class EstudianteRendimiento(BaseModel):
    """
    Schema para el rendimiento académico de un estudiante.
    
    Usado en: GET /api/v1/estudiantes/{id}/rendimiento
    
    Muestra estadísticas académicas detalladas.
    """
    estudiante_id: int
    # Información general
    total_semestres_cursados: int
    total_materias_cursadas: int
    total_materias_aprobadas: int
    total_materias_reprobadas: int
    
    # Promedios
    promedio_acumulado: Optional[Decimal] = Field(None, description="GPA general")
    promedio_ultimo_semestre: Optional[Decimal] = Field(None, description="GPA último semestre")
    
    # Asistencia
    porcentaje_asistencia_promedio: Optional[float] = Field(
        None,
        description="Porcentaje promedio de asistencia"
    )
    
    # Estado
    creditos_aprobados: int
    creditos_totales_programa: int
    porcentaje_avance: float = Field(..., description="Porcentaje de avance en el programa")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estudiante_id": 1,
                "total_semestres_cursados": 5,
                "total_materias_cursadas": 25,
                "total_materias_aprobadas": 23,
                "total_materias_reprobadas": 2,
                "promedio_acumulado": 4.2,
                "promedio_ultimo_semestre": 4.5,
                "porcentaje_asistencia_promedio": 92.5,
                "creditos_aprobados": 115,
                "creditos_totales_programa": 160,
                "porcentaje_avance": 71.87
            }
        }
    )


class EstudianteHistorialAcademico(BaseModel):
    """
    Schema para el historial académico de un estudiante.
    
    Usado en: GET /api/v1/estudiantes/{id}/historial
    
    Lista de todos los grupos cursados con sus notas.
    """
    estudiante_id: int
    programa_nombre: str
    semestre_actual: str
    
    # Historial por semestre
    historial: list[dict] = Field(
        ...,
        description="Lista de semestres con cursos y notas"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estudiante_id": 1,
                "programa_nombre": "Ingeniería de Sistemas",
                "semestre_actual": "2025-2",
                "historial": [
                    {
                        "semestre": "2024-1",
                        "cursos": [
                            {
                                "codigo": "IS-101",
                                "nombre": "Introducción a la Programación",
                                "nota_definitiva": 4.5,
                                "estado": "Aprobado"
                            },
                            {
                                "codigo": "MAT-101",
                                "nombre": "Cálculo I",
                                "nota_definitiva": 4.0,
                                "estado": "Aprobado"
                            }
                        ],
                        "promedio_semestre": 4.25
                    }
                ]
            }
        }
    )


class EstudianteEstadoUpdate(BaseModel):
    """
    Schema para cambiar el estado académico de un estudiante.
    
    Usado en: PATCH /api/v1/estudiantes/{id}/estado
    
    Operación administrativa para actualizar estado.
    """
    estado_academico: EstadoAcademicoEstudiante = Field(
        ...,
        description="Nuevo estado académico"
    )
    motivo: Optional[str] = Field(
        None,
        description="Motivo del cambio de estado (opcional)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado_academico": "En Prueba Academica",
                "motivo": "Promedio por debajo de 3.0 en el último semestre"
            }
        }
    )


class EstudianteFiltros(BaseModel):
    """
    Schema para filtrar estudiantes en consultas.
    
    Usado en: GET /api/v1/estudiantes?filters
    """
    programa_id: Optional[int] = Field(None, gt=0, description="Filtrar por programa")
    estado_academico: Optional[EstadoAcademicoEstudiante] = Field(
        None,
        description="Filtrar por estado"
    )
    buscar: Optional[str] = Field(
        None,
        description="Buscar por nombre, apellido o documento"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "programa_id": 1,
                "estado_academico": "Matriculado",
                "buscar": "juan"
            }
        }
    )
