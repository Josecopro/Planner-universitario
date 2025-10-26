"""
Schemas de Pydantic para Autenticación y Tokens JWT.

Define la forma de los datos relacionados con autenticación,
tokens JWT y operaciones de seguridad.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """
    Schema para la respuesta de autenticación con JWT.
    
    Usado en: POST /api/v1/auth/login
    
    Attributes:
        access_token: Token JWT de acceso
        token_type: Tipo de token (siempre "bearer")
        expires_in: Segundos hasta que expire el token
    """
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Segundos hasta la expiración del token")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImVtYWlsIjoianVhbi5wZXJlekB1bml2ZXJzaWRhZC5lZHUiLCJyb2wiOiJQcm9mZXNvciIsImV4cCI6MTYzMDQ0MDAwMH0.xyz",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }
    )


class TokenData(BaseModel):
    """
    Schema para los datos contenidos en el payload del JWT.
    
    Representa la información decodificada del token.
    
    Attributes:
        usuario_id: ID del usuario autenticado
        email: Email del usuario
        rol: Nombre del rol del usuario
        exp: Timestamp de expiración del token
    """
    usuario_id: Optional[int] = Field(None, description="ID del usuario")
    email: Optional[str] = Field(None, description="Email del usuario")
    rol: Optional[str] = Field(None, description="Rol del usuario")
    exp: Optional[datetime] = Field(None, description="Fecha de expiración")
    
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """
    Schema para la solicitud de inicio de sesión.
    
    Usado en: POST /api/v1/auth/login
    
    Attributes:
        email: Email del usuario
        password: Contraseña en texto plano
    """
    email: EmailStr = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=1, description="Contraseña del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "juan.perez@universidad.edu",
                "password": "MiPassword123"
            }
        }
    )


class LoginResponse(BaseModel):
    """
    Schema para la respuesta exitosa de inicio de sesión.
    
    Usado en: POST /api/v1/auth/login (respuesta completa)
    
    Incluye el token JWT y los datos básicos del usuario autenticado.
    
    Attributes:
        access_token: Token JWT de acceso
        token_type: Tipo de token (bearer)
        expires_in: Segundos hasta expiración
        usuario: Información básica del usuario autenticado
    """
    access_token: str = Field(..., description="Token JWT de acceso")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Segundos hasta expiración")
    usuario: dict = Field(..., description="Datos del usuario autenticado")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "usuario": {
                    "id": 1,
                    "email": "juan.perez@universidad.edu",
                    "nombre": "Juan",
                    "apellido": "Pérez",
                    "rol": "Profesor",
                    "estado": "Activo"
                }
            }
        }
    )


class RefreshTokenRequest(BaseModel):
    """
    Schema para solicitar un nuevo token usando refresh token.
    
    Usado en: POST /api/v1/auth/refresh
    
    Attributes:
        refresh_token: Token de refresco previamente emitido
    """
    refresh_token: str = Field(..., description="Token de refresco")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }
    )


class PasswordChangeRequest(BaseModel):
    """
    Schema para cambio de contraseña de usuario autenticado.
    
    Usado en: POST /api/v1/auth/change-password
              PATCH /api/v1/usuarios/me/password
    
    Requiere la contraseña actual para mayor seguridad.
    
    Attributes:
        current_password: Contraseña actual del usuario
        new_password: Nueva contraseña
    """
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Nueva contraseña (mínimo 8 caracteres)"
    )
    
    @field_validator('new_password')
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
                "current_password": "MiPassword123",
                "new_password": "NuevaSegura456"
            }
        }
    )


class PasswordResetRequest(BaseModel):
    """
    Schema para solicitar el reseteo de contraseña (recuperación).
    
    Usado en: POST /api/v1/auth/password-reset-request
    
    Se envía un token de reseteo al email del usuario.
    
    Attributes:
        email: Email del usuario que solicita recuperación
    """
    email: EmailStr = Field(..., description="Email del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "juan.perez@universidad.edu"
            }
        }
    )


class PasswordResetConfirm(BaseModel):
    """
    Schema para confirmar el reseteo de contraseña con token.
    
    Usado en: POST /api/v1/auth/password-reset-confirm
    
    El token se envía por email al usuario tras solicitar recuperación.
    
    Attributes:
        token: Token de reseteo enviado por email
        new_password: Nueva contraseña
    """
    token: str = Field(..., description="Token de reseteo recibido por email")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Nueva contraseña (mínimo 8 caracteres)"
    )
    
    @field_validator('new_password')
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
                "token": "abc123xyz789",
                "new_password": "NuevaSegura456"
            }
        }
    )


class EmailVerificationRequest(BaseModel):
    """
    Schema para solicitar reenvío de email de verificación.
    
    Usado en: POST /api/v1/auth/resend-verification
    
    Attributes:
        email: Email del usuario
    """
    email: EmailStr = Field(..., description="Email del usuario")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "juan.perez@universidad.edu"
            }
        }
    )


class EmailVerificationConfirm(BaseModel):
    """
    Schema para confirmar verificación de email con token.
    
    Usado en: POST /api/v1/auth/verify-email
    
    Attributes:
        token: Token de verificación enviado por email
    """
    token: str = Field(..., description="Token de verificación")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "abc123xyz789"
            }
        }
    )


class TokenVerifyResponse(BaseModel):
    """
    Schema para la respuesta de verificación de token.
    
    Usado en: POST /api/v1/auth/verify-token
    
    Attributes:
        valid: Indica si el token es válido
        usuario_id: ID del usuario (si el token es válido)
        email: Email del usuario (si el token es válido)
        rol: Rol del usuario (si el token es válido)
        expires_in: Segundos restantes hasta expiración
    """
    valid: bool = Field(..., description="Indica si el token es válido")
    usuario_id: Optional[int] = Field(None, description="ID del usuario")
    email: Optional[str] = Field(None, description="Email del usuario")
    rol: Optional[str] = Field(None, description="Rol del usuario")
    expires_in: Optional[int] = Field(None, description="Segundos hasta expiración")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "valid": True,
                "usuario_id": 1,
                "email": "juan.perez@universidad.edu",
                "rol": "Profesor",
                "expires_in": 82800
            }
        }
    )


class MessageResponse(BaseModel):
    """
    Schema para respuestas simples con un mensaje.
    
    Usado en diversos endpoints de autenticación.
    
    Attributes:
        message: Mensaje de respuesta
    """
    message: str = Field(..., description="Mensaje de respuesta")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Operación realizada exitosamente"
            }
        }
    )
