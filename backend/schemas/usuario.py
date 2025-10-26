"""
Schemas de Pydantic para Usuario
Define la forma de los datos que entran y salen de la API.
"""
from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr
from typing import Optional
from datetime import datetime

from models.usuario import EstadoUsuario


class UsuarioBase(BaseModel):
    """
    Schema base con los campos comunes de Usuario.
    Otros schemas heredan de este.
    """
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre(s) del usuario")
    apellido: str = Field(..., min_length=1, max_length=100, description="Apellido(s) del usuario")
    correo: EmailStr = Field(..., description="Correo electrónico único del usuario")
    
    @field_validator('nombre', 'apellido')
    @classmethod
    def validar_nombres(cls, v: str) -> str:
        """Valida que nombres y apellidos no contengan números"""
        if any(char.isdigit() for char in v):
            raise ValueError('El nombre y apellido no pueden contener números')
        return v.strip()


class UsuarioCreate(UsuarioBase):
    """
    Schema para crear un nuevo usuario.
    
    Usado en: POST /api/v1/usuarios
              POST /api/v1/auth/register
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Contraseña del usuario (mínimo 8 caracteres)"
    )
    rol_id: int = Field(..., gt=0, description="ID del rol asignado")
    avatar_url: Optional[str] = Field(None, max_length=255, description="URL del avatar")
    
    @field_validator('password')
    @classmethod
    def validar_password(cls, v: str) -> str:
        """Valida que la contraseña tenga una complejidad mínima"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(char.islower() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Juan",
                "apellido": "Pérez",
                "correo": "juan.perez@universidad.edu",
                "password": "Segura123",
                "rol_id": 3,
                "avatar_url": "https://ejemplo.com/avatar.jpg"
            }
        }
    )


class UsuarioUpdate(BaseModel):
    """
    Schema para actualizar un usuario existente.
    
    Usado en: PUT/PATCH /api/v1/usuarios/{id}
              PATCH /api/v1/usuarios/me
    """
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    correo: Optional[EmailStr] = None
    rol_id: Optional[int] = Field(None, gt=0)
    avatar_url: Optional[str] = Field(None, max_length=255)
    estado: Optional[EstadoUsuario] = Field(None, description="Cambiar estado del usuario")
    
    @field_validator('nombre', 'apellido')
    @classmethod
    def validar_nombres(cls, v: Optional[str]) -> Optional[str]:
        """Valida que nombres y apellidos no contengan números"""
        if v is None:
            return v
        if any(char.isdigit() for char in v):
            raise ValueError('El nombre y apellido no pueden contener números')
        return v.strip()
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nombre": "Juan Carlos",
                "avatar_url": "https://ejemplo.com/nuevo-avatar.jpg"
            }
        }
    )


class UsuarioPasswordUpdate(BaseModel):
    """
    Schema para cambiar la contraseña del usuario.
    
    Usado en: PATCH /api/v1/usuarios/me/password
              PATCH /api/v1/auth/cambiar-password
    
    Requiere la contraseña actual para mayor seguridad.
    """
    password_actual: str = Field(..., description="Contraseña actual del usuario")
    password_nueva: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Nueva contraseña (mínimo 8 caracteres)"
    )
    
    @field_validator('password_nueva')
    @classmethod
    def validar_password(cls, v: str) -> str:
        """Valida que la contraseña tenga una complejidad mínima"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(char.islower() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "password_actual": "MiPassword123",
                "password_nueva": "NuevaSegura456"
            }
        }
    )


class UsuarioEstadoUpdate(BaseModel):
    """
    Schema para cambiar solo el estado de un usuario.
    
    Usado en: PATCH /api/v1/usuarios/{id}/estado
    """
    estado: EstadoUsuario = Field(..., description="Nuevo estado del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estado": "Activo"
            }
        }
    )


class UsuarioInDB(UsuarioBase):
    """
    Schema que representa un usuario en la base de datos.
    
    Incluye todos los campos del modelo (excepto password_hash).
    """
    id: int
    rol_id: int
    avatar_url: Optional[str]
    estado: EstadoUsuario
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class UsuarioPublic(UsuarioInDB):
    """
    Schema público para devolver al cliente.
    
    Usado en: Respuestas de GET, POST, PUT, PATCH
    
    NUNCA incluye el password_hash.
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Juan",
                "apellido": "Pérez",
                "correo": "juan.perez@universidad.edu",
                "rol_id": 3,
                "avatar_url": "https://ejemplo.com/avatar.jpg",
                "estado": "Activo",
                "fecha_creacion": "2025-01-10T10:00:00Z",
                "ultimo_acceso": "2025-10-22T08:30:00Z"
            }
        }
    )


