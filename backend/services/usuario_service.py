"""
Servicio de Usuario
Lógica de negocio para la gestión de usuarios.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from models.usuario import Usuario, EstadoUsuario
from models.rol import Rol
from models.profesor import Profesor
from models.estudiante import Estudiante
from core.security import (
    hash_password,
    verify_password,
    sanitize_email
)

# CRUD Básico

def crear_usuario(db: Session, datos_usuario: dict) -> Usuario:
    """
    Crea un nuevo usuario en el sistema.
    
    Args:
        db: Sesión de base de datos
        datos_usuario: Diccionario con los datos del usuario:
            - nombre: str
            - apellido: str
            - correo: str
            - password: str (se hasheará automáticamente)
            - rol_id: int
            - avatar_url: Optional[str]
            
    Returns:
        Usuario creado
        
    Raises:
        ValueError: Si el email ya existe o el rol no existe
        
    Example:
        >>> usuario = crear_usuario(db, {
        ...     "nombre": "Juan",
        ...     "apellido": "Pérez",
        ...     "correo": "juan@email.com",
        ...     "password": "Password123",
        ...     "rol_id": 3
        ... })
    """
    email = sanitize_email(datos_usuario["correo"])
    
    usuario_existente = db.query(Usuario).filter(Usuario.correo == email).first()
    if usuario_existente:
        raise ValueError(f"El email {email} ya está registrado")
    
    rol = db.query(Rol).filter(Rol.id == datos_usuario["rol_id"]).first()
    if not rol:
        raise ValueError(f"El rol con id {datos_usuario['rol_id']} no existe")
    
    password_hash = hash_password(datos_usuario["password"])
    
    nuevo_usuario = Usuario(
        nombre=datos_usuario["nombre"],
        apellido=datos_usuario["apellido"],
        correo=email,
        password_hash=password_hash,
        rol_id=datos_usuario["rol_id"],
        avatar_url=datos_usuario.get("avatar_url"),
        estado=EstadoUsuario.PENDIENTE_DE_VERIFICACION
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario


def obtener_usuario_por_id(db: Session, usuario_id: int) -> Optional[Usuario]:
    """
    Obtiene un usuario por su ID.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        
    Returns:
        Usuario si existe, None si no existe
        
    Example:
        >>> usuario = obtener_usuario_por_id(db, 1)
    """
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def obtener_usuario_por_email(db: Session, email: str) -> Optional[Usuario]:
    """
    Obtiene un usuario por su email.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        
    Returns:
        Usuario si existe, None si no existe
        
    Example:
        >>> usuario = obtener_usuario_por_email(db, "juan@email.com")
    """
    email = sanitize_email(email)
    return db.query(Usuario).filter(Usuario.correo == email).first()


def listar_usuarios(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    rol_id: Optional[int] = None,
    estado: Optional[EstadoUsuario] = None,
    busqueda: Optional[str] = None
) -> List[Usuario]:
    """
    Lista usuarios con filtros y paginación.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar (paginación)
        limit: Número máximo de registros a retornar
        rol_id: Filtrar por rol (opcional)
        estado: Filtrar por estado (opcional)
        busqueda: Buscar en nombre, apellido o email (opcional)
        
    Returns:
        Lista de usuarios que cumplen los criterios
        
    Example:
        >>> usuarios = listar_usuarios(db, rol_id=3, estado="Activo", skip=0, limit=10)
    """
    query = db.query(Usuario).options(joinedload(Usuario.rol))
    
    if rol_id:
        query = query.filter(Usuario.rol_id == rol_id)
    
    if estado:
        query = query.filter(Usuario.estado == estado)
    
    if busqueda:
        busqueda_pattern = f"%{busqueda}%"
        query = query.filter(
            or_(
                Usuario.nombre.ilike(busqueda_pattern),
                Usuario.apellido.ilike(busqueda_pattern),
                Usuario.correo.ilike(busqueda_pattern)
            )
        )
    
    query = query.order_by(Usuario.fecha_creacion.desc())
    
    return query.offset(skip).limit(limit).all()


def contar_usuarios(
    db: Session,
    rol_id: Optional[int] = None,
    estado: Optional[EstadoUsuario] = None,
    busqueda: Optional[str] = None
) -> int:
    """
    Cuenta el total de usuarios según filtros.
    
    Args:
        db: Sesión de base de datos
        rol_id: Filtrar por rol (opcional)
        estado: Filtrar por estado (opcional)
        busqueda: Buscar en nombre, apellido o email (opcional)
        
    Returns:
        Número total de usuarios
        
    Example:
        >>> total = contar_usuarios(db, rol_id=3, estado="Activo")
    """
    query = db.query(func.count(Usuario.id))
    
    if rol_id:
        query = query.filter(Usuario.rol_id == rol_id)
    
    if estado:
        query = query.filter(Usuario.estado == estado)
    
    if busqueda:
        busqueda_pattern = f"%{busqueda}%"
        query = query.filter(
            or_(
                Usuario.nombre.ilike(busqueda_pattern),
                Usuario.apellido.ilike(busqueda_pattern),
                Usuario.correo.ilike(busqueda_pattern)
            )
        )
    
    return query.scalar()


def actualizar_usuario(
    db: Session,
    usuario_id: int,
    datos_actualizados: dict
) -> Optional[Usuario]:
    """
    Actualiza los datos de un usuario.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario a actualizar
        datos_actualizados: Diccionario con los campos a actualizar:
            - nombre: Optional[str]
            - apellido: Optional[str]
            - correo: Optional[str]
            - rol_id: Optional[int]
            - avatar_url: Optional[str]
            - estado: Optional[EstadoUsuario]
            
    Returns:
        Usuario actualizado si existe, None si no existe
        
    Raises:
        ValueError: Si el nuevo email ya existe
        
    Example:
        >>> usuario = actualizar_usuario(db, 1, {
        ...     "nombre": "Juan Carlos",
        ...     "avatar_url": "https://nueva-url.com/avatar.jpg"
        ... })
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        return None
    
    if "correo" in datos_actualizados:
        nuevo_email = sanitize_email(datos_actualizados["correo"])
        if nuevo_email != usuario.correo:
            email_existente = obtener_usuario_por_email(db, nuevo_email)
            if email_existente:
                raise ValueError(f"El email {nuevo_email} ya está en uso")
            datos_actualizados["correo"] = nuevo_email
    
    for campo, valor in datos_actualizados.items():
        if hasattr(usuario, campo) and campo != "password_hash":
            setattr(usuario, campo, valor)
    
    db.commit()
    db.refresh(usuario)
    
    return usuario


