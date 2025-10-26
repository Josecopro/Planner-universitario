"""
Schemas de Pydantic para Rol
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional


class RolBase(BaseModel):
    """
    Schema base con los campos comunes de Rol.
    Otros schemas heredan de este.
    """
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Nombre único del rol, ej: Superadmin, Profesor, Estudiante"
    )
    descripcion: Optional[str] = Field(
        None,
        description="Descripción detallada de los permisos y funciones del rol"
    )
    
    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: str) -> str:
        """Valida que el nombre del rol esté capitalizado correctamente"""
        if not v[0].isupper():
            raise ValueError('El nombre del rol debe comenzar con mayúscula')
        return v


class RolCreate(RolBase):
    """
    Schema para crear un nuevo rol.
    
    Usado en: POST /api/v1/roles
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Coordinador",
                "descripcion": "Coordinador de programa académico con permisos para gestionar grupos y cursos"
            }
        }
    )


class RolUpdate(BaseModel):
    """
    Schema para actualizar un rol existente.
    
    Usado en: PUT/PATCH /api/v1/roles/{id}
    """
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion: Optional[str] = None
    
    @field_validator('nombre')
    @classmethod
    def validar_nombre(cls, v: Optional[str]) -> Optional[str]:
        """Valida que el nombre del rol esté capitalizado correctamente"""
        if v is None:
            return v
        if not v[0].isupper():
            raise ValueError('El nombre del rol debe comenzar con mayúscula')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "descripcion": "Coordinador de programa académico con permisos ampliados para gestionar grupos, cursos y estudiantes"
            }
        }
    )


class RolInDB(RolBase):
    """
    Schema que representa un rol en la base de datos.
    
    Incluye todos los campos del modelo.
    """
    id: int
    
    model_config = ConfigDict(from_attributes=True)


class RolPublic(RolInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Superadmin",
                "descripcion": "Administrador del sistema con acceso total a todas las funcionalidades"
            }
        }
    )


class RolList(BaseModel):
    """
    Schema para listar roles con información resumida.
    
    Usado en: GET /api/v1/roles
    """
    id: int
    nombre: str
    descripcion: Optional[str]
    total_usuarios: int = Field(..., description="Cantidad de usuarios con este rol")
    
    model_config = ConfigDict(from_attributes=True)


class RolConContadores(RolPublic):
    """
    Schema que incluye contadores de usuarios por estado.
    
    Usado en: GET /api/v1/roles/{id}/contadores
    
    Vista con información cuantitativa.
    """
    total_usuarios: int = Field(..., description="Total de usuarios con este rol")
    usuarios_activos: int = Field(..., description="Usuarios activos")
    usuarios_inactivos: int = Field(..., description="Usuarios inactivos")
    usuarios_suspendidos: int = Field(..., description="Usuarios suspendidos")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "nombre": "Profesor",
                "descripcion": "Docente con permisos para gestionar sus grupos, actividades y calificaciones",
                "total_usuarios": 45,
                "usuarios_activos": 42,
                "usuarios_inactivos": 2,
                "usuarios_suspendidos": 1
            }
        }
    )


class RolConUsuarios(RolPublic):
    """
    Schema que incluye la lista de usuarios con el rol.
    
    Usado en: GET /api/v1/roles/{id}/usuarios
    
    Vista con usuarios asociados.
    """
    usuarios: list[dict] = Field(
        ...,
        description="Lista de usuarios con este rol"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "nombre": "Profesor",
                "descripcion": "Docente con permisos para gestionar sus grupos, actividades y calificaciones",
                "usuarios": [
                    {
                        "usuario_id": 5,
                        "nombre": "Carlos",
                        "apellido": "Gómez",
                        "email": "carlos.gomez@universidad.edu",
                        "estado": "Activo"
                    },
                    {
                        "usuario_id": 8,
                        "nombre": "Ana",
                        "apellido": "Torres",
                        "email": "ana.torres@universidad.edu",
                        "estado": "Activo"
                    }
                ]
            }
        }
    )