class UsuarioConRol(UsuarioPublic):
    """
    Schema extendido que incluye información del rol.
    
    Usado en: GET /api/v1/usuarios/{id}/detalles
    
    Incluye información del rol asociado.
    """
    rol_nombre: str = Field(..., description="Nombre del rol")
    rol_descripcion: Optional[str] = Field(None, description="Descripción del rol")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "nombre": "Juan",
                "apellido": "Pérez",
                "correo": "juan.perez@universidad.edu",
                "rol_id": 3,
                "avatar_url": "https://ejemplo.com/avatar.jpg",
                "estado": "Activo",
                "fecha_creacion": "2025-01-10T10:00:00Z",
                "ultimo_acceso": "2025-10-22T08:30:00Z",
                "rol_nombre": "Estudiante",
                "rol_descripcion": "Estudiante del sistema universitario"
            }
        }
    )


class UsuarioList(BaseModel):
    """
    Schema para listar usuarios con información resumida.
    
    Usado en: GET /api/v1/usuarios
              GET /api/v1/roles/{id}/usuarios
    """
    id: int
    nombre: str
    apellido: str
    correo: EmailStr
    rol_nombre: str
    estado: EstadoUsuario
    ultimo_acceso: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class UsuarioPerfil(UsuarioConRol):
    """
    Schema de perfil completo del usuario autenticado.
    
    Usado en: GET /api/v1/usuarios/me
    
    Vista completa del usuario con información de perfil específico.
    """
    # Información adicional según el rol
    perfil_profesor: Optional[dict] = Field(
        None,
        description="Datos del perfil de profesor si aplica"
    )
    perfil_estudiante: Optional[dict] = Field(
        None,
        description="Datos del perfil de estudiante si aplica"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 10,
                "nombre": "Juan",
                "apellido": "Pérez",
                "correo": "juan.perez@universidad.edu",
                "rol_id": 3,
                "avatar_url": "https://ejemplo.com/avatar.jpg",
                "estado": "Activo",
                "fecha_creacion": "2025-01-10T10:00:00Z",
                "ultimo_acceso": "2025-10-22T08:30:00Z",
                "rol_nombre": "Estudiante",
                "rol_descripcion": "Estudiante del sistema universitario",
                "perfil_estudiante": {
                    "codigo": "2024001",
                    "programa": "Ingeniería de Sistemas",
                    "semestre_actual": 5,
                    "promedio_acumulado": 4.1
                }
            }
        }
    )


class UsuarioLogin(BaseModel):
    """
    Schema para autenticación de usuario.
    
    Usado en: POST /api/v1/auth/login
    
    Credenciales para iniciar sesión.
    """
    correo: EmailStr = Field(..., description="Correo electrónico del usuario")
    password: str = Field(..., description="Contraseña del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "correo": "juan.perez@universidad.edu",
                "password": "MiPassword123"
            }
        }
    )


class UsuarioToken(BaseModel):
    """
    Schema para la respuesta de autenticación exitosa.
    
    Usado en: Respuesta de POST /api/v1/auth/login
    
    Incluye el token JWT y datos del usuario.
    """
    access_token: str = Field(..., description="Token JWT para autenticación")
    token_type: str = Field(default="bearer", description="Tipo de token")
    usuario: UsuarioConRol = Field(..., description="Datos del usuario autenticado")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "usuario": {
                    "id": 1,
                    "nombre": "Juan",
                    "apellido": "Pérez",
                    "correo": "juan.perez@universidad.edu",
                    "rol_nombre": "Estudiante"
                }
            }
        }
    )


class UsuarioRecuperarPassword(BaseModel):
    """
    Schema para solicitar recuperación de contraseña.
    
    Usado en: POST /api/v1/auth/recuperar-password
    """
    correo: EmailStr = Field(..., description="Correo del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "correo": "juan.perez@universidad.edu"
            }
        }
    )