def eliminar_usuario(db: Session, usuario_id: int) -> bool:
    """
    Elimina un usuario del sistema.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario a eliminar
        
    Returns:
        True si se eliminó, False si no existía
        
    Example:
        >>> eliminado = eliminar_usuario(db, 1)
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        return False
    
    db.delete(usuario)
    db.commit()
    
    return True


def autenticar_usuario(db: Session, email: str, password: str) -> Optional[Usuario]:
    """
    Autentica un usuario con email y contraseña.
    
    Args:
        db: Sesión de base de datos
        email: Email del usuario
        password: Contraseña en texto plano
        
    Returns:
        Usuario si las credenciales son correctas, None si son incorrectas
        
    Example:
        >>> usuario = autenticar_usuario(db, "juan@email.com", "Password123")
        >>> if usuario:
        ...     print("Login exitoso")
    """
    email = sanitize_email(email)
    usuario = obtener_usuario_por_email(db, email)
    
    if not usuario:
        return None
    
    if not verify_password(password, str(usuario.password_hash)):
        return None
    
    return usuario


def actualizar_ultimo_acceso(db: Session, usuario_id: int) -> None:
    """
    Actualiza la fecha y hora del último acceso del usuario.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        
    Example:
        >>> actualizar_ultimo_acceso(db, 1)
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if usuario:
        usuario.ultimo_acceso = datetime.utcnow()  # type: ignore
        db.commit()


