"""
Servicio de Facultad

Este módulo contiene toda la lógica de negocio relacionada con las facultades.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func

from models.facultad import Facultad
from models.profesor import Profesor
from models.curso import Curso


def crear_facultad(
    db: Session,
    datos_facultad: Dict[str, Any]
) -> Facultad:
    """
    Crea una nueva facultad en el sistema.
    
    Args:
        db: Sesión de base de datos
        datos_facultad: Diccionario con los datos de la facultad
            - codigo (str): Código único de la facultad (requerido)
            - nombre (str): Nombre completo de la facultad (requerido)
    
    Returns:
        Facultad creada
    
    Raises:
        ValueError: Si el código o nombre ya existen, o faltan datos requeridos
    
    Example:
        >>> facultad = crear_facultad(db, {
        ...     "codigo": "ING",
        ...     "nombre": "Facultad de Ingeniería"
        ... })
    """
    if not datos_facultad.get("codigo"):
        raise ValueError("El código de la facultad es requerido")
    if not datos_facultad.get("nombre"):
        raise ValueError("El nombre de la facultad es requerido")
    
    facultad_por_codigo = db.query(Facultad).filter(
        Facultad.codigo == datos_facultad["codigo"]
    ).first()
    if facultad_por_codigo:
        raise ValueError(
            f"Ya existe una facultad con el código {datos_facultad['codigo']}"
        )
    
    facultad_por_nombre = db.query(Facultad).filter(
        Facultad.nombre == datos_facultad["nombre"]
    ).first()
    if facultad_por_nombre:
        raise ValueError(
            f"Ya existe una facultad con el nombre {datos_facultad['nombre']}"
        )
    
    nueva_facultad = Facultad(
        codigo=datos_facultad["codigo"],
        nombre=datos_facultad["nombre"]
    )
    
    db.add(nueva_facultad)
    db.commit()
    db.refresh(nueva_facultad)
    
    return nueva_facultad


def obtener_facultades(db: Session) -> List[Facultad]:
    """
    Obtiene todas las facultades del sistema.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Lista de todas las facultades
    
    Example:
        >>> facultades = obtener_facultades(db)
        >>> for facultad in facultades:
        ...     print(f"{facultad.codigo}: {facultad.nombre}")
    """
    return db.query(Facultad).order_by(Facultad.nombre).all()


def obtener_facultad_por_id(
    db: Session,
    facultad_id: int
) -> Optional[Facultad]:
    """
    Obtiene una facultad por su ID con sus relaciones cargadas.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad
    
    Returns:
        Facultad encontrada o None
    
    Example:
        >>> facultad = obtener_facultad_por_id(db, 1)
        >>> if facultad:
        ...     print(f"Facultad: {facultad.nombre}")
    """
    return db.query(Facultad).options(
        joinedload(Facultad.programas_academicos),  # type: ignore
        joinedload(Facultad.cursos),  # type: ignore
        joinedload(Facultad.profesores)  # type: ignore
    ).filter(Facultad.id == facultad_id).first()


def actualizar_facultad(
    db: Session,
    facultad_id: int,
    datos_actualizados: Dict[str, Any]
) -> Facultad:
    """
    Actualiza los datos de una facultad.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad a actualizar
        datos_actualizados: Diccionario con los campos a actualizar
    
    Returns:
        Facultad actualizada
    
    Raises:
        ValueError: Si la facultad no existe o hay conflicto de código/nombre
    
    Example:
        >>> facultad = actualizar_facultad(db, 1, {
        ...     "nombre": "Facultad de Ingeniería y Tecnología"
        ... })
    """
    facultad = obtener_facultad_por_id(db, facultad_id)
    if not facultad:
        raise ValueError(f"La facultad con ID {facultad_id} no existe")
    
    if "codigo" in datos_actualizados and datos_actualizados["codigo"] != facultad.codigo:
        facultad_con_codigo = db.query(Facultad).filter(
            Facultad.codigo == datos_actualizados["codigo"]
        ).first()
        if facultad_con_codigo:
            raise ValueError(
                f"Ya existe una facultad con el código {datos_actualizados['codigo']}"
            )
    
    if "nombre" in datos_actualizados and datos_actualizados["nombre"] != facultad.nombre:
        facultad_con_nombre = db.query(Facultad).filter(
            Facultad.nombre == datos_actualizados["nombre"]
        ).first()
        if facultad_con_nombre:
            raise ValueError(
                f"Ya existe una facultad con el nombre {datos_actualizados['nombre']}"
            )
    
    campos_permitidos = ["codigo", "nombre"]
    
    for campo, valor in datos_actualizados.items():
        if campo in campos_permitidos and hasattr(facultad, campo):
            setattr(facultad, campo, valor)
    
    db.commit()
    db.refresh(facultad)
    
    return facultad


def obtener_profesores_por_facultad(
    db: Session,
    facultad_id: int
) -> List[Profesor]:
    """
    Obtiene todos los profesores adscritos a una facultad.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad
    
    Returns:
        Lista de profesores de la facultad
    
    Raises:
        ValueError: Si la facultad no existe
    
    Example:
        >>> profesores = obtener_profesores_por_facultad(db, 1)
        >>> print(f"La facultad tiene {len(profesores)} profesores")
    """
    facultad = obtener_facultad_por_id(db, facultad_id)
    if not facultad:
        raise ValueError(f"La facultad con ID {facultad_id} no existe")
    
    return db.query(Profesor).filter(
        Profesor.facultad_id == facultad_id
    ).all()


def obtener_cursos_por_facultad(
    db: Session,
    facultad_id: int
) -> List[Curso]:
    """
    Obtiene todos los cursos que pertenecen a una facultad.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad
    
    Returns:
        Lista de cursos de la facultad
    
    Raises:
        ValueError: Si la facultad no existe
    
    Example:
        >>> cursos = obtener_cursos_por_facultad(db, 1)
        >>> print(f"La facultad ofrece {len(cursos)} cursos")
    """
    facultad = obtener_facultad_por_id(db, facultad_id)
    if not facultad:
        raise ValueError(f"La facultad con ID {facultad_id} no existe")
    
    return db.query(Curso).filter(
        Curso.facultad_id == facultad_id
    ).all()


def obtener_facultad_por_codigo(
    db: Session,
    codigo: str
) -> Optional[Facultad]:
    """
    Obtiene una facultad por su código único.
    
    Args:
        db: Sesión de base de datos
        codigo: Código de la facultad
    
    Returns:
        Facultad encontrada o None
    
    Example:
        >>> facultad = obtener_facultad_por_codigo(db, "ING")
    """
    return db.query(Facultad).filter(Facultad.codigo == codigo).first()


def buscar_facultades(
    db: Session,
    termino: str
) -> List[Facultad]:
    """
    Busca facultades por código o nombre.
    
    Args:
        db: Sesión de base de datos
        termino: Término de búsqueda
    
    Returns:
        Lista de facultades que coinciden
    
    Example:
        >>> resultados = buscar_facultades(db, "ingeniería")
    """
    patron = f"%{termino}%"
    
    return db.query(Facultad).filter(
        or_(
            Facultad.codigo.ilike(patron),
            Facultad.nombre.ilike(patron)
        )
    ).all()


def facultad_existe(
    db: Session,
    facultad_id: int
) -> bool:
    """
    Verifica si existe una facultad con el ID dado.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad
    
    Returns:
        True si existe, False en caso contrario
    
    Example:
        >>> if facultad_existe(db, 1):
        ...     print("La facultad existe")
    """
    return db.query(Facultad).filter(Facultad.id == facultad_id).first() is not None


def codigo_facultad_existe(
    db: Session,
    codigo: str
) -> bool:
    """
    Verifica si existe una facultad con el código dado.
    
    Args:
        db: Sesión de base de datos
        codigo: Código de la facultad
    
    Returns:
        True si existe, False en caso contrario
    
    Example:
        >>> if codigo_facultad_existe(db, "ING"):
        ...     print("El código ya está en uso")
    """
    return db.query(Facultad).filter(Facultad.codigo == codigo).first() is not None


def nombre_facultad_existe(
    db: Session,
    nombre: str
) -> bool:
    """
    Verifica si existe una facultad con el nombre dado.
    
    Args:
        db: Sesión de base de datos
        nombre: Nombre de la facultad
    
    Returns:
        True si existe, False en caso contrario
    
    Example:
        >>> if nombre_facultad_existe(db, "Facultad de Ingeniería"):
        ...     print("El nombre ya está en uso")
    """
    return db.query(Facultad).filter(Facultad.nombre == nombre).first() is not None


def facultad_tiene_profesores(
    db: Session,
    facultad_id: int
) -> bool:
    """
    Verifica si una facultad tiene profesores adscritos.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad
    
    Returns:
        True si tiene profesores, False en caso contrario
    
    Example:
        >>> if facultad_tiene_profesores(db, 1):
        ...     print("No se puede eliminar, tiene profesores")
    """
    return db.query(Profesor).filter(
        Profesor.facultad_id == facultad_id
    ).first() is not None


def facultad_tiene_cursos(
    db: Session,
    facultad_id: int
) -> bool:
    """
    Verifica si una facultad tiene cursos asociados.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad
    
    Returns:
        True si tiene cursos, False en caso contrario
    
    Example:
        >>> if facultad_tiene_cursos(db, 1):
        ...     print("No se puede eliminar, tiene cursos")
    """
    return db.query(Curso).filter(
        Curso.facultad_id == facultad_id
    ).first() is not None


def obtener_estadisticas_facultad(
    db: Session,
    facultad_id: int
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de una facultad.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad
    
    Returns:
        Diccionario con estadísticas:
        - total_profesores: Total de profesores adscritos
        - total_cursos: Total de cursos ofrecidos
        - total_programas: Total de programas académicos
    
    Raises:
        ValueError: Si la facultad no existe
    
    Example:
        >>> stats = obtener_estadisticas_facultad(db, 1)
        >>> print(f"Profesores: {stats['total_profesores']}")
    """
    facultad = obtener_facultad_por_id(db, facultad_id)
    if not facultad:
        raise ValueError(f"La facultad con ID {facultad_id} no existe")
    
    total_profesores = db.query(func.count(Profesor.id)).filter(
        Profesor.facultad_id == facultad_id
    ).scalar()
    
    total_cursos = db.query(func.count(Curso.id)).filter(
        Curso.facultad_id == facultad_id
    ).scalar()
    
    from models.programa_academico import ProgramaAcademico
    total_programas = db.query(func.count(ProgramaAcademico.id)).filter(
        ProgramaAcademico.facultad_id == facultad_id
    ).scalar()
    
    return {
        "total_profesores": total_profesores or 0,
        "total_cursos": total_cursos or 0,
        "total_programas": total_programas or 0
    }


def obtener_resumen_facultades(db: Session) -> List[Dict[str, Any]]:
    """
    Obtiene un resumen de todas las facultades con sus estadísticas.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Lista de diccionarios con información resumida de cada facultad
    
    Example:
        >>> resumen = obtener_resumen_facultades(db)
        >>> for item in resumen:
        ...     print(f"{item['nombre']}: {item['total_cursos']} cursos")
    """
    from models.programa_academico import ProgramaAcademico
    
    facultades = obtener_facultades(db)
    resumen = []
    
    for facultad in facultades:
        total_profesores = db.query(func.count(Profesor.id)).filter(
            Profesor.facultad_id == facultad.id
        ).scalar()
        
        total_cursos = db.query(func.count(Curso.id)).filter(
            Curso.facultad_id == facultad.id
        ).scalar()
        
        total_programas = db.query(func.count(ProgramaAcademico.id)).filter(
            ProgramaAcademico.facultad_id == facultad.id
        ).scalar()
        
        resumen.append({
            "id": facultad.id,
            "codigo": facultad.codigo,
            "nombre": facultad.nombre,
            "total_profesores": total_profesores or 0,
            "total_cursos": total_cursos or 0,
            "total_programas": total_programas or 0
        })
    
    return resumen
