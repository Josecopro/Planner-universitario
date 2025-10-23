"""
Schemas de Pydantic para Programa Académico
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional

from models.programa_academico import EstadoPrograma


class ProgramaAcademicoBase(BaseModel):
    """
    Schema base con los campos comunes de Programa Académico.
    Otros schemas heredan de este.
    """
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre del programa, ej: Ingeniería de Sistemas"
    )
    codigo: str = Field(
        ...,
        min_length=1,
        max_length=30,
        description="Código único del programa, ej: IS, IC, MED"
    )
    duracion_semestres: Optional[int] = Field(
        None,
        ge=1,
        le=20,
        description="Duración del programa en semestres"
    )
    
    @field_validator('codigo')
    @classmethod
    def validar_codigo(cls, v: str) -> str:
        """Valida que el código sea en mayúsculas y sin espacios"""
        if not v.isupper():
            raise ValueError('El código debe estar en mayúsculas')
        if ' ' in v:
            raise ValueError('El código no puede contener espacios')
        return v


class ProgramaAcademicoCreate(ProgramaAcademicoBase):
    """
    Schema para crear un nuevo programa académico.
    
    Usado en: POST /api/v1/programas-academicos
    """
    facultad_id: int = Field(..., gt=0, description="ID de la facultad")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Ingeniería de Sistemas",
                "codigo": "IS",
                "facultad_id": 1,
                "duracion_semestres": 10
            }
        }
    )


class ProgramaAcademicoUpdate(BaseModel):
    """
    Schema para actualizar un programa académico existente.
    
    Usado en: PUT/PATCH /api/v1/programas-academicos/{id}
    """
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    codigo: Optional[str] = Field(None, min_length=1, max_length=30)
    facultad_id: Optional[int] = Field(None, gt=0)
    duracion_semestres: Optional[int] = Field(None, ge=1, le=20)
    estado: Optional[EstadoPrograma] = Field(None, description="Cambiar estado del programa")
    
    @field_validator('codigo')
    @classmethod
    def validar_codigo(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el código sea en mayúsculas y sin espacios si se proporciona"""
        if v is None:
            return v
        if not v.isupper():
            raise ValueError('El código debe estar en mayúsculas')
        if ' ' in v:
            raise ValueError('El código no puede contener espacios')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "duracion_semestres": 10,
                "estado": "Activo"
            }
        }
    )


class ProgramaAcademicoEstadoUpdate(BaseModel):
    """
    Schema para cambiar solo el estado de un programa.
    
    Usado en: PATCH /api/v1/programas-academicos/{id}/estado
    """
    estado: EstadoPrograma = Field(..., description="Nuevo estado del programa")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "Inactivo"
            }
        }
    )


class ProgramaAcademicoInDB(ProgramaAcademicoBase):
    """
    Schema que representa un programa académico en la base de datos.
    
    Incluye todos los campos del modelo.
    """
    id: int
    facultad_id: int
    estado: EstadoPrograma
    
    model_config = ConfigDict(from_attributes=True)


class ProgramaAcademicoPublic(ProgramaAcademicoInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Ingeniería de Sistemas",
                "codigo": "IS",
                "facultad_id": 1,
                "duracion_semestres": 10,
                "estado": "Activo"
            }
        }
    )


class ProgramaAcademicoConFacultad(ProgramaAcademicoPublic):
    """
    Schema extendido que incluye información de la facultad.
    
    Usado en: GET /api/v1/programas-academicos/{id}/detalles
    """
    facultad_nombre: str = Field(..., description="Nombre de la facultad")
    facultad_codigo: str = Field(..., description="Código de la facultad")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Ingeniería de Sistemas",
                "codigo": "IS",
                "facultad_id": 1,
                "duracion_semestres": 10,
                "estado": "Activo",
                "facultad_nombre": "Facultad de Ingeniería",
                "facultad_codigo": "ING"
            }
        }
    )