class UsuarioResetPassword(BaseModel):
    """
    Schema para restablecer contraseña con token.
    
    Usado en: POST /api/v1/auth/reset-password
    """
    token: str = Field(..., description="Token de recuperación recibido por email")
    password_nueva: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Nueva contraseña"
    )
    
    @field_validator('password_nueva')
    @classmethod
    def validar_password(cls, v: str) -> str:
        """Valida que la contraseña tenga una complejidad mínima"""
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not any(char.isupper() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        if not any(char.islower() for char in v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        if not any(char.isdigit() for char in v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "abc123def456ghi789",
                "password_nueva": "NuevaSegura456"
            }
        }
    )

class UsuarioEstadisticas(BaseModel):
    """
    Schema para estadísticas generales de usuarios.
    
    Usado en: GET /api/v1/usuarios/estadisticas
    
    Dashboard de usuarios del sistema.
    """
    # Totales
    total_usuarios: int
    usuarios_activos: int
    usuarios_inactivos: int
    usuarios_pendientes: int
    
    # Por rol
    usuarios_por_rol: list[dict] = Field(
        ...,
        description="Distribución de usuarios por rol"
    )
    
    # Actividad
    usuarios_online_hoy: int = Field(
        ...,
        description="Usuarios que han accedido hoy"
    )
    usuarios_activos_semana: int = Field(
        ...,
        description="Usuarios activos en la última semana"
    )
    usuarios_activos_mes: int = Field(
        ...,
        description="Usuarios activos en el último mes"
    )
    
    # Crecimiento
    nuevos_usuarios_mes: int
    nuevos_usuarios_anio: int
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_usuarios": 1350,
                "usuarios_activos": 1280,
                "usuarios_inactivos": 55,
                "usuarios_pendientes": 15,
                "usuarios_por_rol": [
                    {"rol": "Estudiante", "cantidad": 1200},
                    {"rol": "Profesor", "cantidad": 45},
                    {"rol": "Coordinador", "cantidad": 8},
                    {"rol": "Superadmin", "cantidad": 2}
                ],
                "usuarios_online_hoy": 450,
                "usuarios_activos_semana": 980,
                "usuarios_activos_mes": 1150,
                "nuevos_usuarios_mes": 52,
                "nuevos_usuarios_anio": 380
            }
        }
    )


class UsuarioActividadReciente(BaseModel):
    """
    Schema para mostrar actividad reciente de un usuario.
    
    Usado en: GET /api/v1/usuarios/{id}/actividad-reciente
    """
    usuario_id: int
    usuario_nombre: str
    actividades: list[dict] = Field(
        ...,
        description="Lista de actividades recientes"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "usuario_id": 10,
                "usuario_nombre": "Juan Pérez",
                "actividades": [
                    {
                        "tipo": "login",
                        "descripcion": "Inicio de sesión",
                        "fecha": "2025-10-22T08:30:00Z"
                    },
                    {
                        "tipo": "entrega",
                        "descripcion": "Entregó tarea: Programación Orientada a Objetos",
                        "fecha": "2025-10-21T18:45:00Z"
                    },
                    {
                        "tipo": "inscripcion",
                        "descripcion": "Se inscribió en: Bases de Datos",
                        "fecha": "2025-10-15T10:20:00Z"
                    }
                ]
            }
        }
    )


class UsuarioFiltros(BaseModel):
    """
    Schema para filtrar usuarios en consultas.
    
    Usado en: GET /api/v1/usuarios?filters
    """
    rol_id: Optional[int] = Field(None, gt=0, description="Filtrar por rol")
    estado: Optional[EstadoUsuario] = Field(None, description="Filtrar por estado")
    busqueda: Optional[str] = Field(
        None,
        description="Búsqueda por nombre, apellido o correo"
    )
    fecha_desde: Optional[datetime] = Field(
        None,
        description="Usuarios creados desde esta fecha"
    )
    fecha_hasta: Optional[datetime] = Field(
        None,
        description="Usuarios creados hasta esta fecha"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rol_id": 3,
                "estado": "Activo",
                "busqueda": "pérez"
            }
        }
    )
