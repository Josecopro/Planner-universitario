"""
Schemas de Pydantic para Facultad
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class FacultadBase(BaseModel):
    """
    Schema base con los campos comunes de Facultad.
    Otros schemas heredan de este.
    """
    codigo: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Código único de la facultad, ej: ING, CIEN, ADMIN"
    )
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Nombre completo de la facultad"
    )


class FacultadCreate(FacultadBase):
    """
    Schema para crear una nueva facultad.
    
    Usado en: POST /api/v1/facultades
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "codigo": "ING",
                "nombre": "Facultad de Ingeniería"
            }
        }
    )


class FacultadUpdate(BaseModel):
    """
    Schema para actualizar una facultad existente.
    
    Usado en: PUT/PATCH /api/v1/facultades/{id}
    """
    codigo: Optional[str] = Field(None, min_length=1, max_length=20)
    nombre: Optional[str] = Field(None, min_length=1, max_length=150)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Facultad de Ingeniería y Tecnología"
            }
        }
    )


class FacultadInDB(FacultadBase):
    """
    Schema que representa una facultad en la base de datos.
    
    Incluye todos los campos del modelo.
    """
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class FacultadPublic(FacultadInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "codigo": "ING",
                "nombre": "Facultad de Ingeniería"
            }
        }
    )


class FacultadList(BaseModel):
    """
    Schema para listar facultades con información resumida.
    
    Usado en: GET /api/v1/facultades
    """
    id: int
    codigo: str
    nombre: str
    
    model_config = ConfigDict(from_attributes=True)


class FacultadConContadores(FacultadPublic):
    """
    Schema de facultad con contadores de entidades relacionadas.
    
    Usado en: GET /api/v1/facultades/{id}/detalles
    
    Incluye contadores de programas, cursos y profesores.
    """
    total_programas: int = Field(..., description="Número de programas académicos")
    total_cursos: int = Field(..., description="Número de cursos")
    total_profesores: int = Field(..., description="Número de profesores adscritos")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "codigo": "ING",
                "nombre": "Facultad de Ingeniería",
                "total_programas": 5,
                "total_cursos": 120,
                "total_profesores": 45
            }
        }
    )


class FacultadConProgramas(FacultadPublic):
    """
    Schema de facultad con lista de programas académicos.
    
    Usado en: GET /api/v1/facultades/{id}/programas
    """
    programas: list[dict] = Field(
        ...,
        description="Lista de programas académicos de la facultad"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "codigo": "ING",
                "nombre": "Facultad de Ingeniería",
                "programas": [
                    {
                        "id": 1,
                        "codigo": "IS",
                        "nombre": "Ingeniería de Sistemas",
                        "estado": "Activo"
                    },
                    {
                        "id": 2,
                        "codigo": "IC",
                        "nombre": "Ingeniería Civil",
                        "estado": "Activo"
                    }
                ]
            }
        }
    )


class FacultadEstadisticas(BaseModel):
    """
    Schema para estadísticas detalladas de una facultad.
    
    Usado en: GET /api/v1/facultades/{id}/estadisticas
    
    Muestra información agregada de la facultad.
    """
    facultad_id: int
    facultad_nombre: str
    
    # Programas
    total_programas_activos: int
    total_programas_inactivos: int
    
    # Cursos
    total_cursos_activos: int
    total_cursos_inactivos: int
    
    # Estudiantes
    total_estudiantes_activos: int = Field(
        ...,
        description="Estudiantes matriculados en programas de la facultad"
    )
    
    # Profesores
    total_profesores: int
    
    # Grupos
    total_grupos_semestre_actual: int = Field(
        ...,
        description="Grupos activos en el semestre actual"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "facultad_id": 1,
                "facultad_nombre": "Facultad de Ingeniería",
                "total_programas_activos": 5,
                "total_programas_inactivos": 0,
                "total_cursos_activos": 120,
                "total_cursos_inactivos": 10,
                "total_estudiantes_activos": 850,
                "total_profesores": 45,
                "total_grupos_semestre_actual": 95
            }
        }
    )


class FacultadResumenAcademico(BaseModel):
    """
    Schema para el resumen académico de una facultad.
    
    Usado en: GET /api/v1/facultades/{id}/resumen-academico
    """
    facultad_id: int
    facultad_nombre: str
    
    # Métricas por programa
    programas_con_metricas: list[dict] = Field(
        ...,
        description="Lista de programas con sus métricas"
    )
    
    # Métricas generales
    promedio_estudiantes_por_programa: float
    tasa_ocupacion_grupos: float = Field(
        ...,
        description="Porcentaje promedio de ocupación de los grupos"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "facultad_id": 1,
                "facultad_nombre": "Facultad de Ingeniería",
                "programas_con_metricas": [
                    {
                        "programa_id": 1,
                        "programa_nombre": "Ingeniería de Sistemas",
                        "total_estudiantes": 320,
                        "promedio_general": 4.1
                    }
                ],
                "promedio_estudiantes_por_programa": 170.0,
                "tasa_ocupacion_grupos": 85.5
            }
        }
    )


class FacultadOrganigrama(BaseModel):
    """
    Schema para el organigrama de la facultad.
    
    Usado en: GET /api/v1/facultades/{id}/organigrama
    """
    facultad: dict = Field(..., description="Información de la facultad")
    programas: list[dict] = Field(..., description="Programas con sus cursos")
    profesores: list[dict] = Field(..., description="Profesores de la facultad")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "facultad": {
                    "id": 1,
                    "codigo": "ING",
                    "nombre": "Facultad de Ingeniería"
                },
                "programas": [
                    {
                        "id": 1,
                        "nombre": "Ingeniería de Sistemas",
                        "total_estudiantes": 320,
                        "cursos": 45
                    }
                ],
                "profesores": [
                    {
                        "id": 1,
                        "nombre": "Dr. Carlos Gómez",
                        "titulo_academico": "PhD en Ingeniería"
                    }
                ]
            }
        }
    )


class FacultadCatalogo(BaseModel):
    """
    Schema simplificado para el catálogo público de facultades.
    
    Usado en: GET /api/v1/facultades/catalogo
    """
    id: int
    codigo: str
    nombre: str
    total_programas: int
    programas_destacados: list[str] = Field(
        ...,
        description="Lista de nombres de programas principales"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "codigo": "ING",
                "nombre": "Facultad de Ingeniería",
                "total_programas": 5,
                "programas_destacados": [
                    "Ingeniería de Sistemas",
                    "Ingeniería Civil",
                    "Ingeniería Industrial"
                ]
            }
        }
    )


class FacultadFiltros(BaseModel):
    """
    Schema para filtrar facultades en consultas.
    
    Usado en: GET /api/v1/facultades?filters
    """
    buscar: Optional[str] = Field(
        None,
        min_length=1,
        description="Buscar en código o nombre de la facultad"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "buscar": "ingeniería"
            }
        }
    )