class ProgramaAcademicoList(BaseModel):
    """
    Schema para listar programas académicos con información resumida.
    
    Usado en: GET /api/v1/programas-academicos
              GET /api/v1/facultades/{id}/programas
    """
    id: int
    nombre: str
    codigo: str
    facultad_nombre: str
    duracion_semestres: Optional[int]
    estado: EstadoPrograma
    total_estudiantes: int = Field(..., description="Estudiantes inscritos en el programa")
    
    model_config = ConfigDict(from_attributes=True)


class ProgramaAcademicoConContadores(ProgramaAcademicoConFacultad):
    """
    Schema que incluye contadores estadísticos del programa.
    
    Usado en: GET /api/v1/programas-academicos/{id}/contadores
    
    Vista con información cuantitativa.
    """
    total_estudiantes: int = Field(..., description="Total de estudiantes activos")
    estudiantes_nuevos: int = Field(..., description="Estudiantes de primer semestre")
    estudiantes_graduados: int = Field(..., description="Graduados del programa")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Ingeniería de Sistemas",
                "codigo": "IS",
                "facultad_id": 1,
                "duracion_semestres": 10,
                "estado": "Activo",
                "facultad_nombre": "Facultad de Ingeniería",
                "facultad_codigo": "ING",
                "total_estudiantes": 450,
                "estudiantes_nuevos": 52,
                "estudiantes_graduados": 38
            }
        }
    )


# =================================================================
#  SCHEMAS DE ESTADÍSTICAS
# =================================================================

class ProgramaAcademicoEstadisticas(BaseModel):
    """
    Schema para estadísticas detalladas del programa.
    
    Usado en: GET /api/v1/programas-academicos/{id}/estadisticas
    
    Dashboard completo del programa académico.
    """
    programa_id: int
    programa_nombre: str
    programa_codigo: str
    
    # Estudiantes
    total_estudiantes: int
    estudiantes_activos: int
    estudiantes_suspendidos: int
    estudiantes_inactivos: int
    estudiantes_graduados: int
    
    # Distribución por semestre
    distribucion_por_semestre: list[dict] = Field(
        ...,
        description="Cantidad de estudiantes por semestre académico"
    )
    
    # Promedios
    promedio_general_programa: Optional[float] = Field(
        None,
        description="Promedio académico general del programa"
    )
    
    # Tasas
    tasa_desercion: Optional[float] = Field(
        None,
        description="Porcentaje de deserción del programa"
    )
    tasa_graduacion: Optional[float] = Field(
        None,
        description="Porcentaje de graduación"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "programa_id": 1,
                "programa_nombre": "Ingeniería de Sistemas",
                "programa_codigo": "IS",
                "total_estudiantes": 450,
                "estudiantes_activos": 420,
                "estudiantes_suspendidos": 15,
                "estudiantes_inactivos": 15,
                "estudiantes_graduados": 380,
                "distribucion_por_semestre": [
                    {"semestre": 1, "cantidad": 52},
                    {"semestre": 2, "cantidad": 48},
                    {"semestre": 3, "cantidad": 45},
                    {"semestre": 4, "cantidad": 42},
                    {"semestre": 5, "cantidad": 40},
                    {"semestre": 6, "cantidad": 38},
                    {"semestre": 7, "cantidad": 35},
                    {"semestre": 8, "cantidad": 32},
                    {"semestre": 9, "cantidad": 28},
                    {"semestre": 10, "cantidad": 60}
                ],
                "promedio_general_programa": 3.9,
                "tasa_desercion": 15.5,
                "tasa_graduacion": 78.2
            }
        }
    )


