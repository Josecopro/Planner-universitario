"""
Schemas de Pydantic para Curso
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from models.curso import EstadoCurso


class CursoBase(BaseModel):
    """
    Schema base con los campos comunes de Curso.
    Otros schemas heredan de este.
    """
    codigo: str = Field(
        ...,
        min_length=1,
        max_length=30,
        description="Código único de la asignatura, ej: IS-101, MAT-201"
    )
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nombre del curso, ej: Cálculo I"
    )


class CursoCreate(CursoBase):
    """
    Schema para crear un nuevo curso.
    
    Usado en: POST /api/v1/cursos
    """
    facultad_id: int = Field(..., gt=0, description="ID de la facultad a la que pertenece")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "codigo": "IS-101",
                "nombre": "Introducción a la Programación",
                "facultad_id": 1
            }
        }
    )


class CursoUpdate(BaseModel):
    """
    Schema para actualizar un curso existente.
    
    Usado en: PUT/PATCH /api/v1/cursos/{id}
    """
    codigo: Optional[str] = Field(None, min_length=1, max_length=30)
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    estado: Optional[EstadoCurso] = Field(None, description="Nuevo estado del curso")
    facultad_id: Optional[int] = Field(None, gt=0, description="Nueva facultad")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Introducción a la Programación I",
                "estado": "Activo"
            }
        }
    )


class CursoInDB(CursoBase):
    """
    Schema que representa un curso en la base de datos.
    
    Incluye todos los campos del modelo, incluyendo los generados automáticamente.
    """
    id: int
    facultad_id: int
    estado: EstadoCurso
    
    model_config = ConfigDict(from_attributes=True)


class CursoPublic(CursoInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    
    Incluye toda la información del curso.
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "codigo": "IS-101",
                "nombre": "Introducción a la Programación",
                "facultad_id": 1,
                "estado": "Activo"
            }
        }
    )


class CursoConFacultad(CursoPublic):
    """
    Schema extendido que incluye información de la facultad.
    
    Usado en: GET /api/v1/cursos/{id}/detalles
    """
    facultad_nombre: str = Field(..., description="Nombre de la facultad")
    facultad_codigo: str = Field(..., description="Código de la facultad")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "codigo": "IS-101",
                "nombre": "Introducción a la Programación",
                "facultad_id": 1,
                "estado": "Activo",
                "facultad_nombre": "Facultad de Ingeniería",
                "facultad_codigo": "ING"
            }
        }
    )


class CursoList(BaseModel):
    """
    Schema para listar cursos con información resumida.
    
    Usado en: GET /api/v1/cursos?facultad_id=X
    """
    id: int
    codigo: str
    nombre: str
    estado: EstadoCurso
    facultad_id: int
    
    model_config = ConfigDict(from_attributes=True)


class CursoConGrupos(CursoConFacultad):
    """
    Schema que incluye los grupos del curso.
    
    Usado en: GET /api/v1/cursos/{id}/grupos
    
    Muestra el curso con todos sus grupos en diferentes semestres.
    """
    total_grupos: int = Field(..., description="Número total de grupos del curso")
    grupos_activos: int = Field(..., description="Grupos en estado 'En Curso' o 'Abierto'")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "codigo": "IS-101",
                "nombre": "Introducción a la Programación",
                "facultad_id": 1,
                "estado": "Activo",
                "facultad_nombre": "Facultad de Ingeniería",
                "facultad_codigo": "ING",
                "total_grupos": 15,
                "grupos_activos": 3
            }
        }
    )


class CursoFiltros(BaseModel):
    """
    Schema para filtrar cursos en consultas.
    
    Usado en: GET /api/v1/cursos?filters
    
    Permite filtrar por facultad, estado, búsqueda por texto.
    """
    facultad_id: Optional[int] = Field(None, gt=0, description="Filtrar por facultad")
    estado: Optional[EstadoCurso] = Field(None, description="Filtrar por estado")
    buscar: Optional[str] = Field(
        None,
        min_length=1,
        description="Buscar en código o nombre del curso"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "facultad_id": 1,
                "estado": "Activo",
                "buscar": "programación"
            }
        }
    )


class CursoEstadisticas(BaseModel):
    """
    Schema para estadísticas de un curso.
    
    Usado en: GET /api/v1/cursos/{id}/estadisticas
    
    Muestra información agregada del curso a través del tiempo.
    """
    curso_id: int
    total_grupos_historico: int = Field(..., description="Total de grupos que ha tenido")
    total_estudiantes_historico: int = Field(..., description="Total de estudiantes que lo han cursado")
    promedio_estudiantes_por_grupo: float = Field(..., description="Promedio de estudiantes por grupo")
    semestres_ofrecido: list[str] = Field(..., description="Lista de semestres en que se ha ofrecido")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "curso_id": 1,
                "total_grupos_historico": 15,
                "total_estudiantes_historico": 450,
                "promedio_estudiantes_por_grupo": 30.0,
                "semestres_ofrecido": ["2023-1", "2023-2", "2024-1", "2024-2", "2025-1"]
            }
        }
    )


class CursoEstadoUpdate(BaseModel):
    """
    Schema para cambiar solo el estado de un curso.
    
    Usado en: PATCH /api/v1/cursos/{id}/estado
    """
    estado: EstadoCurso = Field(..., description="Nuevo estado del curso")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "En Revision"
            }
        }
    )


class CursoCatalogo(BaseModel):
    """
    Schema simplificado para mostrar el catálogo de cursos.
    
    Usado en: GET /api/v1/cursos/catalogo
    """
    id: int
    codigo: str
    nombre: str
    facultad_nombre: str
    tiene_grupos_disponibles: bool = Field(
        ...,
        description="Indica si hay grupos abiertos para inscripción"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "codigo": "IS-101",
                "nombre": "Introducción a la Programación",
                "facultad_nombre": "Facultad de Ingeniería",
                "tiene_grupos_disponibles": True
            }
        }
    )
