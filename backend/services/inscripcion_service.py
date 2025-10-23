"""
Servicio de Inscripción
Lógica de negocio para gestión de inscripciones de estudiantes en grupos
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from models.inscripcion import Inscripcion, EstadoInscripcion
from models.estudiante import Estudiante
from models.grupo import Grupo, EstadoGrupo


def inscribir_estudiante(
    db: Session,
    datos_inscripcion: Dict[str, Any]
) -> Inscripcion:
    """
    Inscribe un estudiante en un grupo.
    
    Args:
        db: Sesión de base de datos
        datos_inscripcion: Diccionario con los datos de inscripción
            - estudiante_id: int (requerido)
            - grupo_id: int (requerido)
            - fecha_inscripcion: datetime (opcional, default: now)
    
    Returns:
        Inscripcion: La inscripción creada
    
    Raises:
        ValueError: Si el estudiante o grupo no existen, si ya está inscrito,
                   o si el grupo no acepta inscripciones
        IntegrityError: Si se viola la constraint de unicidad
    """
    estudiante_id = datos_inscripcion["estudiante_id"]
    grupo_id = datos_inscripcion["grupo_id"]
    
    estudiante = db.query(Estudiante)\
        .filter(Estudiante.id == estudiante_id)\
        .first()
    
    if not estudiante:
        raise ValueError(f"Estudiante con ID {estudiante_id} no encontrado")
    
    grupo = db.query(Grupo)\
        .filter(Grupo.id == grupo_id)\
        .first()
    
    if not grupo:
        raise ValueError(f"Grupo con ID {grupo_id} no encontrado")
    
    if grupo.estado not in [EstadoGrupo.PROGRAMADO, EstadoGrupo.ABIERTO]:  # type: ignore
        raise ValueError(
            f"El grupo no acepta inscripciones. Estado actual: {grupo.estado.value}"
        )
    
    if grupo.cupo_actual >= grupo.cupo_maximo:  # type: ignore
        raise ValueError("El grupo no tiene cupos disponibles")
    
    inscripcion_existente = db.query(Inscripcion)\
        .filter(
            and_(
                Inscripcion.estudiante_id == estudiante_id,
                Inscripcion.grupo_id == grupo_id
            )
        )\
        .first()
    
    if inscripcion_existente:
        raise ValueError(
            f"El estudiante ya está inscrito en este grupo"
        )
    
    nueva_inscripcion = Inscripcion(
        estudiante_id=estudiante_id,
        grupo_id=grupo_id,
        fecha_inscripcion=datos_inscripcion.get("fecha_inscripcion", datetime.now()),
        estado=EstadoInscripcion.INSCRITO
    )
    
    try:
        db.add(nueva_inscripcion)
        
        grupo.cupo_actual = grupo.cupo_actual + 1  # type: ignore
        
        db.commit()
        db.refresh(nueva_inscripcion)
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Error de integridad: El estudiante ya está inscrito en este grupo"
        )
    
    return nueva_inscripcion


def retirar_estudiante(
    db: Session,
    inscripcion_id: int
) -> Inscripcion:
    """
    Retira un estudiante de un grupo cambiando el estado de la inscripción.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
    
    Returns:
        Inscripcion: La inscripción actualizada con estado RETIRADO
    
    Raises:
        ValueError: Si la inscripción no existe o ya está retirada/cancelada
    """
    inscripcion = db.query(Inscripcion)\
        .options(joinedload(Inscripcion.grupo))\
        .filter(Inscripcion.id == inscripcion_id)\
        .first()
    
    if not inscripcion:
        raise ValueError(f"Inscripción con ID {inscripcion_id} no encontrada")
    
    if inscripcion.estado in [EstadoInscripcion.RETIRADO, EstadoInscripcion.CANCELADO]:  # type: ignore
        raise ValueError(
            f"La inscripción ya está en estado {inscripcion.estado.value}"
        )
    
    inscripcion.estado = EstadoInscripcion.RETIRADO  # type: ignore
    
    grupo = inscripcion.grupo
    if grupo.cupo_actual > 0:  # type: ignore
        grupo.cupo_actual = grupo.cupo_actual - 1  # type: ignore
    
    db.commit()
    db.refresh(inscripcion)
    
    return inscripcion


def obtener_grupos_inscritos(
    db: Session,
    estudiante_id: int,
    semestre: Optional[str] = None
) -> List[Grupo]:
    """
    Obtiene los grupos en los que está inscrito un estudiante.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
        semestre: Filtrar por semestre (opcional)
    
    Returns:
        List[Grupo]: Lista de grupos en los que está inscrito el estudiante
    """
    query = db.query(Grupo)\
        .join(Inscripcion, Inscripcion.grupo_id == Grupo.id)\
        .filter(
            and_(
                Inscripcion.estudiante_id == estudiante_id,
                Inscripcion.estado == EstadoInscripcion.INSCRITO
            )
        )\
        .options(
            joinedload(Grupo.curso),
            joinedload(Grupo.profesor)
        )
    
    if semestre:
        query = query.filter(Grupo.semestre == semestre)
    
    return query.all()


def obtener_inscripciones_por_estudiante(
    db: Session,
    estudiante_id: int,
    semestre: Optional[str] = None
) -> List[Inscripcion]:
    """
    Obtiene todas las inscripciones de un estudiante.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
        semestre: Filtrar por semestre (opcional)
    
    Returns:
        List[Inscripcion]: Lista de inscripciones del estudiante
    """
    query = db.query(Inscripcion)\
        .options(
            joinedload(Inscripcion.grupo).joinedload(Grupo.curso),
            joinedload(Inscripcion.grupo).joinedload(Grupo.profesor)
        )\
        .filter(Inscripcion.estudiante_id == estudiante_id)
    
    if semestre:
        query = query.join(Grupo, Inscripcion.grupo_id == Grupo.id)\
            .filter(Grupo.semestre == semestre)
    
    return query.order_by(Inscripcion.fecha_inscripcion.desc()).all()


def cerrar_inscripcion(
    db: Session,
    inscripcion_id: int
) -> Inscripcion:
    """
    Cierra una inscripción cambiando su estado (APROBADO o REPROBADO).
    Este método NO se usa directamente. Se usa cambiar_estado_inscripcion.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
    
    Returns:
        Inscripcion: La inscripción cerrada
    
    Raises:
        ValueError: Si la inscripción no existe
    """
    inscripcion = db.query(Inscripcion)\
        .filter(Inscripcion.id == inscripcion_id)\
        .first()
    
    if not inscripcion:
        raise ValueError(f"Inscripción con ID {inscripcion_id} no encontrada")
    
    if inscripcion.nota_definitiva is not None:
        if float(inscripcion.nota_definitiva) >= 3.0:  # type: ignore
            inscripcion.estado = EstadoInscripcion.APROBADO  # type: ignore
        else:
            inscripcion.estado = EstadoInscripcion.REPROBADO  # type: ignore
    
    db.commit()
    db.refresh(inscripcion)
    
    return inscripcion


def obtener_inscripcion_por_id(
    db: Session,
    inscripcion_id: int
) -> Optional[Inscripcion]:
    """
    Obtiene una inscripción por su ID con todas sus relaciones.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
    
    Returns:
        Inscripcion | None: La inscripción o None si no existe
    """
    return db.query(Inscripcion)\
        .options(
            joinedload(Inscripcion.estudiante),
            joinedload(Inscripcion.grupo).joinedload(Grupo.curso),
            joinedload(Inscripcion.grupo).joinedload(Grupo.profesor),
            joinedload(Inscripcion.entregas),
            joinedload(Inscripcion.asistencias)
        )\
        .filter(Inscripcion.id == inscripcion_id)\
        .first()


def obtener_inscripciones_por_grupo(
    db: Session,
    grupo_id: int,
    estado: Optional[EstadoInscripcion] = None
) -> List[Inscripcion]:
    """
    Obtiene todas las inscripciones de un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        estado: Filtrar por estado (opcional)
    
    Returns:
        List[Inscripcion]: Lista de inscripciones del grupo
    """
    query = db.query(Inscripcion)\
        .options(joinedload(Inscripcion.estudiante))\
        .filter(Inscripcion.grupo_id == grupo_id)
    
    if estado:
        query = query.filter(Inscripcion.estado == estado)
    
    return query.order_by(Inscripcion.fecha_inscripcion).all()


def estudiante_inscrito_en_grupo(
    db: Session,
    estudiante_id: int,
    grupo_id: int
) -> bool:
    """
    Verifica si un estudiante está inscrito en un grupo específico.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
        grupo_id: ID del grupo
    
    Returns:
        bool: True si está inscrito (estado INSCRITO), False en caso contrario
    """
    inscripcion = db.query(Inscripcion)\
        .filter(
            and_(
                Inscripcion.estudiante_id == estudiante_id,
                Inscripcion.grupo_id == grupo_id,
                Inscripcion.estado == EstadoInscripcion.INSCRITO
            )
        )\
        .first()
    
    return inscripcion is not None


def obtener_inscripcion_estudiante_grupo(
    db: Session,
    estudiante_id: int,
    grupo_id: int
) -> Optional[Inscripcion]:
    """
    Obtiene la inscripción de un estudiante en un grupo específico.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
        grupo_id: ID del grupo
    
    Returns:
        Inscripcion | None: La inscripción o None si no existe
    """
    return db.query(Inscripcion)\
        .filter(
            and_(
                Inscripcion.estudiante_id == estudiante_id,
                Inscripcion.grupo_id == grupo_id
            )
        )\
        .first()


def actualizar_nota_definitiva(
    db: Session,
    inscripcion_id: int,
    nota_definitiva: float
) -> Optional[Inscripcion]:
    """
    Actualiza la nota definitiva de una inscripción.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
        nota_definitiva: Nota final del estudiante
    
    Returns:
        Inscripcion | None: La inscripción actualizada o None si no existe
    
    Raises:
        ValueError: Si la nota es negativa
    """
    if nota_definitiva < 0.0:
        raise ValueError("La nota definitiva no puede ser negativa")
    
    inscripcion = db.query(Inscripcion)\
        .filter(Inscripcion.id == inscripcion_id)\
        .first()
    
    if not inscripcion:
        return None
    
    inscripcion.nota_definitiva = nota_definitiva  # type: ignore
    
    if nota_definitiva >= 3.0:
        inscripcion.estado = EstadoInscripcion.APROBADO  # type: ignore
    else:
        inscripcion.estado = EstadoInscripcion.REPROBADO  # type: ignore
    
    db.commit()
    db.refresh(inscripcion)
    
    return inscripcion


def cambiar_estado_inscripcion(
    db: Session,
    inscripcion_id: int,
    nuevo_estado: EstadoInscripcion
) -> Optional[Inscripcion]:
    """
    Cambia el estado de una inscripción.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
        nuevo_estado: Nuevo estado para la inscripción
    
    Returns:
        Inscripcion | None: La inscripción actualizada o None si no existe
    """
    inscripcion = db.query(Inscripcion)\
        .options(joinedload(Inscripcion.grupo))\
        .filter(Inscripcion.id == inscripcion_id)\
        .first()
    
    if not inscripcion:
        return None
    
    estado_anterior = inscripcion.estado
    inscripcion.estado = nuevo_estado  # type: ignore
    
    if estado_anterior == EstadoInscripcion.INSCRITO and \
       nuevo_estado in [EstadoInscripcion.RETIRADO, EstadoInscripcion.CANCELADO]:  # type: ignore
        grupo = inscripcion.grupo
        if grupo.cupo_actual > 0:  # type: ignore
            grupo.cupo_actual = grupo.cupo_actual - 1  # type: ignore
    
    if estado_anterior in [EstadoInscripcion.RETIRADO, EstadoInscripcion.CANCELADO] and \
       nuevo_estado == EstadoInscripcion.INSCRITO:  # type: ignore
        grupo = inscripcion.grupo
        if grupo.cupo_actual < grupo.cupo_maximo:  # type: ignore
            grupo.cupo_actual = grupo.cupo_actual + 1  # type: ignore
    
    db.commit()
    db.refresh(inscripcion)
    
    return inscripcion


def contar_inscripciones_por_grupo(
    db: Session,
    grupo_id: int,
    estado: Optional[EstadoInscripcion] = None
) -> int:
    """
    Cuenta el número de inscripciones de un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        estado: Filtrar por estado (opcional)
    
    Returns:
        int: Número de inscripciones
    """
    query = db.query(Inscripcion)\
        .filter(Inscripcion.grupo_id == grupo_id)
    
    if estado:
        query = query.filter(Inscripcion.estado == estado)
    
    return query.count()


def contar_inscripciones_por_estudiante(
    db: Session,
    estudiante_id: int,
    semestre: Optional[str] = None
) -> int:
    """
    Cuenta el número de inscripciones de un estudiante.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
        semestre: Filtrar por semestre (opcional)
    
    Returns:
        int: Número de inscripciones
    """
    query = db.query(Inscripcion)\
        .filter(Inscripcion.estudiante_id == estudiante_id)
    
    if semestre:
        query = query.join(Grupo, Inscripcion.grupo_id == Grupo.id)\
            .filter(Grupo.semestre == semestre)
    
    return query.count()


def obtener_estudiantes_inscritos(
    db: Session,
    grupo_id: int
) -> List[Estudiante]:
    """
    Obtiene la lista de estudiantes inscritos en un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        List[Estudiante]: Lista de estudiantes activamente inscritos
    """
    return db.query(Estudiante)\
        .join(Inscripcion, Inscripcion.estudiante_id == Estudiante.id)\
        .filter(
            and_(
                Inscripcion.grupo_id == grupo_id,
                Inscripcion.estado == EstadoInscripcion.INSCRITO
            )
        )\
        .all()


def obtener_estadisticas_inscripcion(
    db: Session,
    grupo_id: int
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de inscripciones para un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        Dict: Diccionario con estadísticas
            - total_inscripciones: Total de inscripciones
            - inscritos: Estudiantes actualmente inscritos
            - retirados: Estudiantes que se retiraron
            - aprobados: Estudiantes aprobados
            - reprobados: Estudiantes reprobados
            - cancelados: Inscripciones canceladas
            - cupos_disponibles: Cupos restantes
    """
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    
    if not grupo:
        return {
            "total_inscripciones": 0,
            "inscritos": 0,
            "retirados": 0,
            "aprobados": 0,
            "reprobados": 0,
            "cancelados": 0,
            "cupos_disponibles": 0
        }
    
    total_inscripciones = contar_inscripciones_por_grupo(db, grupo_id)
    inscritos = contar_inscripciones_por_grupo(db, grupo_id, EstadoInscripcion.INSCRITO)
    retirados = contar_inscripciones_por_grupo(db, grupo_id, EstadoInscripcion.RETIRADO)
    aprobados = contar_inscripciones_por_grupo(db, grupo_id, EstadoInscripcion.APROBADO)
    reprobados = contar_inscripciones_por_grupo(db, grupo_id, EstadoInscripcion.REPROBADO)
    cancelados = contar_inscripciones_por_grupo(db, grupo_id, EstadoInscripcion.CANCELADO)
    
    cupos_disponibles = int(grupo.cupo_maximo - grupo.cupo_actual)  # type: ignore
    
    return {
        "total_inscripciones": total_inscripciones,
        "inscritos": inscritos,
        "retirados": retirados,
        "aprobados": aprobados,
        "reprobados": reprobados,
        "cancelados": cancelados,
        "cupos_disponibles": cupos_disponibles
    }


def inscripcion_existe(
    db: Session,
    inscripcion_id: int
) -> bool:
    """
    Verifica si una inscripción existe.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
    
    Returns:
        bool: True si existe, False en caso contrario
    """
    return db.query(Inscripcion)\
        .filter(Inscripcion.id == inscripcion_id)\
        .first() is not None


def eliminar_inscripcion(
    db: Session,
    inscripcion_id: int
) -> bool:
    """
    Elimina una inscripción de la base de datos.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
    
    Returns:
        bool: True si se eliminó, False si no se encontró
    """
    inscripcion = db.query(Inscripcion)\
        .options(joinedload(Inscripcion.grupo))\
        .filter(Inscripcion.id == inscripcion_id)\
        .first()
    
    if not inscripcion:
        return False
    
    if inscripcion.estado == EstadoInscripcion.INSCRITO:  # type: ignore
        grupo = inscripcion.grupo
        if grupo.cupo_actual > 0:  # type: ignore
            grupo.cupo_actual = grupo.cupo_actual - 1  # type: ignore
    
    db.delete(inscripcion)
    db.commit()
    
    return True