class ProgramaAcademicoPensum(BaseModel):
    """
    Schema para el pensum o plan de estudios del programa.
    
    Usado en: GET /api/v1/programas-academicos/{id}/pensum
    
    Estructura curricular del programa.
    """
    programa_id: int
    programa_nombre: str
    duracion_semestres: Optional[int]
    
    # Información curricular
    total_creditos: int = Field(..., description="Total de créditos del programa")
    cursos_por_semestre: list[dict] = Field(
        ...,
        description="Cursos organizados por semestre sugerido"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "programa_id": 1,
                "programa_nombre": "Ingeniería de Sistemas",
                "duracion_semestres": 10,
                "total_creditos": 160,
                "cursos_por_semestre": [
                    {
                        "semestre": 1,
                        "cursos": [
                            {
                                "codigo": "IS-101",
                                "nombre": "Introducción a la Programación",
                                "creditos": 3,
                                "tipo": "Obligatorio"
                            },
                            {
                                "codigo": "MAT-101",
                                "nombre": "Cálculo I",
                                "creditos": 4,
                                "tipo": "Obligatorio"
                            }
                        ]
                    },
                    {
                        "semestre": 2,
                        "cursos": [
                            {
                                "codigo": "IS-201",
                                "nombre": "Estructuras de Datos",
                                "creditos": 3,
                                "tipo": "Obligatorio"
                            }
                        ]
                    }
                ]
            }
        }
    )


class ProgramaAcademicoRendimiento(BaseModel):
    """
    Schema para análisis de rendimiento del programa.
    
    Usado en: GET /api/v1/programas-academicos/{id}/rendimiento
    
    Análisis de desempeño académico del programa.
    """
    programa_id: int
    programa_nombre: str
    
    # Promedios por cohorte
    promedios_por_cohorte: list[dict] = Field(
        ...,
        description="Promedio académico por año de ingreso"
    )
    
    # Cursos con mayor dificultad
    cursos_alta_reprobacion: list[dict] = Field(
        ...,
        description="Cursos con mayor tasa de reprobación"
    )
    
    # Tiempo de graduación
    tiempo_promedio_graduacion: Optional[float] = Field(
        None,
        description="Semestres promedio para graduarse"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "programa_id": 1,
                "programa_nombre": "Ingeniería de Sistemas",
                "promedios_por_cohorte": [
                    {"cohorte": "2024", "promedio": 4.0, "estudiantes": 52},
                    {"cohorte": "2023", "promedio": 3.9, "estudiantes": 48},
                    {"cohorte": "2022", "promedio": 3.8, "estudiantes": 45}
                ],
                "cursos_alta_reprobacion": [
                    {
                        "codigo": "MAT-201",
                        "nombre": "Cálculo II",
                        "tasa_reprobacion": 35.2
                    },
                    {
                        "codigo": "IS-301",
                        "nombre": "Estructuras de Datos",
                        "tasa_reprobacion": 28.5
                    }
                ],
                "tiempo_promedio_graduacion": 11.2
            }
        }
    )


# =================================================================
#  SCHEMAS DE CATÁLOGO
# =================================================================

class ProgramaAcademicoCatalogo(BaseModel):
    """
    Schema simplificado para catálogos y selectores.
    
    Usado en: GET /api/v1/programas-academicos/catalogo
    
    Vista mínima para dropdowns y listas de selección.
    """
    id: int
    nombre: str
    codigo: str
    facultad_nombre: str
    estado: EstadoPrograma
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Ingeniería de Sistemas",
                "codigo": "IS",
                "facultad_nombre": "Facultad de Ingeniería",
                "estado": "Activo"
            }
        }
    )


# =================================================================
#  SCHEMAS DE FILTROS
# =================================================================

class ProgramaAcademicoFiltros(BaseModel):
    """
    Schema para filtrar programas académicos en consultas.
    
    Usado en: GET /api/v1/programas-academicos?filters
    """
    facultad_id: Optional[int] = Field(None, gt=0, description="Filtrar por facultad")
    estado: Optional[EstadoPrograma] = Field(None, description="Filtrar por estado")
    duracion_minima: Optional[int] = Field(None, ge=1, description="Duración mínima en semestres")
    duracion_maxima: Optional[int] = Field(None, ge=1, description="Duración máxima en semestres")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "facultad_id": 1,
                "estado": "Activo",
                "duracion_minima": 8,
                "duracion_maxima": 12
            }
        }
    )
