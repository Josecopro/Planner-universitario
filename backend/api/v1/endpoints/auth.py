"""
Endpoints de Autenticación y Autorización.

Este módulo maneja todas las operaciones de autenticación,
incluyendo login, logout, cambio de contraseña, verificación de tokens
y gestión de sesiones de usuario.
"""
from datetime import timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import (
    verify_password,
    create_access_token,
    get_current_user,
    get_current_active_user,
    hash_password,
    record_login_attempt,
    is_account_locked,
    get_remaining_attempts,
    clear_login_attempts,
    sanitize_email,
    decode_access_token
)
from core.config import settings
from services.usuario_service import (
    obtener_usuario_por_email,
    actualizar_ultimo_acceso,
    cambiar_password,
    obtener_usuario_por_id
)
from models.usuario import EstadoUsuario
from schemas.token import (
    LoginRequest,
    LoginResponse,
    Token,
    PasswordChangeRequest,
    MessageResponse,
    TokenVerifyResponse
)
from schemas.usuario import UsuarioPublic

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """
    Autenticar usuario y obtener token JWT.
    
    Implementa:
    - Verificación de credenciales
    - Rate limiting (máximo 5 intentos en 15 minutos)
    - Verificación de estado del usuario
    - Actualización de último acceso
    - Generación de token JWT
    
    Args:
        login_data: Credenciales del usuario (email y password)
        request: Request de FastAPI para obtener IP
        db: Sesión de base de datos
        
    Returns:
        Token JWT y datos del usuario autenticado
        
    Raises:
        HTTPException 401: Credenciales inválidas
        HTTPException 403: Usuario inactivo o cuenta bloqueada
        HTTPException 429: Demasiados intentos de login
    """
    email = sanitize_email(login_data.email)
    
    if is_account_locked(email):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Cuenta bloqueada temporalmente. Intente nuevamente en {settings.LOCKOUT_DURATION_MINUTES} minutos."
        )
    
    usuario = obtener_usuario_por_email(db, email)
    
    if not usuario or not verify_password(login_data.password, str(usuario.password_hash)):
        record_login_attempt(email)
        intentos_restantes = get_remaining_attempts(email)
        
        if intentos_restantes > 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Email o contraseña incorrectos. {intentos_restantes} intentos restantes.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Cuenta bloqueada por demasiados intentos. Intente en {settings.LOCKOUT_DURATION_MINUTES} minutos."
            )
    
    if usuario.estado == EstadoUsuario.INACTIVO:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador del sistema."
        )
    
    if usuario.estado == EstadoUsuario.PENDIENTE_DE_VERIFICACION:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email pendiente de verificación. Revise su correo electrónico."
        )
    
    clear_login_attempts(email)
    
    actualizar_ultimo_acceso(db, usuario.id)  # type: ignore
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": usuario.id,
            "email": usuario.correo,  # type: ignore
            "rol": usuario.rol.nombre  # type: ignore
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # en segundos
        "usuario": {
            "id": usuario.id,
            "email": usuario.correo,  # type: ignore
            "nombre": usuario.nombre,
            "apellido": usuario.apellido,
            "rol": usuario.rol.nombre,  # type: ignore
            "estado": usuario.estado  # type: ignore
        }
    }


