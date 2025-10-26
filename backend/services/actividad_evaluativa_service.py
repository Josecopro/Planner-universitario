"""
Servicio de Actividad Evaluativa
Lógica de negocio para gestión de actividades evaluativas (tareas, exámenes, etc.)
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from models.actividad_evaluativa import (
    ActividadEvaluativa,
    EstadoActividad,
    TipoActividad,
    PrioridadActividad
)
from models.grupo import Grupo
from utils.datetime_utils import obtener_datetime_actual, es_fecha_pasada
from utils.validators import validar_porcentaje, validar_tipo_actividad, validar_prioridad
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from models.actividad_evaluativa import (
    ActividadEvaluativa,
    EstadoActividad,
    TipoActividad,
    PrioridadActividad
)
from models.grupo import Grupo
from models.entrega import Entrega


def crear_actividad(
    db: Session,
    grupo_id: int,
    datos_actividad: Dict[str, Any]
) -> ActividadEvaluativa:
    """
    Crea una nueva actividad evaluativa para un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo al que pertenece la actividad
        datos_actividad: Diccionario con los datos de la actividad
            - titulo: str (requerido)
            - descripcion: str (opcional)
            - fecha_entrega: datetime (requerido)
            - tipo: TipoActividad (opcional, default TAREA)
            - prioridad: PrioridadActividad (opcional, default MEDIA)
            - porcentaje: float (opcional, default 0.0)
            - estado: EstadoActividad (opcional, default PROGRAMADA)
    
    Returns:
        ActividadEvaluativa: La actividad creada
    
    Raises:
        ValueError: Si el grupo no existe o los datos son inválidos
    """
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise ValueError(f"Grupo con ID {grupo_id} no encontrado")
    
    porcentaje = datos_actividad.get("porcentaje", 0.0)
    if not validar_porcentaje(porcentaje):
        raise ValueError("El porcentaje debe estar entre 0.0 y 100.0")
    
    nueva_actividad = ActividadEvaluativa(
        grupo_id=grupo_id,
        titulo=datos_actividad["titulo"],
        descripcion=datos_actividad.get("descripcion"),
        fecha_entrega=datos_actividad["fecha_entrega"],
        tipo=datos_actividad.get("tipo", TipoActividad.TAREA),
        prioridad=datos_actividad.get("prioridad", PrioridadActividad.MEDIA),
        porcentaje=porcentaje,
        estado=datos_actividad.get("estado", EstadoActividad.PROGRAMADA)
    )
    
    db.add(nueva_actividad)
    db.commit()
    db.refresh(nueva_actividad)
    
    return nueva_actividad


def obtener_actividades_por_grupo(
    db: Session,
    grupo_id: int
) -> List[ActividadEvaluativa]:
    """
    Obtiene todas las actividades de un grupo específico.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        List[ActividadEvaluativa]: Lista de actividades del grupo
    """
    return db.query(ActividadEvaluativa)\
        .filter(ActividadEvaluativa.grupo_id == grupo_id)\
        .order_by(ActividadEvaluativa.fecha_entrega)\
        .all()


def eliminar_actividad(
    db: Session,
    actividad_id: int
) -> bool:
    """
    Elimina una actividad evaluativa.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad a eliminar
    
    Returns:
        bool: True si se eliminó, False si no se encontró
    """
    actividad = db.query(ActividadEvaluativa)\
        .filter(ActividadEvaluativa.id == actividad_id)\
        .first()
    
    if not actividad:
        return False
    
    db.delete(actividad)
    db.commit()
    
    return True


def actualizar_actividad(
    db: Session,
    actividad_id: int,
    datos_actualizacion: Dict[str, Any]
) -> Optional[ActividadEvaluativa]:
    """
    Actualiza los datos de una actividad evaluativa.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad a actualizar
        datos_actualizacion: Diccionario con los campos a actualizar
            Campos permitidos: titulo, descripcion, fecha_entrega, tipo, 
            prioridad, porcentaje, estado
    
    Returns:
        ActividadEvaluativa | None: La actividad actualizada o None si no existe
    
    Raises:
        ValueError: Si los datos de actualización son inválidos
    """
    actividad = db.query(ActividadEvaluativa)\
        .filter(ActividadEvaluativa.id == actividad_id)\
        .first()
    
    if not actividad:
        return None
    
    if "porcentaje" in datos_actualizacion:
        porcentaje = datos_actualizacion["porcentaje"]
        if not validar_porcentaje(porcentaje):
            raise ValueError("El porcentaje debe estar entre 0.0 y 100.0")
    
    campos_permitidos = [
        "titulo", "descripcion", "fecha_entrega", 
        "tipo", "prioridad", "porcentaje", "estado"
    ]
    
    for campo, valor in datos_actualizacion.items():
        if campo in campos_permitidos and hasattr(actividad, campo):
            setattr(actividad, campo, valor)
    
    db.commit()
    db.refresh(actividad)
    
    return actividad


def obtener_actividad_por_id(
    db: Session,
    actividad_id: int
) -> Optional[ActividadEvaluativa]:
    """
    Obtiene una actividad por su ID con todas sus relaciones cargadas.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        ActividadEvaluativa | None: La actividad o None si no existe
    """
    return db.query(ActividadEvaluativa)\
        .options(
            joinedload(ActividadEvaluativa.grupo),
            joinedload(ActividadEvaluativa.entregas)
        )\
        .filter(ActividadEvaluativa.id == actividad_id)\
        .first()


def obtener_actividades_filtradas(
    db: Session,
    grupo_id: int,
    estado: Optional[EstadoActividad] = None,
    prioridad: Optional[PrioridadActividad] = None,
    fecha: Optional[datetime] = None
) -> List[ActividadEvaluativa]:
    """
    Obtiene actividades filtradas por múltiples criterios.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        estado: Filtrar por estado (opcional)
        prioridad: Filtrar por prioridad (opcional)
        fecha: Filtrar actividades con fecha_entrega >= fecha (opcional)
    
    Returns:
        List[ActividadEvaluativa]: Lista de actividades que cumplen los criterios
    """
    query = db.query(ActividadEvaluativa)\
        .filter(ActividadEvaluativa.grupo_id == grupo_id)
    
    if estado:
        query = query.filter(ActividadEvaluativa.estado == estado)
    
    if prioridad:
        query = query.filter(ActividadEvaluativa.prioridad == prioridad)
    
    if fecha:
        query = query.filter(ActividadEvaluativa.fecha_entrega >= fecha)  # type: ignore
    
    return query.order_by(ActividadEvaluativa.fecha_entrega).all()


def obtener_actividades_pendientes_grupo(
    db: Session,
    grupo_id: int,
    fecha_limite: Optional[datetime] = None
) -> List[ActividadEvaluativa]:
    """
    Obtiene las actividades pendientes (PROGRAMADA, PUBLICADA, ABIERTA) de un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        fecha_limite: Fecha límite para filtrar (opcional)
    
    Returns:
        List[ActividadEvaluativa]: Lista de actividades pendientes
    """
    estados_pendientes = [
        EstadoActividad.PROGRAMADA,
        EstadoActividad.PUBLICADA,
        EstadoActividad.ABIERTA
    ]
    
    query = db.query(ActividadEvaluativa)\
        .filter(
            and_(
                ActividadEvaluativa.grupo_id == grupo_id,
                ActividadEvaluativa.estado.in_(estados_pendientes)  # type: ignore
            )
        )
    
    if fecha_limite:
        query = query.filter(ActividadEvaluativa.fecha_entrega <= fecha_limite)  # type: ignore
    
    return query.order_by(ActividadEvaluativa.fecha_entrega).all()


def obtener_actividades_por_tipo(
    db: Session,
    grupo_id: int,
    tipo: TipoActividad
) -> List[ActividadEvaluativa]:
    """
    Obtiene todas las actividades de un tipo específico en un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        tipo: Tipo de actividad (TAREA, QUIZ, EXAMEN_PARCIAL, etc.)
    
    Returns:
        List[ActividadEvaluativa]: Lista de actividades del tipo especificado
    """
    return db.query(ActividadEvaluativa)\
        .filter(
            and_(
                ActividadEvaluativa.grupo_id == grupo_id,
                ActividadEvaluativa.tipo == tipo
            )
        )\
        .order_by(ActividadEvaluativa.fecha_entrega)\
        .all()


def obtener_actividades_proximas(
    db: Session,
    grupo_id: int,
    dias: int = 7
) -> List[ActividadEvaluativa]:
    """
    Obtiene actividades que vencen en los próximos N días.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        dias: Número de días hacia adelante (default: 7)
    
    Returns:
        List[ActividadEvaluativa]: Lista de actividades próximas a vencer
    """
    from datetime import timedelta
    
    fecha_actual = obtener_datetime_actual()
    fecha_limite = fecha_actual + timedelta(days=dias)
    
    estados_activos = [
        EstadoActividad.PUBLICADA,
        EstadoActividad.ABIERTA
    ]
    
    return db.query(ActividadEvaluativa)\
        .filter(
            and_(
                ActividadEvaluativa.grupo_id == grupo_id,
                ActividadEvaluativa.estado.in_(estados_activos),  # type: ignore
                ActividadEvaluativa.fecha_entrega >= fecha_actual,  # type: ignore
                ActividadEvaluativa.fecha_entrega <= fecha_limite  # type: ignore
            )
        )\
        .order_by(ActividadEvaluativa.fecha_entrega)\
        .all()


def cambiar_estado_actividad(
    db: Session,
    actividad_id: int,
    nuevo_estado: EstadoActividad
) -> Optional[ActividadEvaluativa]:
    """
    Cambia el estado de una actividad.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
        nuevo_estado: Nuevo estado para la actividad
    
    Returns:
        ActividadEvaluativa | None: La actividad actualizada o None si no existe
    """
    actividad = db.query(ActividadEvaluativa)\
        .filter(ActividadEvaluativa.id == actividad_id)\
        .first()
    
    if not actividad:
        return None
    
    actividad.estado = nuevo_estado  # type: ignore
    db.commit()
    db.refresh(actividad)
    
    return actividad


def actividad_existe(
    db: Session,
    actividad_id: int
) -> bool:
    """
    Verifica si una actividad existe.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        bool: True si existe, False en caso contrario
    """
    return db.query(ActividadEvaluativa)\
        .filter(ActividadEvaluativa.id == actividad_id)\
        .first() is not None


def obtener_porcentaje_total_grupo(
    db: Session,
    grupo_id: int
) -> float:
    """
    Calcula el porcentaje total asignado a todas las actividades de un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        float: Suma de todos los porcentajes de las actividades del grupo
    """
    from sqlalchemy import func
    
    resultado = db.query(func.sum(ActividadEvaluativa.porcentaje))\
        .filter(ActividadEvaluativa.grupo_id == grupo_id)\
        .scalar()
    
    return float(resultado) if resultado else 0.0


def actividad_esta_vencida(
    db: Session,
    actividad_id: int
) -> bool:
    """
    Verifica si una actividad ya venció (fecha_entrega pasada).
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        bool: True si está vencida, False en caso contrario o si no existe
    """
    actividad = db.query(ActividadEvaluativa)\
        .filter(ActividadEvaluativa.id == actividad_id)\
        .first()
    
    if not actividad:
        return False
    
    return es_fecha_pasada(actividad.fecha_entrega)  # type: ignore


def obtener_actividades_por_prioridad(
    db: Session,
    grupo_id: int,
    prioridad: PrioridadActividad
) -> List[ActividadEvaluativa]:
    """
    Obtiene actividades de un grupo filtradas por prioridad.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        prioridad: Prioridad a filtrar (BAJA, MEDIA, ALTA)
    
    Returns:
        List[ActividadEvaluativa]: Lista de actividades con la prioridad especificada
    """
    return db.query(ActividadEvaluativa)\
        .filter(
            and_(
                ActividadEvaluativa.grupo_id == grupo_id,
                ActividadEvaluativa.prioridad == prioridad
            )
        )\
        .order_by(ActividadEvaluativa.fecha_entrega)\
        .all()


def contar_entregas_actividad(
    db: Session,
    actividad_id: int
) -> int:
    """
    Cuenta el número de entregas realizadas para una actividad.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        int: Número de entregas
    """
    return db.query(Entrega)\
        .filter(Entrega.actividad_id == actividad_id)\
        .count()


def obtener_estadisticas_actividad(
    db: Session,
    actividad_id: int
) -> Optional[Dict[str, Any]]:
    """
    Obtiene estadísticas detalladas de una actividad.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        Dict | None: Diccionario con estadísticas o None si no existe
            - actividad: Objeto ActividadEvaluativa
            - total_entregas: Número de entregas
            - estudiantes_inscritos: Total de estudiantes en el grupo
            - porcentaje_entrega: Porcentaje de estudiantes que entregaron
            - esta_vencida: Boolean indicando si ya pasó la fecha límite
    """
    actividad = obtener_actividad_por_id(db, actividad_id)
    
    if not actividad:
        return None
    
    total_entregas = contar_entregas_actividad(db, actividad_id)
    
    from models.inscripcion import Inscripcion
    estudiantes_inscritos = db.query(Inscripcion)\
        .filter(Inscripcion.grupo_id == actividad.grupo_id)\
        .count()
    
    porcentaje_entrega = 0.0
    if estudiantes_inscritos > 0:
        porcentaje_entrega = (total_entregas / estudiantes_inscritos) * 100
    
    esta_vencida = es_fecha_pasada(actividad.fecha_entrega)  # type: ignore
    
    return {
        "actividad": actividad,
        "total_entregas": total_entregas,
        "estudiantes_inscritos": estudiantes_inscritos,
        "porcentaje_entrega": round(porcentaje_entrega, 2),
        "esta_vencida": esta_vencida
    }
