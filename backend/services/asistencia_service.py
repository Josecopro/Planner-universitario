"""
Servicio de Asistencia
Lógica de negocio para gestión de asistencia de estudiantes
"""
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError

from models.asistencia import Asistencia, EstadoAsistencia
from models.inscripcion import Inscripcion
from models.grupo import Grupo


def registrar_asistencia_grupo(
    db: Session,
    grupo_id: int,
    fecha: date,
    asistencias: List[Dict[str, Any]]
) -> bool:
    """
    Registra la asistencia de múltiples estudiantes de un grupo en una fecha.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        fecha: Fecha de la asistencia
        asistencias: Lista de diccionarios con:
            - inscripcion_id: int (requerido)
            - estado: EstadoAsistencia (requerido)
    
    Returns:
        bool: True si se registraron todas las asistencias exitosamente
    
    Raises:
        ValueError: Si el grupo no existe o si hay errores en los datos
    """
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    
    if not grupo:
        raise ValueError(f"Grupo con ID {grupo_id} no encontrado")
    
    try:
        for asistencia_data in asistencias:
            inscripcion_id = asistencia_data["inscripcion_id"]
            estado = asistencia_data["estado"]
            
            asistencia_existente = db.query(Asistencia)\
                .filter(
                    and_(
                        Asistencia.inscripcion_id == inscripcion_id,
                        Asistencia.fecha == fecha
                    )
                )\
                .first()
            
            if asistencia_existente:
                asistencia_existente.estado = estado  # type: ignore
            else:
                nueva_asistencia = Asistencia(
                    inscripcion_id=inscripcion_id,
                    fecha=fecha,
                    estado=estado,
                    grupo_id=grupo_id
                )
                db.add(nueva_asistencia)
        
        db.commit()
        return True
        
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Error de integridad al registrar asistencias: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error al registrar asistencias: {str(e)}")


def obtener_asistencia_por_fecha(
    db: Session,
    grupo_id: int,
    fecha: date
) -> List[Asistencia]:
    """
    Obtiene todos los registros de asistencia de un grupo en una fecha específica.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        fecha: Fecha de la asistencia
    
    Returns:
        List[Asistencia]: Lista de registros de asistencia
    """
    return db.query(Asistencia)\
        .options(
            joinedload(Asistencia.inscripcion).joinedload(Inscripcion.estudiante)
        )\
        .filter(
            and_(
                Asistencia.grupo_id == grupo_id,
                Asistencia.fecha == fecha
            )
        )\
        .all()


def calcular_porcentaje_asistencia_inscripcion(
    db: Session,
    inscripcion_id: int
) -> float:
    """
    Calcula el porcentaje de asistencia de un estudiante en un grupo.
    
    Solo cuenta como asistencias positivas: PRESENTE y TARDANZA.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
    
    Returns:
        float: Porcentaje de asistencia (0.0 - 100.0)
    """
    total_registros = db.query(Asistencia)\
        .filter(Asistencia.inscripcion_id == inscripcion_id)\
        .count()
    
    if total_registros == 0:
        return 0.0
    
    asistencias_positivas = db.query(Asistencia)\
        .filter(
            and_(
                Asistencia.inscripcion_id == inscripcion_id,
                Asistencia.estado.in_([  # type: ignore
                    EstadoAsistencia.PRESENTE,
                    EstadoAsistencia.TARDANZA
                ])
            )
        )\
        .count()
    
    porcentaje = (asistencias_positivas / total_registros) * 100.0
    return round(porcentaje, 2)


def calcular_porcentaje_asistencia_grupo(
    db: Session,
    grupo_id: int
) -> float:
    """
    Calcula el porcentaje promedio de asistencia de todo un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        float: Porcentaje promedio de asistencia del grupo (0.0 - 100.0)
    """
    inscripciones = db.query(Inscripcion)\
        .filter(Inscripcion.grupo_id == grupo_id)\
        .all()
    
    if not inscripciones:
        return 0.0
    
    porcentajes = []
    for inscripcion in inscripciones:
        porcentaje = calcular_porcentaje_asistencia_inscripcion(db, inscripcion.id)  # type: ignore
        porcentajes.append(porcentaje)
    
    if porcentajes:
        return round(sum(porcentajes) / len(porcentajes), 2)
    
    return 0.0


def obtener_asistencia_por_id(
    db: Session,
    asistencia_id: int
) -> Optional[Asistencia]:
    """
    Obtiene un registro de asistencia por su ID.
    
    Args:
        db: Sesión de base de datos
        asistencia_id: ID de la asistencia
    
    Returns:
        Asistencia | None: El registro de asistencia o None si no existe
    """
    return db.query(Asistencia)\
        .options(
            joinedload(Asistencia.inscripcion),
            joinedload(Asistencia.grupo)
        )\
        .filter(Asistencia.id == asistencia_id)\
        .first()