@router.get("/me", response_model=UsuarioPublic)
def obtener_usuario_actual(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener información del usuario autenticado.
    
    Args:
        current_user: Usuario actual (inyectado por dependency)
        db: Sesión de base de datos
        
    Returns:
        Información completa del usuario autenticado
        
    Raises:
        HTTPException 401: Token inválido o expirado
    """
    # Actualizar último acceso
    actualizar_ultimo_acceso(db, current_user.id)  # type: ignore
    return current_user


@router.post("/change-password", response_model=MessageResponse)
def cambiar_password_usuario(
    password_data: PasswordChangeRequest,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Cambiar contraseña del usuario autenticado.
    
    Requiere la contraseña actual para mayor seguridad.
    
    Args:
        password_data: Contraseña actual y nueva
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Mensaje de éxito
        
    Raises:
        HTTPException 400: Contraseña actual incorrecta
        HTTPException 401: Token inválido
    """
    try:
        cambiado = cambiar_password(
            db,
            current_user.id,  # type: ignore
            password_data.current_password,
            password_data.new_password
        )
        
        if not cambiado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        
        return {"message": "Contraseña actualizada exitosamente. Por seguridad, inicie sesión nuevamente."}
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/verify-token", response_model=TokenVerifyResponse)
def verificar_token(
    token: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verificar si un token JWT es válido.
    
    Útil para el frontend para validar tokens antes de hacer requests.
    
    Args:
        token: Token JWT a verificar
        db: Sesión de base de datos
        
    Returns:
        Información sobre la validez del token y datos del usuario
    """
    try:
        token_data = decode_access_token(token)
        
        if token_data.usuario_id is None:
            return {
                "valid": False,
                "usuario_id": None,
                "email": None,
                "rol": None,
                "expires_in": None
            }
        
        usuario = obtener_usuario_por_id(db, token_data.usuario_id)
        
        if not usuario or usuario.estado != EstadoUsuario.ACTIVO:  # type: ignore
            return {
                "valid": False,
                "usuario_id": None,
                "email": None,
                "rol": None,
                "expires_in": None
            }
        
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        return {
            "valid": True,
            "usuario_id": token_data.usuario_id,
            "email": token_data.email,
            "rol": token_data.rol,
            "expires_in": expires_in
        }
    
    except HTTPException:
        return {
            "valid": False,
            "usuario_id": None,
            "email": None,
            "rol": None,
            "expires_in": None
        }


@router.post("/logout", response_model=MessageResponse)
def logout(
    current_user = Depends(get_current_user)
) -> Any:
    """
    Cerrar sesión del usuario.
    
    Nota: Con JWT no hay un "logout" real en el servidor ya que los tokens
    son stateless. El cliente debe eliminar el token de su almacenamiento.
    Este endpoint está aquí por conveniencia y para registrar el evento.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Mensaje de confirmación
    """
    
    return {
        "message": "Sesión cerrada exitosamente. Elimine el token del cliente."
    }


@router.get("/check-permissions", response_model=Dict[str, Any])
def verificar_permisos(
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Verificar permisos del usuario actual.
    
    Retorna un objeto con los permisos específicos del usuario
    basándose en su rol.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Diccionario con permisos del usuario
    """
    rol_nombre = current_user.rol.nombre  # type: ignore
    
    permisos = {
        "Superadmin": {
            "puede_eliminar_usuarios": True,
            "puede_eliminar_roles": True,
            "puede_eliminar_facultades": True,
            "puede_eliminar_programas": True,
            "puede_eliminar_grupos": True,
            "puede_eliminar_horarios": True,
            "puede_gestionar_todo": True,
            "puede_ver_estadisticas": True,
            "puede_crear_usuarios": True,
            "puede_modificar_roles": True
        },
        "Profesor": {
            "puede_eliminar_usuarios": False,
            "puede_eliminar_roles": False,
            "puede_eliminar_facultades": False,
            "puede_eliminar_programas": False,
            "puede_eliminar_grupos": False,
            "puede_eliminar_horarios": False,
            "puede_gestionar_todo": False,
            "puede_ver_estadisticas": False,
            "puede_crear_usuarios": False,
            "puede_modificar_roles": False,
            "puede_gestionar_grupos": True,
            "puede_calificar": True,
            "puede_tomar_asistencia": True,
            "puede_crear_actividades": True,
            "puede_ver_estudiantes": True
        },
        "Estudiante": {
            "puede_eliminar_usuarios": False,
            "puede_eliminar_roles": False,
            "puede_eliminar_facultades": False,
            "puede_eliminar_programas": False,
            "puede_eliminar_grupos": False,
            "puede_eliminar_horarios": False,
            "puede_gestionar_todo": False,
            "puede_ver_estadisticas": False,
            "puede_crear_usuarios": False,
            "puede_modificar_roles": False,
            "puede_gestionar_grupos": False,
            "puede_calificar": False,
            "puede_tomar_asistencia": False,
            "puede_crear_actividades": False,
            "puede_ver_estudiantes": False,
            "puede_inscribirse": True,
            "puede_ver_calificaciones": True,
            "puede_entregar_actividades": True,
            "puede_ver_horarios": True
        }
    }
    
    permisos_usuario = permisos.get(rol_nombre, {})
    
    return {
        "usuario_id": current_user.id,
        "rol": rol_nombre,
        "permisos": permisos_usuario
    }


@router.get("/session-info", response_model=Dict[str, Any])
def informacion_sesion(
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtener información completa de la sesión actual.
    
    Incluye datos del usuario, rol, permisos y estadísticas de sesión.
    
    Args:
        current_user: Usuario autenticado
        db: Sesión de base de datos
        
    Returns:
        Información completa de la sesión
    """
    rol_nombre = current_user.rol.nombre  # type: ignore
    
    perfil_especifico = None
    
    if rol_nombre == "Profesor" and hasattr(current_user, 'profesor') and current_user.profesor:
        perfil_especifico = {
            "tipo": "profesor",
            "departamento": current_user.profesor.departamento,  # type: ignore
            "especialidad": current_user.profesor.especialidad,  # type: ignore
            "oficina": current_user.profesor.oficina  # type: ignore
        }
    elif rol_nombre == "Estudiante" and hasattr(current_user, 'estudiante') and current_user.estudiante:
        perfil_especifico = {
            "tipo": "estudiante",
            "codigo": current_user.estudiante.codigo,  # type: ignore
            "semestre_actual": current_user.estudiante.semestre_actual,  # type: ignore
            "programa_id": current_user.estudiante.programa_id  # type: ignore
        }
    
    return {
        "usuario": {
            "id": current_user.id,
            "email": current_user.correo,  # type: ignore
            "nombre": current_user.nombre,
            "apellido": current_user.apellido,
            "estado": current_user.estado,  # type: ignore
            "ultimo_acceso": current_user.ultimo_acceso  # type: ignore
        },
        "rol": {
            "nombre": rol_nombre,
            "descripcion": current_user.rol.descripcion  # type: ignore
        },
        "perfil_especifico": perfil_especifico,
        "token_info": {
            "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "token_type": "bearer"
        }
    }
