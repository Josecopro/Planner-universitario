"""
Servicio de Curso

Este módulo contiene toda la lógica de negocio relacionada con los cursos.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from models.curso import Curso, EstadoCurso
from models.facultad import Facultad
from models.grupo import Grupo


def crear_curso(
    db: Session,
    datos_curso: Dict[str, Any]
) -> Curso:
    """
    Crea un nuevo curso en el catálogo.
    
    Args:
        db: Sesión de base de datos
        datos_curso: Diccionario con los datos del curso
            - codigo (str): Código único del curso (requerido)
            - nombre (str): Nombre del curso (requerido)
            - facultad_id (int): ID de la facultad (requerido)
            - estado (EstadoCurso, opcional): Estado del curso (default: ACTIVO)
    
    Returns:
        Curso creado
    
    Raises:
        ValueError: Si el código ya existe, la facultad no existe, o faltan datos requeridos
    
    Example:
        >>> curso = crear_curso(db, {
        ...     "codigo": "IS-101",
        ...     "nombre": "Introducción a la Programación",
        ...     "facultad_id": 1
        ... })
    """
    if not datos_curso.get("codigo"):
        raise ValueError("El código del curso es requerido")
    if not datos_curso.get("nombre"):
        raise ValueError("El nombre del curso es requerido")
    if not datos_curso.get("facultad_id"):
        raise ValueError("El facultad_id es requerido")
    
    curso_existente = db.query(Curso).filter(
        Curso.codigo == datos_curso["codigo"]
    ).first()
    if curso_existente:
        raise ValueError(f"Ya existe un curso con el código {datos_curso['codigo']}")
    
    facultad = db.query(Facultad).filter(
        Facultad.id == datos_curso["facultad_id"]
    ).first()
    if not facultad:
        raise ValueError(
            f"La facultad con ID {datos_curso['facultad_id']} no existe"
        )
    
    nuevo_curso = Curso(
        codigo=datos_curso["codigo"],
        nombre=datos_curso["nombre"],
        facultad_id=datos_curso["facultad_id"],
        estado=datos_curso.get("estado", EstadoCurso.ACTIVO)
    )
    
    db.add(nuevo_curso)
    db.commit()
    db.refresh(nuevo_curso)
    
    return nuevo_curso


def obtener_cursos(
    db: Session,
    filtros: Optional[Dict[str, Any]] = None
) -> List[Curso]:
    """
    Obtiene una lista de cursos aplicando filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        filtros: Diccionario opcional con filtros:
            - facultad_id (int): Filtrar por facultad
            - estado (EstadoCurso): Filtrar por estado
            - codigo (str): Buscar por código (parcial)
            - nombre (str): Buscar por nombre (parcial)
    
    Returns:
        Lista de cursos que cumplen los filtros
    
    Example:
        >>> cursos = obtener_cursos(db, {"facultad_id": 1, "estado": EstadoCurso.ACTIVO})
        >>> cursos_programacion = obtener_cursos(db, {"nombre": "programación"})
    """
    query = db.query(Curso).options(
        joinedload(Curso.facultad)  # type: ignore
    )
    
    if filtros:
        if "facultad_id" in filtros and filtros["facultad_id"]:
            query = query.filter(Curso.facultad_id == filtros["facultad_id"])
        
        if "estado" in filtros and filtros["estado"]:
            query = query.filter(Curso.estado == filtros["estado"])
        
        if "codigo" in filtros and filtros["codigo"]:
            query = query.filter(Curso.codigo.ilike(f"%{filtros['codigo']}%"))
        
        if "nombre" in filtros and filtros["nombre"]:
            query = query.filter(Curso.nombre.ilike(f"%{filtros['nombre']}%"))
    
    return query.all()


def obtener_curso_por_id(
    db: Session,
    curso_id: int
) -> Optional[Curso]:
    """
    Obtiene un curso por su ID con sus relaciones cargadas.
    
    Args:
        db: Sesión de base de datos
        curso_id: ID del curso
    
    Returns:
        Curso encontrado o None
    
    Example:
        >>> curso = obtener_curso_por_id(db, 1)
        >>> if curso:
        ...     print(f"Curso: {curso.nombre}")
    """
    return db.query(Curso).options(
        joinedload(Curso.facultad),  # type: ignore
        joinedload(Curso.grupos)  # type: ignore
    ).filter(Curso.id == curso_id).first()


def actualizar_curso(
    db: Session,
    curso_id: int,
    datos_actualizacion: Dict[str, Any]
) -> Curso:
    """
    Actualiza los datos de un curso.
    
    Args:
        db: Sesión de base de datos
        curso_id: ID del curso a actualizar
        datos_actualizacion: Diccionario con los campos a actualizar
    
    Returns:
        Curso actualizado
    
    Raises:
        ValueError: Si el curso no existe, el código ya existe, o la facultad no es válida
    
    Example:
        >>> curso = actualizar_curso(db, 1, {
        ...     "nombre": "Programación Avanzada I",
        ...     "estado": EstadoCurso.ACTIVO
        ... })
    """
    curso = obtener_curso_por_id(db, curso_id)
    if not curso:
        raise ValueError(f"El curso con ID {curso_id} no existe")
    
    if "codigo" in datos_actualizacion and datos_actualizacion["codigo"] != curso.codigo:
        curso_con_codigo = db.query(Curso).filter(
            Curso.codigo == datos_actualizacion["codigo"]
        ).first()
        if curso_con_codigo:
            raise ValueError(
                f"Ya existe un curso con el código {datos_actualizacion['codigo']}"
            )
    
    if "facultad_id" in datos_actualizacion and datos_actualizacion["facultad_id"]:
        facultad = db.query(Facultad).filter(
            Facultad.id == datos_actualizacion["facultad_id"]
        ).first()
        if not facultad:
            raise ValueError(
                f"La facultad con ID {datos_actualizacion['facultad_id']} no existe"
            )
    
    campos_permitidos = ["codigo", "nombre", "facultad_id", "estado"]
    
    for campo, valor in datos_actualizacion.items():
        if campo in campos_permitidos and hasattr(curso, campo):
            setattr(curso, campo, valor)
    
    db.commit()
    db.refresh(curso)
    
    return curso


def desactivar_curso(
    db: Session,
    curso_id: int
) -> Curso:
    """
    Desactiva un curso cambiando su estado a INACTIVO.
    
    Args:
        db: Sesión de base de datos
        curso_id: ID del curso a desactivar
    
    Returns:
        Curso desactivado
    
    Raises:
        ValueError: Si el curso no existe
    
    Example:
        >>> curso = desactivar_curso(db, 1)
        >>> assert curso.estado == EstadoCurso.INACTIVO
    """
    curso = obtener_curso_por_id(db, curso_id)
    if not curso:
        raise ValueError(f"El curso con ID {curso_id} no existe")
    
    curso.estado = EstadoCurso.INACTIVO  # type: ignore
    db.commit()
    db.refresh(curso)
    
    return curso


def obtener_grupos_por_curso(
    db: Session,
    curso_id: int,
    semestre: Optional[str] = None
) -> List[Grupo]:
    """
    Obtiene todos los grupos asociados a un curso.
    
    Args:
        db: Sesión de base de datos
        curso_id: ID del curso
        semestre: Filtro opcional por semestre (ej: "2024-1")
    
    Returns:
        Lista de grupos del curso
    
    Raises:
        ValueError: Si el curso no existe
    
    Example:
        >>> grupos = obtener_grupos_por_curso(db, 1, "2024-1")
        >>> for grupo in grupos:
        ...     print(f"Grupo {grupo.numero_grupo}")
    """
    curso = obtener_curso_por_id(db, curso_id)
    if not curso:
        raise ValueError(f"El curso con ID {curso_id} no existe")
    
    query = db.query(Grupo).filter(Grupo.curso_id == curso_id)
    
    if semestre:
        query = query.filter(Grupo.semestre == semestre)
    
    return query.all()


def obtener_curso_por_codigo(
    db: Session,
    codigo: str
) -> Optional[Curso]:
    """
    Obtiene un curso por su código único.
    
    Args:
        db: Sesión de base de datos
        codigo: Código del curso
    
    Returns:
        Curso encontrado o None
    
    Example:
        >>> curso = obtener_curso_por_codigo(db, "IS-101")
    """
    return db.query(Curso).filter(Curso.codigo == codigo).first()


def obtener_cursos_por_facultad(
    db: Session,
    facultad_id: int,
    solo_activos: bool = True
) -> List[Curso]:
    """
    Obtiene todos los cursos de una facultad.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad
        solo_activos: Si True, solo retorna cursos activos
    
    Returns:
        Lista de cursos de la facultad
    
    Example:
        >>> cursos = obtener_cursos_por_facultad(db, 1)
    """
    query = db.query(Curso).filter(Curso.facultad_id == facultad_id)
    
    if solo_activos:
        query = query.filter(Curso.estado == EstadoCurso.ACTIVO)
    
    return query.all()


def buscar_cursos(
    db: Session,
    termino: str,
    limit: int = 20
) -> List[Curso]:
    """
    Busca cursos por código o nombre.
    
    Args:
        db: Sesión de base de datos
        termino: Término de búsqueda
        limit: Máximo de resultados
    
    Returns:
        Lista de cursos que coinciden
    
    Example:
        >>> resultados = buscar_cursos(db, "programación")
    """
    patron = f"%{termino}%"
    
    return db.query(Curso).filter(
        or_(
            Curso.codigo.ilike(patron),
            Curso.nombre.ilike(patron)
        )
    ).limit(limit).all()


def curso_existe(
    db: Session,
    curso_id: int
) -> bool:
    """
    Verifica si existe un curso con el ID dado.
    
    Args:
        db: Sesión de base de datos
        curso_id: ID del curso
    
    Returns:
        True si existe, False en caso contrario
    
    Example:
        >>> if curso_existe(db, 1):
        ...     print("El curso existe")
    """
    return db.query(Curso).filter(Curso.id == curso_id).first() is not None


def codigo_curso_existe(
    db: Session,
    codigo: str
) -> bool:
    """
    Verifica si existe un curso con el código dado.
    
    Args:
        db: Sesión de base de datos
        codigo: Código del curso
    
    Returns:
        True si existe, False en caso contrario
    
    Example:
        >>> if codigo_curso_existe(db, "IS-101"):
        ...     print("El código ya está en uso")
    """
    return db.query(Curso).filter(Curso.codigo == codigo).first() is not None


def curso_tiene_grupos_activos(
    db: Session,
    curso_id: int
) -> bool:
    """
    Verifica si un curso tiene grupos activos.
    
    Args:
        db: Sesión de base de datos
        curso_id: ID del curso
    
    Returns:
        True si tiene grupos activos, False en caso contrario
    
    Example:
        >>> if curso_tiene_grupos_activos(db, 1):
        ...     print("No se puede eliminar, tiene grupos activos")
    """
    from models.grupo import EstadoGrupo
    
    return db.query(Grupo).filter(
        and_(
            Grupo.curso_id == curso_id,
            Grupo.estado.in_([EstadoGrupo.ABIERTO, EstadoGrupo.EN_CURSO])
        )
    ).first() is not None


def obtener_estadisticas_curso(
    db: Session,
    curso_id: int
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de un curso.
    
    Args:
        db: Sesión de base de datos
        curso_id: ID del curso
    
    Returns:
        Diccionario con estadísticas:
        - total_grupos: Total de grupos creados
        - grupos_activos: Grupos actualmente activos
        - total_estudiantes_historicos: Total de estudiantes que han cursado
    
    Raises:
        ValueError: Si el curso no existe
    
    Example:
        >>> stats = obtener_estadisticas_curso(db, 1)
        >>> print(f"Total grupos: {stats['total_grupos']}")
    """
    curso = obtener_curso_por_id(db, curso_id)
    if not curso:
        raise ValueError(f"El curso con ID {curso_id} no existe")
    
    total_grupos = db.query(func.count(Grupo.id)).filter(
        Grupo.curso_id == curso_id
    ).scalar()
    
    from models.grupo import EstadoGrupo
    grupos_activos = db.query(func.count(Grupo.id)).filter(
        and_(
            Grupo.curso_id == curso_id,
            Grupo.estado.in_([EstadoGrupo.ABIERTO, EstadoGrupo.EN_CURSO])
        )
    ).scalar()
    
    from models.inscripcion import Inscripcion
    total_estudiantes = db.query(func.count(Inscripcion.estudiante_id.distinct())).join(
        Grupo
    ).filter(
        Grupo.curso_id == curso_id
    ).scalar()
    
    return {
        "total_grupos": total_grupos or 0,
        "grupos_activos": grupos_activos or 0,
        "total_estudiantes_historicos": total_estudiantes or 0
    }


def obtener_conteo_cursos_por_facultad(db: Session) -> List[Dict[str, Any]]:
    """
    Obtiene el conteo de cursos agrupados por facultad.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Lista de diccionarios con facultad_id, nombre_facultad y total_cursos
    
    Example:
        >>> conteo = obtener_conteo_cursos_por_facultad(db)
        >>> for item in conteo:
        ...     print(f"{item['nombre_facultad']}: {item['total_cursos']} cursos")
    """
    resultados = db.query(
        Facultad.id.label("facultad_id"),
        Facultad.nombre.label("nombre_facultad"),
        func.count(Curso.id).label("total_cursos")
    ).outerjoin(
        Curso, Curso.facultad_id == Facultad.id
    ).group_by(
        Facultad.id, Facultad.nombre
    ).all()
    
    return [
        {
            "facultad_id": r.facultad_id,
            "nombre_facultad": r.nombre_facultad,
            "total_cursos": r.total_cursos
        }
        for r in resultados
    ]
