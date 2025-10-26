"""
Servicio de Profesor

Este módulo contiene toda la lógica de negocio relacionada con los profesores.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, extract
from datetime import datetime, timedelta

from models.profesor import Profesor
from models.usuario import Usuario, EstadoUsuario
from models.facultad import Facultad
from models.grupo import Grupo, EstadoGrupo
from models.curso import Curso
from models.horario import Horario


def crear_perfil_profesor(
    db: Session,
    datos_profesor: Dict[str, Any]
) -> Profesor:
    """
    Crea un perfil de profesor para un usuario.
    
    Args:
        db: Sesión de base de datos
        datos_profesor: Diccionario con los datos del profesor
            - usuario_id (int): ID del usuario (requerido)
            - documento (str, opcional): Número de documento
            - tipo_documento (str, opcional): Tipo de documento
            - facultad_id (int, opcional): ID de la facultad
            - titulo_academico (str, opcional): Título académico
    
    Returns:
        Profesor: El perfil de profesor creado
    
    Raises:
        ValueError: Si el usuario no existe, ya tiene perfil de profesor,
                   no tiene rol de profesor, o la facultad no existe
    
    Example:
        >>> profesor = crear_perfil_profesor(db, {
        ...     "usuario_id": 5,
        ...     "documento": "1234567890",
        ...     "tipo_documento": "Cédula",
        ...     "facultad_id": 2,
        ...     "titulo_academico": "PhD en Ingeniería de Software"
        ... })
    """
    usuario_id = datos_profesor.get("usuario_id")
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise ValueError(f"El usuario con ID {usuario_id} no existe")
    
    if usuario.rol_id != 2: # type: ignore
        raise ValueError(f"El usuario {usuario.nombre_completo} no tiene rol de profesor")
    
    profesor_existente = db.query(Profesor).filter(
        Profesor.usuario_id == usuario_id
    ).first()
    if profesor_existente:
        raise ValueError(f"El usuario {usuario.nombre_completo} ya tiene un perfil de profesor")
    
    facultad_id = datos_profesor.get("facultad_id")
    if facultad_id:
        facultad = db.query(Facultad).filter(Facultad.id == facultad_id).first()
        if not facultad:
            raise ValueError(f"La facultad con ID {facultad_id} no existe")
    
    nuevo_profesor = Profesor(
        usuario_id=usuario_id,
        documento=datos_profesor.get("documento"),
        tipo_documento=datos_profesor.get("tipo_documento"),
        facultad_id=facultad_id,
        titulo_academico=datos_profesor.get("titulo_academico")
    )
    
    db.add(nuevo_profesor)
    db.commit()
    db.refresh(nuevo_profesor)
    
    return nuevo_profesor


def obtener_profesor_por_id(
    db: Session,
    profesor_id: int
) -> Optional[Profesor]:
    """
    Obtiene un profesor por su ID.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
    
    Returns:
        Profesor o None si no existe
    
    Example:
        >>> profesor = obtener_profesor_por_id(db, 1)
        >>> if profesor:
        ...     print(profesor.titulo_academico)
    """
    return db.query(Profesor).filter(Profesor.id == profesor_id).first()


def obtener_profesor_por_usuario_id(
    db: Session,
    usuario_id: int
) -> Optional[Profesor]:
    """
    Obtiene un profesor por el ID de su usuario.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
    
    Returns:
        Profesor o None si no existe
    
    Example:
        >>> profesor = obtener_profesor_por_usuario_id(db, 5)
    """
    return db.query(Profesor).filter(Profesor.usuario_id == usuario_id).first()


def listar_profesores(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    facultad_id: Optional[int] = None,
    busqueda: Optional[str] = None,
    solo_activos: bool = True
) -> List[Profesor]:
    """
    Lista profesores con filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar (paginación)
        limit: Número máximo de registros a retornar
        facultad_id: Filtrar por facultad (opcional)
        busqueda: Búsqueda por nombre, apellido o documento (opcional)
        solo_activos: Si True, solo retorna profesores con usuario activo
    
    Returns:
        Lista de profesores
    
    Example:
        >>> profesores = listar_profesores(db, facultad_id=2, skip=0, limit=20)
    """
    query = db.query(Profesor).join(Usuario)
    
    # Filtrar por facultad
    if facultad_id:
        query = query.filter(Profesor.facultad_id == facultad_id)
    
    # Filtrar solo activos
    if solo_activos:
        query = query.filter(Usuario.estado == EstadoUsuario.ACTIVO)
    
    # Búsqueda por texto
    if busqueda:
        busqueda_patron = f"%{busqueda}%"
        query = query.filter(
            or_(
                Usuario.nombre.ilike(busqueda_patron),
                Usuario.apellido.ilike(busqueda_patron),
                Profesor.documento.ilike(busqueda_patron),
                Profesor.titulo_academico.ilike(busqueda_patron)
            )
        )
    
    return query.offset(skip).limit(limit).all()


def contar_profesores(
    db: Session,
    facultad_id: Optional[int] = None,
    solo_activos: bool = True
) -> int:
    """
    Cuenta el total de profesores con filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        facultad_id: Filtrar por facultad (opcional)
        solo_activos: Si True, solo cuenta profesores con usuario activo
    
    Returns:
        Total de profesores
    
    Example:
        >>> total = contar_profesores(db, facultad_id=2)
    """
    query = db.query(func.count(Profesor.id)).join(Usuario)
    
    if facultad_id:
        query = query.filter(Profesor.facultad_id == facultad_id)
    
    if solo_activos:
        query = query.filter(Usuario.estado == EstadoUsuario.ACTIVO)
    
    return query.scalar()


def actualizar_profesor(
    db: Session,
    profesor_id: int,
    datos_actualizados: Dict[str, Any]
) -> Profesor:
    """
    Actualiza los datos de un profesor.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
        datos_actualizados: Diccionario con los campos a actualizar
    
    Returns:
        Profesor actualizado
    
    Raises:
        ValueError: Si el profesor no existe o la facultad no es válida
    
    Example:
        >>> profesor = actualizar_profesor(db, 1, {
        ...     "titulo_academico": "PhD en Computer Science"
        ... })
    """
    profesor = obtener_profesor_por_id(db, profesor_id)
    if not profesor:
        raise ValueError(f"El profesor con ID {profesor_id} no existe")
    
    if "facultad_id" in datos_actualizados and datos_actualizados["facultad_id"]:
        facultad = db.query(Facultad).filter(
            Facultad.id == datos_actualizados["facultad_id"]
        ).first()
        if not facultad:
            raise ValueError(
                f"La facultad con ID {datos_actualizados['facultad_id']} no existe"
            )
    
    campos_permitidos = [
        "documento",
        "tipo_documento",
        "facultad_id",
        "titulo_academico"
    ]
    
    for campo, valor in datos_actualizados.items():
        if campo in campos_permitidos:
            setattr(profesor, campo, valor)
    
    db.commit()
    db.refresh(profesor)
    
    return profesor


def eliminar_profesor(
    db: Session,
    profesor_id: int
) -> bool:
    """
    Elimina un profesor del sistema.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
    
    Returns:
        True si se eliminó, False si no existía
    
    Example:
        >>> eliminado = eliminar_profesor(db, 1)
    """
    profesor = obtener_profesor_por_id(db, profesor_id)
    if not profesor:
        return False
    
    db.delete(profesor)
    db.commit()
    
    return True


def obtener_perfil_completo_profesor(
    db: Session,
    profesor_id: int
) -> Optional[Dict[str, Any]]:
    """
    Obtiene el perfil completo de un profesor con toda la información relacionada.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
    
    Returns:
        Diccionario con los datos completos o None si no existe:
        - profesor: Modelo Profesor
        - usuario: Modelo Usuario asociado
        - facultad: Modelo Facultad (si tiene)
        - total_grupos: Total de grupos asignados
        - grupos_activos: Total de grupos en curso
        - total_estudiantes: Total de estudiantes actuales
    
    Example:
        >>> perfil = obtener_perfil_completo_profesor(db, 1)
        >>> print(f"Profesor: {perfil['usuario'].nombre_completo}")
        >>> print(f"Grupos activos: {perfil['grupos_activos']}")
    """
    profesor = db.query(Profesor).options(
        joinedload(Profesor.usuario),
        joinedload(Profesor.facultad)
    ).filter(Profesor.id == profesor_id).first()
    
    if not profesor:
        return None
    
    total_grupos = db.query(func.count(Grupo.id)).filter(
        Grupo.profesor_id == profesor_id
    ).scalar()
    
    grupos_activos = db.query(func.count(Grupo.id)).filter(
        and_(
            Grupo.profesor_id == profesor_id,
            Grupo.estado.in_([EstadoGrupo.ABIERTO, EstadoGrupo.EN_CURSO])
        )
    ).scalar()
    
    from models.inscripcion import Inscripcion, EstadoInscripcion
    total_estudiantes = db.query(func.count(Inscripcion.id.distinct())).join(
        Grupo
    ).filter(
        and_(
            Grupo.profesor_id == profesor_id,
            Grupo.estado.in_([EstadoGrupo.ABIERTO, EstadoGrupo.EN_CURSO]),
            Inscripcion.estado == EstadoInscripcion.APROBADO
        )
    ).scalar()
    
    return {
        "profesor": profesor,
        "usuario": profesor.usuario,
        "facultad": profesor.facultad,
        "total_grupos": total_grupos or 0,
        "grupos_activos": grupos_activos or 0,
        "total_estudiantes": total_estudiantes or 0
    }


def actualizar_datos_profesor(
    db: Session,
    profesor_id: int,
    datos_actualizacion: Dict[str, Any]
) -> Profesor:
    """
    Actualiza solo los datos específicos del profesor (no del usuario).
    
    Esta función permite actualizar campos como título académico,
    pero NO modifica datos del usuario asociado (nombre, email, etc.).
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
        datos_actualizacion: Diccionario con los campos a actualizar
    
    Returns:
        Profesor actualizado
    
    Raises:
        ValueError: Si el profesor no existe
    
    Example:
        >>> profesor = actualizar_datos_profesor(db, 1, {
        ...     "titulo_academico": "PhD en Inteligencia Artificial"
        ... })
    """
    return actualizar_profesor(db, profesor_id, datos_actualizacion)


def obtener_grupos_asignados(
    db: Session,
    profesor_id: int,
    semestre: Optional[str] = None,
    estado: Optional[EstadoGrupo] = None
) -> List[Grupo]:
    """
    Obtiene los grupos asignados a un profesor.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
        semestre: Filtrar por semestre (ej: "2024-1", "2024-2")
        estado: Filtrar por estado del grupo
    
    Returns:
        Lista de grupos con sus datos relacionados (curso, horarios)
    
    Example:
        >>> grupos = obtener_grupos_asignados(db, 1, semestre="2024-2")
        >>> for grupo in grupos:
        ...     print(f"{grupo.curso.nombre} - Grupo {grupo.numero_grupo}")
    """
    query = db.query(Grupo).options(
        joinedload(Grupo.curso),
        joinedload(Grupo.horarios)
    ).filter(Grupo.profesor_id == profesor_id)
    
    if semestre:
        query = query.filter(Grupo.semestre == semestre)
    
    if estado:
        query = query.filter(Grupo.estado == estado)
    
    return query.order_by(Grupo.semestre.desc(), Grupo.numero_grupo).all() # type: ignore


def obtener_grupos_activos(
    db: Session,
    profesor_id: int
) -> List[Grupo]:
    """
    Obtiene los grupos activos (en curso o abiertos) de un profesor.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
    
    Returns:
        Lista de grupos activos
    
    Example:
        >>> grupos_activos = obtener_grupos_activos(db, 1)
    """
    return db.query(Grupo).options(
        joinedload(Grupo.curso),
        joinedload(Grupo.horarios)
    ).filter(
        and_(
            Grupo.profesor_id == profesor_id,
            Grupo.estado.in_([EstadoGrupo.ABIERTO, EstadoGrupo.EN_CURSO])
        )
    ).all()


def obtener_carga_academica(
    db: Session,
    profesor_id: int,
    semestre: str
) -> Dict[str, Any]:
    """
    Obtiene la carga académica completa de un profesor en un semestre.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
        semestre: Semestre a consultar (ej: "2024-2")
    
    Returns:
        Diccionario con información de la carga:
        - grupos: Lista de grupos
        - total_grupos: Total de grupos
        - total_estudiantes: Total de estudiantes en todos los grupos
        - total_horas_semanales: Total de horas de clase por semana
        - cursos: Lista única de cursos que dicta
    
    Example:
        >>> carga = obtener_carga_academica(db, 1, "2024-2")
        >>> print(f"Grupos: {carga['total_grupos']}")
        >>> print(f"Horas semanales: {carga['total_horas_semanales']}")
    """
    grupos = db.query(Grupo).options(
        joinedload(Grupo.curso),
        joinedload(Grupo.horarios)
    ).filter(
        and_(
            Grupo.profesor_id == profesor_id,
            Grupo.semestre == semestre
        )
    ).all()
    
    from models.inscripcion import Inscripcion, EstadoInscripcion
    total_estudiantes = 0
    for grupo in grupos:
        estudiantes_grupo = db.query(func.count(Inscripcion.id)).filter(
            and_(
                Inscripcion.grupo_id == grupo.id,
                Inscripcion.estado == EstadoInscripcion.APROBADO
            )
        ).scalar()
        total_estudiantes += estudiantes_grupo or 0
    
    total_horas = 0
    for grupo in grupos:
        for horario in grupo.horarios:
            if horario.hora_inicio and horario.hora_fin:
                duracion = datetime.combine(datetime.today(), horario.hora_fin) - \
                          datetime.combine(datetime.today(), horario.hora_inicio)
                total_horas += duracion.total_seconds() / 3600
    
    cursos_unicos = list({grupo.curso for grupo in grupos})
    
    return {
        "grupos": grupos,
        "total_grupos": len(grupos),
        "total_estudiantes": total_estudiantes,
        "total_horas_semanales": round(total_horas, 2),
        "cursos": cursos_unicos
    }


def obtener_estadisticas_profesor(
    db: Session,
    profesor_id: int
) -> Dict[str, Any]:
    """
    Obtiene estadísticas generales de un profesor.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
    
    Returns:
        Diccionario con estadísticas:
        - total_grupos_dictados: Total histórico de grupos
        - grupos_activos: Grupos actuales
        - total_estudiantes_actuales: Estudiantes en grupos activos
        - semestres_activo: Cantidad de semestres en que ha dictado
    
    Example:
        >>> stats = obtener_estadisticas_profesor(db, 1)
        >>> print(f"Ha dictado {stats['total_grupos_dictados']} grupos")
    """
    # Total de grupos históricos
    total_grupos = db.query(func.count(Grupo.id)).filter(
        Grupo.profesor_id == profesor_id
    ).scalar()
    
    # Grupos activos
    grupos_activos = db.query(func.count(Grupo.id)).filter(
        and_(
            Grupo.profesor_id == profesor_id,
            Grupo.estado.in_([EstadoGrupo.ABIERTO, EstadoGrupo.EN_CURSO])
        )
    ).scalar()
    
    # Estudiantes actuales
    from models.inscripcion import Inscripcion, EstadoInscripcion
    estudiantes_actuales = db.query(func.count(Inscripcion.id.distinct())).join(
        Grupo
    ).filter(
        and_(
            Grupo.profesor_id == profesor_id,
            Grupo.estado.in_([EstadoGrupo.ABIERTO, EstadoGrupo.EN_CURSO]),
            Inscripcion.estado == EstadoInscripcion.APROBADO
        )
    ).scalar()
    
    # Semestres en los que ha estado activo
    semestres = db.query(func.count(Grupo.semestre.distinct())).filter(
        Grupo.profesor_id == profesor_id
    ).scalar()
    
    return {
        "total_grupos_dictados": total_grupos or 0,
        "grupos_activos": grupos_activos or 0,
        "total_estudiantes_actuales": estudiantes_actuales or 0,
        "semestres_activo": semestres or 0
    }


def obtener_profesores_por_facultad(
    db: Session,
    facultad_id: int,
    solo_activos: bool = True
) -> List[Profesor]:
    """
    Obtiene todos los profesores de una facultad.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad
        solo_activos: Si True, solo retorna profesores activos
    
    Returns:
        Lista de profesores de la facultad
    
    Example:
        >>> profesores = obtener_profesores_por_facultad(db, 2)
    """
    query = db.query(Profesor).join(Usuario).filter(
        Profesor.facultad_id == facultad_id
    )
    
    if solo_activos:
        query = query.filter(Usuario.estado == EstadoUsuario.ACTIVO)
    
    return query.all()


def buscar_profesores(
    db: Session,
    termino: str,
    limit: int = 10
) -> List[Profesor]:
    """
    Busca profesores por nombre, apellido, documento o título.
    
    Args:
        db: Sesión de base de datos
        termino: Término de búsqueda
        limit: Máximo de resultados
    
    Returns:
        Lista de profesores que coinciden
    
    Example:
        >>> resultados = buscar_profesores(db, "garcía")
    """
    patron = f"%{termino}%"
    
    return db.query(Profesor).join(Usuario).filter(
        or_(
            Usuario.nombre.ilike(patron),
            Usuario.apellido.ilike(patron),
            Profesor.documento.ilike(patron),
            Profesor.titulo_academico.ilike(patron)
        )
    ).limit(limit).all()


def profesor_existe(
    db: Session,
    profesor_id: int
) -> bool:
    """
    Verifica si existe un profesor con el ID dado.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
    
    Returns:
        True si existe, False en caso contrario
    
    Example:
        >>> if profesor_existe(db, 1):
        ...     print("El profesor existe")
    """
    return db.query(Profesor).filter(Profesor.id == profesor_id).first() is not None


def usuario_tiene_perfil_profesor(
    db: Session,
    usuario_id: int
) -> bool:
    """
    Verifica si un usuario tiene perfil de profesor.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
    
    Returns:
        True si tiene perfil, False en caso contrario
    
    Example:
        >>> if usuario_tiene_perfil_profesor(db, 5):
        ...     print("Este usuario es profesor")
    """
    return db.query(Profesor).filter(
        Profesor.usuario_id == usuario_id
    ).first() is not None


def profesor_puede_dictar_curso(
    db: Session,
    profesor_id: int,
    curso_id: int
) -> tuple[bool, str]:
    """
    Verifica si un profesor puede dictar un curso específico.
    
    Valida que:
    - El profesor existe y está activo
    - El curso existe
    - El profesor pertenece a la misma facultad del programa del curso (opcional)
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
        curso_id: ID del curso
    
    Returns:
        Tupla (puede_dictar, mensaje)
    
    Example:
        >>> puede, msg = profesor_puede_dictar_curso(db, 1, 5)
        >>> if puede:
        ...     print("Puede dictar el curso")
    """
    profesor = obtener_profesor_por_id(db, profesor_id)
    if not profesor:
        return False, "El profesor no existe"
    
    if profesor.usuario.estado != EstadoUsuario.ACTIVO:
        return False, "El profesor no está activo"
    
    curso = db.query(Curso).filter(Curso.id == curso_id).first()
    if not curso:
        return False, "El curso no existe"
    
    return True, "El profesor puede dictar el curso"