def obtener_asistencias_por_inscripcion(
    db: Session,
    inscripcion_id: int,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None
) -> List[Asistencia]:
    """
    Obtiene todos los registros de asistencia de un estudiante.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
        fecha_inicio: Fecha inicial del rango (opcional)
        fecha_fin: Fecha final del rango (opcional)
    
    Returns:
        List[Asistencia]: Lista de registros de asistencia
    """
    query = db.query(Asistencia)\
        .filter(Asistencia.inscripcion_id == inscripcion_id)
    
    if fecha_inicio:
        query = query.filter(Asistencia.fecha >= fecha_inicio)  # type: ignore
    
    if fecha_fin:
        query = query.filter(Asistencia.fecha <= fecha_fin)  # type: ignore
    
    return query.order_by(Asistencia.fecha.desc()).all()


def obtener_asistencias_por_grupo(
    db: Session,
    grupo_id: int,
    fecha_inicio: Optional[date] = None,
    fecha_fin: Optional[date] = None
) -> List[Asistencia]:
    """
    Obtiene todos los registros de asistencia de un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        fecha_inicio: Fecha inicial del rango (opcional)
        fecha_fin: Fecha final del rango (opcional)
    
    Returns:
        List[Asistencia]: Lista de registros de asistencia
    """
    query = db.query(Asistencia)\
        .options(joinedload(Asistencia.inscripcion))\
        .filter(Asistencia.grupo_id == grupo_id)
    
    if fecha_inicio:
        query = query.filter(Asistencia.fecha >= fecha_inicio)  # type: ignore
    
    if fecha_fin:
        query = query.filter(Asistencia.fecha <= fecha_fin)  # type: ignore
    
    return query.order_by(Asistencia.fecha.desc()).all()


def actualizar_asistencia(
    db: Session,
    asistencia_id: int,
    nuevo_estado: EstadoAsistencia
) -> Optional[Asistencia]:
    """
    Actualiza el estado de un registro de asistencia.
    
    Args:
        db: Sesión de base de datos
        asistencia_id: ID de la asistencia
        nuevo_estado: Nuevo estado de asistencia
    
    Returns:
        Asistencia | None: El registro actualizado o None si no existe
    """
    asistencia = db.query(Asistencia)\
        .filter(Asistencia.id == asistencia_id)\
        .first()
    
    if not asistencia:
        return None
    
    asistencia.estado = nuevo_estado  # type: ignore
    db.commit()
    db.refresh(asistencia)
    
    return asistencia


def registrar_asistencia_individual(
    db: Session,
    inscripcion_id: int,
    fecha: date,
    estado: EstadoAsistencia,
    grupo_id: int
) -> Asistencia:
    """
    Registra la asistencia de un estudiante individual.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
        fecha: Fecha de la asistencia
        estado: Estado de asistencia
        grupo_id: ID del grupo
    
    Returns:
        Asistencia: El registro de asistencia creado o actualizado
    
    Raises:
        ValueError: Si la inscripción no existe
    """
    inscripcion = db.query(Inscripcion)\
        .filter(Inscripcion.id == inscripcion_id)\
        .first()
    
    if not inscripcion:
        raise ValueError(f"Inscripción con ID {inscripcion_id} no encontrada")
    
    asistencia_existente = db.query(Asistencia)\
        .filter(
            and_(
                Asistencia.inscripcion_id == inscripcion_id,
                Asistencia.fecha == fecha
            )
        )\
        .first()
    
    if asistencia_existente:
        asistencia_existente.estado = estado  # type: ignore
        db.commit()
        db.refresh(asistencia_existente)
        return asistencia_existente
    else:
        nueva_asistencia = Asistencia(
            inscripcion_id=inscripcion_id,
            fecha=fecha,
            estado=estado,
            grupo_id=grupo_id
        )
        
        try:
            db.add(nueva_asistencia)
            db.commit()
            db.refresh(nueva_asistencia)
            return nueva_asistencia
        except IntegrityError:
            db.rollback()
            raise ValueError("Error de integridad al registrar asistencia")


def obtener_fechas_asistencia_grupo(
    db: Session,
    grupo_id: int
) -> List[date]:
    """
    Obtiene todas las fechas en las que se ha tomado asistencia en un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        List[date]: Lista de fechas únicas ordenadas
    """
    fechas = db.query(Asistencia.fecha)\
        .filter(Asistencia.grupo_id == grupo_id)\
        .distinct()\
        .order_by(Asistencia.fecha.desc())\
        .all()
    
    return [f.fecha for f in fechas]


def contar_asistencias_por_estado(
    db: Session,
    inscripcion_id: int
) -> Dict[str, int]:
    """
    Cuenta las asistencias de un estudiante agrupadas por estado.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
    
    Returns:
        Dict: Diccionario con el conteo por estado
            - presentes: Número de asistencias PRESENTE
            - ausentes: Número de asistencias AUSENTE
            - justificados: Número de asistencias JUSTIFICADO
            - tardanzas: Número de asistencias TARDANZA
    """
    presentes = db.query(Asistencia)\
        .filter(
            and_(
                Asistencia.inscripcion_id == inscripcion_id,
                Asistencia.estado == EstadoAsistencia.PRESENTE
            )
        )\
        .count()
    
    ausentes = db.query(Asistencia)\
        .filter(
            and_(
                Asistencia.inscripcion_id == inscripcion_id,
                Asistencia.estado == EstadoAsistencia.AUSENTE
            )
        )\
        .count()
    
    justificados = db.query(Asistencia)\
        .filter(
            and_(
                Asistencia.inscripcion_id == inscripcion_id,
                Asistencia.estado == EstadoAsistencia.JUSTIFICADO
            )
        )\
        .count()
    
    tardanzas = db.query(Asistencia)\
        .filter(
            and_(
                Asistencia.inscripcion_id == inscripcion_id,
                Asistencia.estado == EstadoAsistencia.TARDANZA
            )
        )\
        .count()
    
    return {
        "presentes": presentes,
        "ausentes": ausentes,
        "justificados": justificados,
        "tardanzas": tardanzas
    }


