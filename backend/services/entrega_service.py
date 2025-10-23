"""
Servicio de Entrega
Lógica de negocio para gestión de entregas de actividades evaluativas
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from models.entrega import Entrega, EstadoEntrega
from models.actividad_evaluativa import ActividadEvaluativa, EstadoActividad
from models.inscripcion import Inscripcion


def realizar_entrega(
    db: Session,
    datos_entrega: Dict[str, Any]
) -> Entrega:
    """
    Registra la entrega de un estudiante para una actividad evaluativa.
    
    Args:
        db: Sesión de base de datos
        datos_entrega: Diccionario con los datos de la entrega
            - actividad_id: int (requerido)
            - inscripcion_id: int (requerido)
            - texto_entrega: str (opcional)
            - archivos_adjuntos: List[str] (opcional)
            - fecha_entrega: datetime (opcional, default: now)
    
    Returns:
        Entrega: La entrega creada
    
    Raises:
        ValueError: Si la actividad o inscripción no existen, si ya existe
                   una entrega, o si la actividad no acepta entregas
        IntegrityError: Si se viola la constraint de unicidad
    """
    actividad_id = datos_entrega["actividad_id"]
    inscripcion_id = datos_entrega["inscripcion_id"]
    
    actividad = db.query(ActividadEvaluativa)\
        .filter(ActividadEvaluativa.id == actividad_id)\
        .first()
    
    if not actividad:
        raise ValueError(f"Actividad con ID {actividad_id} no encontrada")
    
    inscripcion = db.query(Inscripcion)\
        .filter(Inscripcion.id == inscripcion_id)\
        .first()
    
    if not inscripcion:
        raise ValueError(f"Inscripción con ID {inscripcion_id} no encontrada")
    
    entrega_existente = db.query(Entrega)\
        .filter(
            and_(
                Entrega.actividad_id == actividad_id,
                Entrega.inscripcion_id == inscripcion_id
            )
        )\
        .first()
    
    if entrega_existente:
        raise ValueError(
            f"Ya existe una entrega para esta actividad por parte del estudiante"
        )
    
    fecha_entrega = datos_entrega.get("fecha_entrega", datetime.now())
    
    if fecha_entrega > actividad.fecha_entrega:  # type: ignore
        estado = EstadoEntrega.ENTREGADA_TARDE
    else:
        estado = EstadoEntrega.ENTREGADA
    
    nueva_entrega = Entrega(
        actividad_id=actividad_id,
        inscripcion_id=inscripcion_id,
        fecha_entrega=fecha_entrega,
        estado=estado,
        texto_entrega=datos_entrega.get("texto_entrega"),
        archivos_adjuntos=datos_entrega.get("archivos_adjuntos")
    )
    
    try:
        db.add(nueva_entrega)
        db.commit()
        db.refresh(nueva_entrega)
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Error de integridad: Ya existe una entrega para esta actividad y estudiante"
        )
    
    return nueva_entrega


def obtener_entrega_de_estudiante(
    db: Session,
    actividad_id: int,
    inscripcion_id: int
) -> Optional[Entrega]:
    """
    Obtiene la entrega de un estudiante específico para una actividad.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
        inscripcion_id: ID de la inscripción del estudiante
    
    Returns:
        Entrega | None: La entrega del estudiante o None si no existe
    """
    return db.query(Entrega)\
        .options(
            joinedload(Entrega.actividad),
            joinedload(Entrega.inscripcion),
            joinedload(Entrega.calificacion)
        )\
        .filter(
            and_(
                Entrega.actividad_id == actividad_id,
                Entrega.inscripcion_id == inscripcion_id
            )
        )\
        .first()


def obtener_entregas_pendientes_por_calificar(
    db: Session,
    grupo_id: int
) -> List[Entrega]:
    """
    Obtiene todas las entregas de un grupo que están pendientes de calificación.
    
    Args:
        db: Session de base de datos
        grupo_id: ID del grupo
    
    Returns:
        List[Entrega]: Lista de entregas en estado ENTREGADA o ENTREGADA_TARDE
                       que no tienen calificación asociada
    """
    from models.calificacion import Calificacion
    
    entregas = db.query(Entrega)\
        .join(ActividadEvaluativa, Entrega.actividad_id == ActividadEvaluativa.id)\
        .outerjoin(Calificacion, Entrega.id == Calificacion.entrega_id)\
        .filter(
            and_(
                ActividadEvaluativa.grupo_id == grupo_id,
                Entrega.estado.in_([  # type: ignore
                    EstadoEntrega.ENTREGADA,
                    EstadoEntrega.ENTREGADA_TARDE
                ]),
                Calificacion.id == None  # type: ignore
            )
        )\
        .options(
            joinedload(Entrega.actividad),
            joinedload(Entrega.inscripcion)
        )\
        .all()
    
    return entregas


def actualizar_entrega(
    db: Session,
    datos_actualizacion: Dict[str, Any]
) -> Optional[Entrega]:
    """
    Actualiza los datos de una entrega existente.
    
    Args:
        db: Sesión de base de datos
        datos_actualizacion: Diccionario con los campos a actualizar
            Debe incluir el ID de la entrega y los campos a modificar:
            - entrega_id: int (requerido)
            - texto_entrega: str (opcional)
            - archivos_adjuntos: List[str] (opcional)
            - estado: EstadoEntrega (opcional)
    
    Returns:
        Entrega | None: La entrega actualizada o None si no existe
    
    Raises:
        ValueError: Si no se proporciona entrega_id
    """
    if "entrega_id" not in datos_actualizacion:
        raise ValueError("Se requiere el ID de la entrega para actualizarla")
    
    entrega_id = datos_actualizacion["entrega_id"]
    
    entrega = db.query(Entrega)\
        .filter(Entrega.id == entrega_id)\
        .first()
    
    if not entrega:
        return None
    
    campos_permitidos = ["texto_entrega", "archivos_adjuntos", "estado"]
    
    for campo, valor in datos_actualizacion.items():
        if campo in campos_permitidos and hasattr(entrega, campo):
            setattr(entrega, campo, valor)
    
    db.commit()
    db.refresh(entrega)
    
    return entrega


def marcar_como_calificada(
    db: Session,
    entrega_id: int
) -> Optional[Entrega]:
    """
    Marca una entrega como calificada.
    
    Args:
        db: Sesión de base de datos
        entrega_id: ID de la entrega
    
    Returns:
        Entrega | None: La entrega actualizada o None si no existe
    """
    entrega = db.query(Entrega)\
        .filter(Entrega.id == entrega_id)\
        .first()
    
    if not entrega:
        return None
    
    entrega.estado = EstadoEntrega.CALIFICADA  # type: ignore
    db.commit()
    db.refresh(entrega)
    
    return entrega


def obtener_entrega_para_calificar(
    db: Session,
    entrega_id: int
) -> Optional[Entrega]:
    """
    Obtiene una entrega con todas sus relaciones para el proceso de calificación.
    
    Args:
        db: Sesión de base de datos
        entrega_id: ID de la entrega
    
    Returns:
        Entrega | None: La entrega con actividad, inscripción y calificación cargadas
    """
    return db.query(Entrega)\
        .options(
            joinedload(Entrega.actividad),
            joinedload(Entrega.inscripcion).joinedload(Inscripcion.estudiante),
            joinedload(Entrega.calificacion)
        )\
        .filter(Entrega.id == entrega_id)\
        .first()


def obtener_entregas_por_actividad(
    db: Session,
    actividad_id: int
) -> List[Entrega]:
    """
    Obtiene todas las entregas de una actividad específica.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        List[Entrega]: Lista de entregas de la actividad
    """
    return db.query(Entrega)\
        .options(
            joinedload(Entrega.inscripcion).joinedload(Inscripcion.estudiante),
            joinedload(Entrega.calificacion)
        )\
        .filter(Entrega.actividad_id == actividad_id)\
        .order_by(Entrega.fecha_entrega)\
        .all()


def obtener_entregas_por_estado(
    db: Session,
    actividad_id: int,
    estado: EstadoEntrega
) -> List[Entrega]:
    """
    Obtiene entregas de una actividad filtradas por estado.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
        estado: Estado de la entrega a filtrar
    
    Returns:
        List[Entrega]: Lista de entregas con el estado especificado
    """
    return db.query(Entrega)\
        .filter(
            and_(
                Entrega.actividad_id == actividad_id,
                Entrega.estado == estado
            )
        )\
        .options(joinedload(Entrega.inscripcion))\
        .order_by(Entrega.fecha_entrega)\
        .all()


def obtener_entregas_tardias(
    db: Session,
    actividad_id: int
) -> List[Entrega]:
    """
    Obtiene las entregas tardías de una actividad.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        List[Entrega]: Lista de entregas con estado ENTREGADA_TARDE
    """
    return obtener_entregas_por_estado(
        db, 
        actividad_id, 
        EstadoEntrega.ENTREGADA_TARDE
    )


def entrega_existe(
    db: Session,
    actividad_id: int,
    inscripcion_id: int
) -> bool:
    """
    Verifica si existe una entrega para una actividad y estudiante específicos.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
        inscripcion_id: ID de la inscripción del estudiante
    
    Returns:
        bool: True si existe la entrega, False en caso contrario
    """
    return db.query(Entrega)\
        .filter(
            and_(
                Entrega.actividad_id == actividad_id,
                Entrega.inscripcion_id == inscripcion_id
            )
        )\
        .first() is not None


def obtener_entrega_por_id(
    db: Session,
    entrega_id: int
) -> Optional[Entrega]:
    """
    Obtiene una entrega por su ID con todas sus relaciones.
    
    Args:
        db: Sesión de base de datos
        entrega_id: ID de la entrega
    
    Returns:
        Entrega | None: La entrega o None si no existe
    """
    return db.query(Entrega)\
        .options(
            joinedload(Entrega.actividad),
            joinedload(Entrega.inscripcion).joinedload(Inscripcion.estudiante),
            joinedload(Entrega.calificacion)
        )\
        .filter(Entrega.id == entrega_id)\
        .first()


def contar_entregas_por_actividad(
    db: Session,
    actividad_id: int,
    estado: Optional[EstadoEntrega] = None
) -> int:
    """
    Cuenta el número de entregas de una actividad, opcionalmente por estado.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
        estado: Estado para filtrar (opcional)
    
    Returns:
        int: Número de entregas
    """
    query = db.query(Entrega)\
        .filter(Entrega.actividad_id == actividad_id)
    
    if estado:
        query = query.filter(Entrega.estado == estado)
    
    return query.count()


def obtener_entregas_de_estudiante(
    db: Session,
    inscripcion_id: int
) -> List[Entrega]:
    """
    Obtiene todas las entregas de un estudiante en un grupo.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción del estudiante
    
    Returns:
        List[Entrega]: Lista de entregas del estudiante
    """
    return db.query(Entrega)\
        .options(
            joinedload(Entrega.actividad),
            joinedload(Entrega.calificacion)
        )\
        .filter(Entrega.inscripcion_id == inscripcion_id)\
        .order_by(Entrega.fecha_entrega.desc())\
        .all()


def estudiante_ha_entregado(
    db: Session,
    actividad_id: int,
    inscripcion_id: int
) -> bool:
    """
    Verifica si un estudiante ha realizado la entrega de una actividad.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
        inscripcion_id: ID de la inscripción del estudiante
    
    Returns:
        bool: True si el estudiante ya entregó, False en caso contrario
    """
    return entrega_existe(db, actividad_id, inscripcion_id)


def obtener_estadisticas_entregas(
    db: Session,
    actividad_id: int
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de entregas para una actividad.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        Dict: Diccionario con estadísticas
            - total_entregas: Total de entregas
            - entregas_a_tiempo: Entregas con estado ENTREGADA
            - entregas_tardias: Entregas con estado ENTREGADA_TARDE
            - entregas_calificadas: Entregas con estado CALIFICADA
            - entregas_pendientes: Entregas sin calificar (ENTREGADA + ENTREGADA_TARDE)
            - estudiantes_sin_entregar: Estudiantes inscritos que no han entregado
    """
    actividad = db.query(ActividadEvaluativa)\
        .filter(ActividadEvaluativa.id == actividad_id)\
        .first()
    
    if not actividad:
        return {
            "total_entregas": 0,
            "entregas_a_tiempo": 0,
            "entregas_tardias": 0,
            "entregas_calificadas": 0,
            "entregas_pendientes": 0,
            "estudiantes_sin_entregar": 0
        }
    
    total_entregas = contar_entregas_por_actividad(db, actividad_id)
    entregas_a_tiempo = contar_entregas_por_actividad(
        db, actividad_id, EstadoEntrega.ENTREGADA
    )
    entregas_tardias = contar_entregas_por_actividad(
        db, actividad_id, EstadoEntrega.ENTREGADA_TARDE
    )
    entregas_calificadas = contar_entregas_por_actividad(
        db, actividad_id, EstadoEntrega.CALIFICADA
    )
    
    entregas_pendientes = entregas_a_tiempo + entregas_tardias
    
    total_estudiantes = db.query(Inscripcion)\
        .filter(Inscripcion.grupo_id == actividad.grupo_id)\
        .count()
    
    estudiantes_sin_entregar = total_estudiantes - total_entregas
    
    return {
        "total_entregas": total_entregas,
        "entregas_a_tiempo": entregas_a_tiempo,
        "entregas_tardias": entregas_tardias,
        "entregas_calificadas": entregas_calificadas,
        "entregas_pendientes": entregas_pendientes,
        "estudiantes_sin_entregar": estudiantes_sin_entregar
    }


def eliminar_entrega(
    db: Session,
    entrega_id: int
) -> bool:
    """
    Elimina una entrega.
    
    Args:
        db: Sesión de base de datos
        entrega_id: ID de la entrega a eliminar
    
    Returns:
        bool: True si se eliminó, False si no se encontró
    """
    entrega = db.query(Entrega)\
        .filter(Entrega.id == entrega_id)\
        .first()
    
    if not entrega:
        return False
    
    db.delete(entrega)
    db.commit()
    
    return True
