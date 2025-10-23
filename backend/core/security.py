"""
Módulo de Seguridad
Funciones críticas para autenticación, autorización y manejo de contraseñas.
"""
from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings


# Contexto de hashing usando bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Genera un hash seguro de la contraseña usando bcrypt.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash de la contraseña
        
    Example:
        >>> hashed = hash_password("MiPassword123")
        >>> print(hashed)
        $2b$12$...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña en texto plano coincide con un hash.
    
    Args:
        plain_password: Contraseña en texto plano a verificar
        hashed_password: Hash almacenado en la base de datos
        
    Returns:
        True si la contraseña es correcta, False en caso contrario
        
    Example:
        >>> hashed = hash_password("MiPassword123")
        >>> verify_password("MiPassword123", hashed)
        True
        >>> verify_password("OtraPassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de acceso.
    
    Args:
        data: Diccionario con los datos a codificar en el token (ej: {"sub": "user@email.com"})
        expires_delta: Tiempo de expiración del token (opcional)
        
    Returns:
        Token JWT codificado
        
    Example:
        >>> token = create_access_token({"sub": "juan@email.com", "rol": "Estudiante"})
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un token JWT de actualización (refresh token).
    
    Args:
        data: Diccionario con los datos a codificar
        expires_delta: Tiempo de expiración (opcional)
        
    Returns:
        Refresh token JWT codificado
        
    Example:
        >>> refresh = create_refresh_token({"sub": "juan@email.com"})
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """
    Decodifica y valida un token JWT.
    
    Args:
        token: Token JWT a decodificar
        
    Returns:
        Payload del token si es válido, None si es inválido o expirado
        
    Example:
        >>> token = create_access_token({"sub": "juan@email.com"})
        >>> payload = decode_token(token)
        >>> print(payload["sub"])
        juan@email.com
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_password_reset_token(email: str) -> str:
    """
    Crea un token temporal para resetear contraseña.
    
    Args:
        email: Email del usuario que solicitó el reset
        
    Returns:
        Token JWT para reset de contraseña
        
    Example:
        >>> token = create_password_reset_token("juan@email.com")
        >>> # Enviar este token por email al usuario
    """
    delta = timedelta(minutes=30)
    data = {
        "sub": email,
        "type": "password_reset"
    }
    return create_access_token(data, expires_delta=delta)


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verifica un token de reset de contraseña y retorna el email.
    
    Args:
        token: Token de reset recibido
        
    Returns:
        Email del usuario si el token es válido, None en caso contrario
        
    Example:
        >>> token = create_password_reset_token("juan@email.com")
        >>> email = verify_password_reset_token(token)
        >>> print(email)
        juan@email.com
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    if payload.get("type") != "password_reset":
        return None
    
    return payload.get("sub")


def create_verification_token(email: str) -> str:
    """
    Crea un token para verificación de email.
    
    Se usa cuando un usuario se registra y necesita verificar su email.
    
    Args:
        email: Email a verificar
        
    Returns:
        Token JWT para verificación de email
        
    Example:
        >>> token = create_verification_token("nuevo@email.com")
        >>> # Enviar este token en un link de verificación
    """
    delta = timedelta(hours=24)
    data = {
        "sub": email,
        "type": "email_verification"
    }
    return create_access_token(data, expires_delta=delta)


def verify_email_token(token: str) -> Optional[str]:
    """
    Verifica un token de verificación de email.
    
    Args:
        token: Token de verificación recibido
        
    Returns:
        Email si el token es válido, None en caso contrario
        
    Example:
        >>> token = create_verification_token("nuevo@email.com")
        >>> email = verify_email_token(token)
        >>> # Activar la cuenta del usuario con este email
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    if payload.get("type") != "email_verification":
        return None
    
    return payload.get("sub")


def is_token_expired(token: str) -> bool:
    """
    Verifica si un token ha expirado.
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        True si el token expiró, False si aún es válido
        
    Example:
        >>> token = create_access_token({"sub": "user@email.com"})
        >>> is_token_expired(token)
        False
    """
    payload = decode_token(token)
    
    if payload is None:
        return True
    
    exp = payload.get("exp")
    if exp is None:
        return True
    
    now = datetime.utcnow().timestamp()
    return now > exp


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Obtiene la fecha de expiración de un token.
    
    Args:
        token: Token JWT
        
    Returns:
        Fecha de expiración o None si el token es inválido
        
    Example:
        >>> token = create_access_token({"sub": "user@email.com"})
        >>> exp = get_token_expiration(token)
        >>> print(exp)
        2025-10-22 10:30:00
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    exp = payload.get("exp")
    if exp is None:
        return None
    
    return datetime.fromtimestamp(exp)


def check_permission(user_rol: str, required_roles: list[str]) -> bool:
    """
    Verifica si un usuario tiene los permisos necesarios.
    
    Args:
        user_rol: Rol del usuario actual
        required_roles: Lista de roles permitidos para la acción
        
    Returns:
        True si el usuario tiene permiso, False en caso contrario
        
    Example:
        >>> check_permission("Superadmin", ["Superadmin", "Coordinador"])
        True
        >>> check_permission("Estudiante", ["Profesor"])
        False
    """
    return user_rol in required_roles


def check_is_superadmin(user_rol: str) -> bool:
    """
    Verifica si el usuario es Superadmin.
    
    Args:
        user_rol: Rol del usuario
        
    Returns:
        True si es Superadmin
        
    Example:
        >>> check_is_superadmin("Superadmin")
        True
    """
    return user_rol == "Superadmin"


def check_is_profesor(user_rol: str) -> bool:
    """
    Verifica si el usuario es Profesor.
    
    Args:
        user_rol: Rol del usuario
        
    Returns:
        True si es Profesor
    """
    return user_rol == "Profesor"


def check_is_estudiante(user_rol: str) -> bool:
    """
    Verifica si el usuario es Estudiante.
    
    Args:
        user_rol: Rol del usuario
        
    Returns:
        True si es Estudiante
    """
    return user_rol == "Estudiante"


def generate_secure_random_token(length: int = 32) -> str:
    """
    Genera un token aleatorio seguro.
    
    Útil para tokens de verificación, reset de password, etc.
    
    Args:
        length: Longitud del token (por defecto 32 caracteres)
        
    Returns:
        Token aleatorio en hexadecimal
        
    Example:
        >>> token = generate_secure_random_token()
        >>> print(len(token))
        64  # 32 bytes = 64 caracteres hex
    """
    import secrets
    return secrets.token_hex(length)


def sanitize_email(email: str) -> str:
    """
    Sanitiza y normaliza una dirección de email.
    
    Args:
        email: Email a sanitizar
        
    Returns:
        Email en minúsculas y sin espacios
        
    Example:
        >>> sanitize_email("  Juan.Perez@UNIVERSIDAD.edu  ")
        'juan.perez@universidad.edu'
    """
    return email.strip().lower()


def mask_email(email: str) -> str:
    """
    Enmascara parcialmente un email para mostrar en logs o UI.
    
    Args:
        email: Email a enmascarar
        
    Returns:
        Email parcialmente oculto
        
    Example:
        >>> mask_email("juan.perez@universidad.edu")
        'j***z@universidad.edu'
    """
    if "@" not in email:
        return email
    
    local, domain = email.split("@", 1)
    
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "***" + local[-1]
    
    return f"{masked_local}@{domain}"


def validate_password_strength(password: str) -> dict[str, Any]:
    """
    Valida la fortaleza de una contraseña.
    
    Args:
        password: Contraseña a validar
        
    Returns:
        Diccionario con resultado de validación y mensaje
        
    Example:
        >>> result = validate_password_strength("abc")
        >>> print(result)
        {'is_valid': False, 'message': 'La contraseña debe tener al menos 8 caracteres'}
    """
    # Longitud mínima
    if len(password) < 8:
        return {
            "is_valid": False,
            "message": "La contraseña debe tener al menos 8 caracteres",
            "score": 0
        }
    
    has_upper = any(c.isupper() for c in password)
    if not has_upper:
        return {
            "is_valid": False,
            "message": "La contraseña debe contener al menos una letra mayúscula",
            "score": 1
        }
    
    has_lower = any(c.islower() for c in password)
    if not has_lower:
        return {
            "is_valid": False,
            "message": "La contraseña debe contener al menos una letra minúscula",
            "score": 2
        }
    
    has_digit = any(c.isdigit() for c in password)
    if not has_digit:
        return {
            "is_valid": False,
            "message": "La contraseña debe contener al menos un número",
            "score": 3
        }
    
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    score = 4
    if has_special:
        score = 5
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1
    
    strength_levels = {
        4: "Aceptable",
        5: "Buena",
        6: "Fuerte",
        7: "Muy Fuerte"
    }
    
    return {
        "is_valid": True,
        "message": f"Contraseña {strength_levels.get(score, 'Aceptable')}",
        "score": score,
        "strength": strength_levels.get(score, "Aceptable"),
        "recommendations": [
            "Considera usar caracteres especiales" if not has_special else None,
            "Considera usar una contraseña más larga" if len(password) < 12 else None
        ]
    }


_login_attempts: dict[str, list[datetime]] = {}
_max_attempts = 5
_lockout_duration = timedelta(minutes=15)


def record_login_attempt(identifier: str) -> None:
    """
    Registra un intento de login.
    
    Args:
        identifier: Email o IP del usuario
    """
    now = datetime.utcnow()
    
    if identifier not in _login_attempts:
        _login_attempts[identifier] = []
    
    _login_attempts[identifier].append(now)
    
    cutoff = now - _lockout_duration
    _login_attempts[identifier] = [
        attempt for attempt in _login_attempts[identifier]
        if attempt > cutoff
    ]


def is_account_locked(identifier: str) -> bool:
    """
    Verifica si una cuenta está bloqueada por demasiados intentos.
    
    Args:
        identifier: Email o IP del usuario
        
    Returns:
        True si está bloqueada
    """
    if identifier not in _login_attempts:
        return False
    
    # Limpiar intentos antiguos
    now = datetime.utcnow()
    cutoff = now - _lockout_duration
    _login_attempts[identifier] = [
        attempt for attempt in _login_attempts[identifier]
        if attempt > cutoff
    ]
    
    return len(_login_attempts[identifier]) >= _max_attempts


def get_remaining_attempts(identifier: str) -> int:
    """
    Obtiene el número de intentos restantes.
    
    Args:
        identifier: Email o IP del usuario
        
    Returns:
        Número de intentos restantes antes de bloqueo
    """
    if identifier not in _login_attempts:
        return _max_attempts
    
    current_attempts = len(_login_attempts[identifier])
    return max(0, _max_attempts - current_attempts)


def clear_login_attempts(identifier: str) -> None:
    """
    Limpia los intentos de login (después de un login exitoso).
    
    Args:
        identifier: Email o IP del usuario
    """
    if identifier in _login_attempts:
        del _login_attempts[identifier]