class RolPermisos(BaseModel):
    """
    Schema que describe los permisos asociados a un rol.
    
    Usado en: GET /api/v1/roles/{id}/permisos
    
    Detalla las acciones permitidas para el rol.
    """
    rol_id: int
    rol_nombre: str
    permisos: dict = Field(
        ...,
        description="Diccionario de permisos organizados por módulo"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rol_id": 2,
                "rol_nombre": "Profesor",
                "permisos": {
                    "grupos": {
                        "ver": True,
                        "ver_propios": True,
                        "crear": False,
                        "editar_propios": True,
                        "eliminar": False
                    },
                    "actividades": {
                        "ver": True,
                        "crear": True,
                        "editar": True,
                        "eliminar": True,
                        "calificar": True
                    },
                    "estudiantes": {
                        "ver_en_grupos_propios": True,
                        "ver_todos": False,
                        "editar": False,
                        "eliminar": False
                    },
                    "calificaciones": {
                        "ver_en_grupos_propios": True,
                        "modificar_en_grupos_propios": True,
                        "ver_todas": False
                    },
                    "asistencia": {
                        "tomar_en_grupos_propios": True,
                        "editar_en_grupos_propios": True,
                        "ver_reportes": True
                    }
                }
            }
        }
    )


class RolEstadisticas(BaseModel):
    """
    Schema para estadísticas de un rol.
    
    Usado en: GET /api/v1/roles/{id}/estadisticas
    
    Dashboard con información del rol.
    """
    rol_id: int
    rol_nombre: str
    
    # Contadores de usuarios
    total_usuarios: int
    usuarios_activos: int
    usuarios_inactivos: int
    usuarios_suspendidos: int
    usuarios_eliminados: int
    
    # Actividad
    usuarios_con_login_reciente: int = Field(
        ...,
        description="Usuarios que han iniciado sesión en los últimos 30 días"
    )
    porcentaje_actividad: float = Field(
        ...,
        description="Porcentaje de usuarios activos con login reciente"
    )
    
    # Crecimiento
    usuarios_nuevos_mes: int = Field(
        ...,
        description="Usuarios creados en el último mes"
    )
    usuarios_nuevos_anio: int = Field(
        ...,
        description="Usuarios creados en el último año"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rol_id": 3,
                "rol_nombre": "Estudiante",
                "total_usuarios": 1250,
                "usuarios_activos": 1180,
                "usuarios_inactivos": 50,
                "usuarios_suspendidos": 15,
                "usuarios_eliminados": 5,
                "usuarios_con_login_reciente": 1050,
                "porcentaje_actividad": 88.98,
                "usuarios_nuevos_mes": 52,
                "usuarios_nuevos_anio": 320
            }
        }
    )


class RolCatalogo(BaseModel):
    """
    Schema simplificado para catálogos y selectores.
    
    Usado en: GET /api/v1/roles/catalogo
    """
    id: int
    nombre: str
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 2,
                "nombre": "Profesor"
            }
        }
    )


class RolJerarquia(BaseModel):
    """
    Schema que define la jerarquía de roles en el sistema.
    
    Usado en: GET /api/v1/roles/jerarquia
    """
    roles: list[dict] = Field(
        ...,
        description="Roles ordenados por nivel de autoridad (mayor a menor)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "roles": [
                    {
                        "nivel": 1,
                        "id": 1,
                        "nombre": "Superadmin",
                        "descripcion": "Acceso total al sistema",
                        "puede_gestionar": ["Todos los roles"]
                    },
                    {
                        "nivel": 2,
                        "id": 4,
                        "nombre": "Coordinador",
                        "descripcion": "Coordinador de programa académico",
                        "puede_gestionar": ["Profesor", "Estudiante"]
                    },
                    {
                        "nivel": 3,
                        "id": 2,
                        "nombre": "Profesor",
                        "descripcion": "Docente del sistema",
                        "puede_gestionar": []
                    },
                    {
                        "nivel": 4,
                        "id": 3,
                        "nombre": "Estudiante",
                        "descripcion": "Estudiante del sistema",
                        "puede_gestionar": []
                    }
                ]
            }
        }
    )


class RolValidacion(BaseModel):
    """
    Schema para validar si un nombre de rol está disponible.
    
    Usado en: POST /api/v1/roles/validar-nombre
    """
    nombre_disponible: bool = Field(
        ...,
        description="Indica si el nombre está disponible"
    )
    mensaje: str = Field(
        ...,
        description="Mensaje descriptivo del resultado"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre_disponible": False,
                "mensaje": "El nombre 'Profesor' ya está en uso"
            }
        }
    )