def obtener_perfil_completo(db: Session, usuario_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene el perfil completo del usuario incluyendo datos específicos del rol.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        
    Returns:
        Diccionario con el perfil completo incluyendo:
        - Datos del usuario
        - Datos del rol
        - Perfil de profesor (si aplica)
        - Perfil de estudiante (si aplica)
        None si el usuario no existe
        
    Example:
        >>> perfil = obtener_perfil_completo(db, 1)
        >>> print(perfil["usuario"]["nombre"])
        >>> print(perfil["rol"]["nombre"])
    """
    usuario = db.query(Usuario).options(
        joinedload(Usuario.rol),
        joinedload(Usuario.profesor),
        joinedload(Usuario.estudiante)
    ).filter(Usuario.id == usuario_id).first()
    
    if not usuario:
        return None
    
    perfil = {
        "usuario": usuario,
        "rol": usuario.rol,
        "profesor": None,
        "estudiante": None
    }
    
    if usuario.profesor:
        perfil["profesor"] = usuario.profesor
    
    if usuario.estudiante:
        perfil["estudiante"] = usuario.estudiante
    
    return perfil


def actualizar_datos_personales(
    db: Session,
    usuario_id: int,
    datos_actualizados: dict
) -> Optional[Usuario]:
    """
    Actualiza datos personales del usuario (nombre, apellido, avatar).
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        datos_actualizados: Diccionario con:
            - nombre: Optional[str]
            - apellido: Optional[str]
            - avatar_url: Optional[str]
            
    Returns:
        Usuario actualizado si existe, None si no existe
        
    Example:
        >>> usuario = actualizar_datos_personales(db, 1, {
        ...     "nombre": "Juan Carlos",
        ...     "avatar_url": "https://nueva-url.com/avatar.jpg"
        ... })
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        return None
    
    campos_permitidos = ["nombre", "apellido", "avatar_url"]
    
    for campo in campos_permitidos:
        if campo in datos_actualizados:
            setattr(usuario, campo, datos_actualizados[campo])
    
    db.commit()
    db.refresh(usuario)
    
    return usuario


def cambiar_password(
    db: Session,
    usuario_id: int,
    password_antigua: str,
    password_nueva: str
) -> bool:
    """
    Cambia la contraseña de un usuario verificando la antigua.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        password_antigua: Contraseña actual (para verificación)
        password_nueva: Nueva contraseña
        
    Returns:
        True si se cambió exitosamente, False si la contraseña antigua es incorrecta
        
    Raises:
        ValueError: Si el usuario no existe
        
    Example:
        >>> cambiado = cambiar_password(db, 1, "OldPass123", "NewPass456")
        >>> if cambiado:
        ...     print("Contraseña actualizada")
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise ValueError(f"Usuario con id {usuario_id} no existe")
    
    if not verify_password(password_antigua, str(usuario.password_hash)):
        return False
    
    # Actualizar contraseña
    usuario.password_hash = hash_password(password_nueva)  # type: ignore
    db.commit()
    
    return True


def resetear_password(db: Session, usuario_id: int, password_nueva: str) -> bool:
    """
    Resetea la contraseña sin verificar la antigua (para recuperación).
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        password_nueva: Nueva contraseña
        
    Returns:
        True si se reseteó exitosamente, False si el usuario no existe
        
    Example:
        >>> reseteado = resetear_password(db, 1, "NewPassword123")
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        return False
    
    usuario.password_hash = hash_password(password_nueva)  # type: ignore
    db.commit()
    
    return True


def activar_usuario(db: Session, usuario_id: int) -> Optional[Usuario]:
    """
    Activa un usuario (cambia estado a ACTIVO).
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        
    Returns:
        Usuario actualizado si existe, None si no existe
        
    Example:
        >>> usuario = activar_usuario(db, 1)
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        return None
    
    usuario.estado = EstadoUsuario.ACTIVO # type: ignore
    db.commit()
    db.refresh(usuario)
    
    return usuario


def desactivar_usuario(db: Session, usuario_id: int) -> Optional[Usuario]:
    """
    Desactiva un usuario (cambia estado a INACTIVO).
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        
    Returns:
        Usuario actualizado si existe, None si no existe
        
    Example:
        >>> usuario = desactivar_usuario(db, 1)
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        return None
    
    usuario.estado = EstadoUsuario.INACTIVO # type: ignore
    db.commit()
    db.refresh(usuario)
    
    return usuario


def cambiar_estado_usuario(
    db: Session,
    usuario_id: int,
    nuevo_estado: EstadoUsuario
) -> Optional[Usuario]:
    """
    Cambia el estado de un usuario.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        nuevo_estado: Nuevo estado (ACTIVO, INACTIVO, PENDIENTE_DE_VERIFICACION)
        
    Returns:
        Usuario actualizado si existe, None si no existe
        
    Example:
        >>> usuario = cambiar_estado_usuario(db, 1, EstadoUsuario.ACTIVO)
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        return None
    
    usuario.estado = nuevo_estado # type: ignore
    db.commit()
    db.refresh(usuario)
    
    return usuario


def obtener_estadisticas_usuarios(db: Session) -> Dict[str, Any]:
    """
    Obtiene estadísticas generales de usuarios.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Diccionario con estadísticas:
        - total_usuarios
        - usuarios_activos
        - usuarios_inactivos
        - usuarios_pendientes
        - usuarios_por_rol
        - usuarios_creados_mes
        
    Example:
        >>> stats = obtener_estadisticas_usuarios(db)
        >>> print(f"Total: {stats['total_usuarios']}")
    """
    # Contadores por estado
    total = db.query(func.count(Usuario.id)).scalar()
    activos = db.query(func.count(Usuario.id)).filter(
        Usuario.estado == EstadoUsuario.ACTIVO
    ).scalar()
    inactivos = db.query(func.count(Usuario.id)).filter(
        Usuario.estado == EstadoUsuario.INACTIVO
    ).scalar()
    pendientes = db.query(func.count(Usuario.id)).filter(
        Usuario.estado == EstadoUsuario.PENDIENTE_DE_VERIFICACION
    ).scalar()
    
    # Usuarios por rol
    usuarios_por_rol = db.query(
        Rol.nombre,
        func.count(Usuario.id)
    ).join(Usuario.rol).group_by(Rol.nombre).all()
    
    # Usuarios creados en el último mes
    hace_un_mes = datetime.utcnow().replace(day=1)
    creados_mes = db.query(func.count(Usuario.id)).filter(
        Usuario.fecha_creacion >= hace_un_mes
    ).scalar()
    
    return {
        "total_usuarios": total,
        "usuarios_activos": activos,
        "usuarios_inactivos": inactivos,
        "usuarios_pendientes": pendientes,
        "usuarios_por_rol": [
            {"rol": rol, "cantidad": cantidad}
            for rol, cantidad in usuarios_por_rol
        ],
        "usuarios_creados_mes": creados_mes
    }


def obtener_usuarios_por_rol(db: Session, rol_nombre: str) -> List[Usuario]:
    """
    Obtiene todos los usuarios de un rol específico.
    
    Args:
        db: Sesión de base de datos
        rol_nombre: Nombre del rol (Superadmin, Profesor, Estudiante, Coordinador)
        
    Returns:
        Lista de usuarios con ese rol
        
    Example:
        >>> profesores = obtener_usuarios_por_rol(db, "Profesor")
    """
    return db.query(Usuario).join(Usuario.rol).filter(
        Rol.nombre == rol_nombre
    ).all()


def buscar_usuarios(db: Session, termino: str, limit: int = 20) -> List[Usuario]:
    """
    Busca usuarios por nombre, apellido o email.
    
    Args:
        db: Sesión de base de datos
        termino: Término de búsqueda
        limit: Número máximo de resultados
        
    Returns:
        Lista de usuarios que coinciden con la búsqueda
        
    Example:
        >>> resultados = buscar_usuarios(db, "juan")
    """
    pattern = f"%{termino}%"
    return db.query(Usuario).filter(
        or_(
            Usuario.nombre.ilike(pattern),
            Usuario.apellido.ilike(pattern),
            Usuario.correo.ilike(pattern)
        )
    ).limit(limit).all()


def email_existe(db: Session, email: str) -> bool:
    """
    Verifica si un email ya está registrado.
    
    Args:
        db: Sesión de base de datos
        email: Email a verificar
        
    Returns:
        True si el email existe, False si no existe
        
    Example:
        >>> if email_existe(db, "nuevo@email.com"):
        ...     print("Email ya registrado")
    """
    email = sanitize_email(email)
    return db.query(Usuario).filter(Usuario.correo == email).first() is not None


def usuario_esta_activo(db: Session, usuario_id: int) -> bool:
    """
    Verifica si un usuario está en estado ACTIVO.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        
    Returns:
        True si está activo, False si no existe o no está activo
        
    Example:
        >>> if usuario_esta_activo(db, 1):
        ...     print("Usuario activo")
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    return usuario is not None and usuario.estado == EstadoUsuario.ACTIVO # type: ignore


def usuario_puede_iniciar_sesion(db: Session, usuario_id: int) -> tuple[bool, str]:
    """
    Verifica si un usuario puede iniciar sesión.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
        
    Returns:
        Tupla (puede_iniciar, mensaje)
        - puede_iniciar: True si puede, False si no
        - mensaje: Razón por la que no puede (si aplica)
        
    Example:
        >>> puede, mensaje = usuario_puede_iniciar_sesion(db, 1)
        >>> if not puede:
        ...     print(f"No puede iniciar sesión: {mensaje}")
    """
    usuario = obtener_usuario_por_id(db, usuario_id)
    
    if not usuario:
        return False, "Usuario no existe"
    
    if usuario.estado == EstadoUsuario.INACTIVO:  # type: ignore
        return False, "Usuario inactivo"
    
    if usuario.estado == EstadoUsuario.PENDIENTE_DE_VERIFICACION:  # type: ignore
        return False, "Email pendiente de verificación"
    
    return True, "OK"
