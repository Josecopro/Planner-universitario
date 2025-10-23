"""
Servicio de Rol

Este módulo contiene toda la lógica de negocio relacionada con los roles del sistema.
"""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from models.rol import Rol


def crear_rol(
    db: Session,
    datos_rol: dict
) -> Rol:
    """
    Crea un nuevo rol en el sistema.
    
    Args:
        db: Sesión de base de datos
        datos_rol: Diccionario con los datos del rol
            - nombre (str): Nombre único del rol (requerido)
            - descripcion (str, opcional): Descripción del rol
    
    Returns:
        Rol creado
    
    Raises:
        ValueError: Si el nombre ya existe o falta
    
    Example:
        >>> rol = crear_rol(db, {
        ...     "nombre": "Coordinador",
        ...     "descripcion": "Coordinador de programa académico"
        ... })
    """
    if not datos_rol.get("nombre"):
        raise ValueError("El nombre del rol es requerido")
    
    rol_existente = db.query(Rol).filter(
        Rol.nombre == datos_rol["nombre"]
    ).first()
    if rol_existente:
        raise ValueError(f"Ya existe un rol con el nombre {datos_rol['nombre']}")
    
    nuevo_rol = Rol(
        nombre=datos_rol["nombre"],
        descripcion=datos_rol.get("descripcion")
    )
    
    db.add(nuevo_rol)
    db.commit()
    db.refresh(nuevo_rol)
    
    return nuevo_rol


def obtener_roles(db: Session) -> List[Rol]:
    """
    Obtiene todos los roles del sistema.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Lista de todos los roles ordenados por nombre
    
    Example:
        >>> roles = obtener_roles(db)
        >>> for rol in roles:
        ...     print(f"{rol.nombre}: {rol.descripcion}")
    """
    return db.query(Rol).order_by(Rol.nombre).all()


def actualizar_descripcion_rol(
    db: Session,
    rol_id: int,
    nueva_descripcion: str
) -> Rol:
    """
    Actualiza la descripción de un rol.
    
    Args:
        db: Sesión de base de datos
        rol_id: ID del rol a actualizar
        nueva_descripcion: Nueva descripción del rol
    
    Returns:
        Rol actualizado
    
    Raises:
        ValueError: Si el rol no existe
    
    Example:
        >>> rol = actualizar_descripcion_rol(
        ...     db, 
        ...     1, 
        ...     "Administrador del sistema con acceso total"
        ... )
    """
    rol = obtener_rol_por_id(db, rol_id)
    if not rol:
        raise ValueError(f"El rol con ID {rol_id} no existe")
    
    rol.descripcion = nueva_descripcion  # type: ignore
    db.commit()
    db.refresh(rol)
    
    return rol


def eliminar_rol(
    db: Session,
    rol_id: int
) -> bool:
    """
    Elimina un rol del sistema.
    
    Args:
        db: Sesión de base de datos
        rol_id: ID del rol a eliminar
    
    Returns:
        True si se eliminó correctamente
    
    Raises:
        ValueError: Si el rol no existe o tiene usuarios asociados
    
    Example:
        >>> if eliminar_rol(db, 5):
        ...     print("Rol eliminado correctamente")
    """
    rol = obtener_rol_por_id(db, rol_id)
    if not rol:
        raise ValueError(f"El rol con ID {rol_id} no existe")
    
    if rol_tiene_usuarios(db, rol_id):
        raise ValueError(
            f"No se puede eliminar el rol '{rol.nombre}' porque tiene usuarios asociados"
        )
    
    db.delete(rol)
    db.commit()
    
    return True


def obtener_rol_por_id(
    db: Session,
    rol_id: int
) -> Optional[Rol]:
    """
    Obtiene un rol por su ID con relaciones cargadas.
    
    Args:
        db: Sesión de base de datos
        rol_id: ID del rol
    
    Returns:
        Rol encontrado o None
    
    Example:
        >>> rol = obtener_rol_por_id(db, 1)
        >>> if rol:
        ...     print(f"Rol: {rol.nombre}")
    """
    return db.query(Rol).options(
        joinedload(Rol.usuarios)  # type: ignore
    ).filter(Rol.id == rol_id).first()


def obtener_rol_por_nombre(
    db: Session,
    nombre: str
) -> Optional[Rol]:
    """
    Obtiene un rol por su nombre.
    
    Args:
        db: Sesión de base de datos
        nombre: Nombre del rol
    
    Returns:
        Rol encontrado o None
    
    Example:
        >>> rol = obtener_rol_por_nombre(db, "Profesor")
    """
    return db.query(Rol).filter(Rol.nombre == nombre).first()