def obtener_estadisticas_asistencia_grupo(
    db: Session,
    grupo_id: int,
    fecha: Optional[date] = None
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de asistencia para un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        fecha: Fecha específica (opcional, si no se proporciona calcula sobre todas las fechas)
    
    Returns:
        Dict: Diccionario con estadísticas
            - total_estudiantes: Total de estudiantes inscritos
            - total_registros: Total de registros de asistencia
            - presentes: Número de presentes
            - ausentes: Número de ausentes
            - justificados: Número de justificados
            - tardanzas: Número de tardanzas
            - porcentaje_asistencia: Porcentaje promedio de asistencia
    """
    query = db.query(Asistencia)\
        .filter(Asistencia.grupo_id == grupo_id)
    
    if fecha:
        query = query.filter(Asistencia.fecha == fecha)
    
    asistencias = query.all()
    
    total_estudiantes = db.query(Inscripcion)\
        .filter(Inscripcion.grupo_id == grupo_id)\
        .count()
    
    presentes = sum(1 for a in asistencias if a.estado == EstadoAsistencia.PRESENTE)  # type: ignore
    ausentes = sum(1 for a in asistencias if a.estado == EstadoAsistencia.AUSENTE)  # type: ignore
    justificados = sum(1 for a in asistencias if a.estado == EstadoAsistencia.JUSTIFICADO)  # type: ignore
    tardanzas = sum(1 for a in asistencias if a.estado == EstadoAsistencia.TARDANZA)  # type: ignore
    
    porcentaje_asistencia = calcular_porcentaje_asistencia_grupo(db, grupo_id)
    
    return {
        "total_estudiantes": total_estudiantes,
        "total_registros": len(asistencias),
        "presentes": presentes,
        "ausentes": ausentes,
        "justificados": justificados,
        "tardanzas": tardanzas,
        "porcentaje_asistencia": porcentaje_asistencia
    }


def eliminar_asistencia(
    db: Session,
    asistencia_id: int
) -> bool:
    """
    Elimina un registro de asistencia.
    
    Args:
        db: Sesión de base de datos
        asistencia_id: ID de la asistencia a eliminar
    
    Returns:
        bool: True si se eliminó, False si no se encontró
    """
    asistencia = db.query(Asistencia)\
        .filter(Asistencia.id == asistencia_id)\
        .first()
    
    if not asistencia:
        return False
    
    db.delete(asistencia)
    db.commit()
    
    return True


def asistencia_existe(
    db: Session,
    inscripcion_id: int,
    fecha: date
) -> bool:
    """
    Verifica si existe un registro de asistencia para un estudiante en una fecha.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
        fecha: Fecha a verificar
    
    Returns:
        bool: True si existe, False en caso contrario
    """
    return db.query(Asistencia)\
        .filter(
            and_(
                Asistencia.inscripcion_id == inscripcion_id,
                Asistencia.fecha == fecha
            )
        )\
        .first() is not None


def obtener_estudiantes_ausentes(
    db: Session,
    grupo_id: int,
    fecha: date
) -> List[Asistencia]:
    """
    Obtiene los estudiantes ausentes de un grupo en una fecha específica.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        fecha: Fecha a consultar
    
    Returns:
        List[Asistencia]: Lista de registros de asistencia con estado AUSENTE
    """
    return db.query(Asistencia)\
        .options(joinedload(Asistencia.inscripcion))\
        .filter(
            and_(
                Asistencia.grupo_id == grupo_id,
                Asistencia.fecha == fecha,
                Asistencia.estado == EstadoAsistencia.AUSENTE
            )
        )\
        .all()


def obtener_reporte_asistencia_estudiante(
    db: Session,
    inscripcion_id: int
) -> Dict[str, Any]:
    """
    Genera un reporte completo de asistencia para un estudiante.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
    
    Returns:
        Dict: Reporte completo con estadísticas y detalles
    """
    asistencias = obtener_asistencias_por_inscripcion(db, inscripcion_id)
    
    conteo_estados = contar_asistencias_por_estado(db, inscripcion_id)
    porcentaje = calcular_porcentaje_asistencia_inscripcion(db, inscripcion_id)
    
    return {
        "inscripcion_id": inscripcion_id,
        "total_registros": len(asistencias),
        "porcentaje_asistencia": porcentaje,
        "conteo_estados": conteo_estados,
        "asistencias": asistencias
    }