def buscar_roles(
    db: Session,
    termino: str
) -> List[Rol]:
    """
    Busca roles por nombre o descripción.
    
    Args:
        db: Sesión de base de datos
        termino: Término de búsqueda
    
    Returns:
        Lista de roles que coinciden
    
    Example:
        >>> resultados = buscar_roles(db, "admin")
    """
    patron = f"%{termino}%"
    
    return db.query(Rol).filter(
        or_(
            Rol.nombre.ilike(patron),
            Rol.descripcion.ilike(patron)
        )
    ).all()


def rol_existe(
    db: Session,
    rol_id: int
) -> bool:
    """
    Verifica si existe un rol con el ID dado.
    
    Args:
        db: Sesión de base de datos
        rol_id: ID del rol
    
    Returns:
        True si existe, False en caso contrario
    
    Example:
        >>> if rol_existe(db, 1):
        ...     print("El rol existe")
    """
    return db.query(Rol).filter(Rol.id == rol_id).first() is not None


def nombre_rol_existe(
    db: Session,
    nombre: str
) -> bool:
    """
    Verifica si existe un rol con el nombre dado.
    
    Args:
        db: Sesión de base de datos
        nombre: Nombre del rol
    
    Returns:
        True si existe, False en caso contrario
    
    Example:
        >>> if nombre_rol_existe(db, "Profesor"):
        ...     print("El nombre ya está en uso")
    """
    return db.query(Rol).filter(Rol.nombre == nombre).first() is not None


def rol_tiene_usuarios(
    db: Session,
    rol_id: int
) -> bool:
    """
    Verifica si un rol tiene usuarios asociados.
    
    Args:
        db: Sesión de base de datos
        rol_id: ID del rol
    
    Returns:
        True si tiene usuarios, False en caso contrario
    
    Example:
        >>> if rol_tiene_usuarios(db, 1):
        ...     print("No se puede eliminar, tiene usuarios")
    """
    from models.usuario import Usuario
    
    return db.query(Usuario).filter(
        Usuario.rol_id == rol_id
    ).first() is not None


def obtener_usuarios_por_rol(
    db: Session,
    rol_id: int
) -> List:
    """
    Obtiene todos los usuarios que tienen un rol específico.
    
    Args:
        db: Sesión de base de datos
        rol_id: ID del rol
    
    Returns:
        Lista de usuarios con ese rol
    
    Raises:
        ValueError: Si el rol no existe
    
    Example:
        >>> usuarios = obtener_usuarios_por_rol(db, 1)
        >>> print(f"Total usuarios con este rol: {len(usuarios)}")
    """
    from models.usuario import Usuario
    
    rol = obtener_rol_por_id(db, rol_id)
    if not rol:
        raise ValueError(f"El rol con ID {rol_id} no existe")
    
    return db.query(Usuario).filter(Usuario.rol_id == rol_id).all()


def contar_usuarios_por_rol(
    db: Session,
    rol_id: int
) -> int:
    """
    Cuenta cuántos usuarios tienen un rol específico.
    
    Args:
        db: Sesión de base de datos
        rol_id: ID del rol
    
    Returns:
        Cantidad de usuarios con ese rol
    
    Raises:
        ValueError: Si el rol no existe
    
    Example:
        >>> total = contar_usuarios_por_rol(db, 1)
        >>> print(f"Total de usuarios: {total}")
    """
    from models.usuario import Usuario
    
    rol = obtener_rol_por_id(db, rol_id)
    if not rol:
        raise ValueError(f"El rol con ID {rol_id} no existe")
    
    return db.query(Usuario).filter(Usuario.rol_id == rol_id).count()


def inicializar_roles_sistema(db: Session) -> List[Rol]:
    """
    Inicializa los roles básicos del sistema si no existen.
    
    Crea los roles: Superadmin, Profesor, Estudiante
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Lista de roles creados o existentes
    
    Example:
        >>> roles = inicializar_roles_sistema(db)
        >>> print(f"Roles del sistema: {len(roles)}")
    """
    roles_base = [
        {
            "nombre": "Superadmin",
            "descripcion": "Administrador del sistema con acceso total a todas las funcionalidades"
        },
        {
            "nombre": "Profesor",
            "descripcion": "Docente con acceso a gestión de cursos, grupos, calificaciones y asistencia"
        },
        {
            "nombre": "Estudiante",
            "descripcion": "Estudiante con acceso a consulta de cursos, calificaciones y horarios"
        }
    ]
    
    roles_creados = []
    
    for datos_rol in roles_base:
        rol_existente = obtener_rol_por_nombre(db, datos_rol["nombre"])
        if rol_existente:
            roles_creados.append(rol_existente)
        else:
            nuevo_rol = crear_rol(db, datos_rol)
            roles_creados.append(nuevo_rol)
    
    return roles_creados
