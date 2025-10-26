"""
Servicio de Calificación
Lógica de negocio para gestión de calificaciones y cálculo de promedios
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from models.calificacion import Calificacion
from models.entrega import Entrega
from models.actividad_evaluativa import ActividadEvaluativa
from models.inscripcion import Inscripcion
from utils.datetime_utils import obtener_datetime_actual
from utils.validators import validar_nota
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from models.calificacion import Calificacion
from models.entrega import Entrega, EstadoEntrega
from models.inscripcion import Inscripcion
from models.actividad_evaluativa import ActividadEvaluativa


def crear_calificacion(
    db: Session,
    datos_calificacion: Dict[str, Any]
) -> Calificacion:
    """
    Crea una calificación para una entrega.
    
    Args:
        db: Sesión de base de datos
        datos_calificacion: Diccionario con los datos de la calificación
            - entrega_id: int (requerido)
            - nota_obtenida: float (requerido)
            - retroalimentacion: str (opcional)
            - fecha_calificacion: datetime (opcional, default: now)
    
    Returns:
        Calificacion: La calificación creada
    
    Raises:
        ValueError: Si la entrega no existe, ya está calificada, o la nota es inválida
        IntegrityError: Si se viola la constraint de unicidad
    """
    entrega_id = datos_calificacion["entrega_id"]
    nota_obtenida = datos_calificacion["nota_obtenida"]
    
    if nota_obtenida < 0.0:
        raise ValueError("La nota obtenida no puede ser negativa")
    
    entrega = db.query(Entrega)\
        .filter(Entrega.id == entrega_id)\
        .first()
    
    if not entrega:
        raise ValueError(f"Entrega con ID {entrega_id} no encontrada")
    
    calificacion_existente = db.query(Calificacion)\
        .filter(Calificacion.entrega_id == entrega_id)\
        .first()
    
    if calificacion_existente:
        raise ValueError(
            f"Ya existe una calificación para esta entrega. Use actualizar_calificacion en su lugar."
        )
    
    nueva_calificacion = Calificacion(
        entrega_id=entrega_id,
        nota_obtenida=nota_obtenida,
        retroalimentacion=datos_calificacion.get("retroalimentacion"),
        fecha_calificacion=datos_calificacion.get("fecha_calificacion", obtener_datetime_actual())
    )
    
    try:
        db.add(nueva_calificacion)
        
        entrega.estado = EstadoEntrega.CALIFICADA  # type: ignore
        
        db.commit()
        db.refresh(nueva_calificacion)
    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Error de integridad: Ya existe una calificación para esta entrega"
        )
    
    return nueva_calificacion


def actualizar_calificacion(
    db: Session,
    calificacion_id: int,
    datos_actualizacion: Dict[str, Any]
) -> Optional[Calificacion]:
    """
    Actualiza una calificación existente.
    
    Args:
        db: Sesión de base de datos
        calificacion_id: ID de la calificación a actualizar
        datos_actualizacion: Diccionario con los campos a actualizar
            - nota_obtenida: float (opcional)
            - retroalimentacion: str (opcional)
            - fecha_calificacion: datetime (opcional)
    
    Returns:
        Calificacion | None: La calificación actualizada o None si no existe
    
    Raises:
        ValueError: Si la nota es inválida
    """
    calificacion = db.query(Calificacion)\
        .filter(Calificacion.id == calificacion_id)\
        .first()
    
    if not calificacion:
        return None
    
    if "nota_obtenida" in datos_actualizacion:
        nota = datos_actualizacion["nota_obtenida"]
        if nota < 0.0:
            raise ValueError("La nota obtenida no puede ser negativa")
        calificacion.nota_obtenida = nota  # type: ignore
    
    if "retroalimentacion" in datos_actualizacion:
        calificacion.retroalimentacion = datos_actualizacion["retroalimentacion"]  # type: ignore
    
    if "fecha_calificacion" in datos_actualizacion:
        calificacion.fecha_calificacion = datos_actualizacion["fecha_calificacion"]  # type: ignore
    
    db.commit()
    db.refresh(calificacion)
    
    return calificacion


def obtener_calificaciones_de_actividad(
    db: Session,
    actividad_id: int
) -> List[Calificacion]:
    """
    Obtiene todas las calificaciones de una actividad evaluativa.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        List[Calificacion]: Lista de calificaciones de la actividad
    """
    return db.query(Calificacion)\
        .join(Entrega, Calificacion.entrega_id == Entrega.id)\
        .filter(Entrega.actividad_id == actividad_id)\
        .options(
            joinedload(Calificacion.entrega)
        )\
        .order_by(Calificacion.fecha_calificacion.desc())\
        .all()


def obtener_calificaciones_de_estudiante(
    db: Session,
    inscripcion_id: int
) -> List[Calificacion]:
    """
    Obtiene todas las calificaciones de un estudiante en un grupo.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción del estudiante
    
    Returns:
        List[Calificacion]: Lista de calificaciones del estudiante
    """
    return db.query(Calificacion)\
        .join(Entrega, Calificacion.entrega_id == Entrega.id)\
        .filter(Entrega.inscripcion_id == inscripcion_id)\
        .options(
            joinedload(Calificacion.entrega)
        )\
        .order_by(Calificacion.fecha_calificacion.desc())\
        .all()


def calcular_nota_definitiva(
    db: Session,
    inscripcion_id: int
) -> float:
    """
    Calcula la nota definitiva de un estudiante en un grupo.
    
    Calcula el promedio ponderado de todas las calificaciones del estudiante
    en las actividades del grupo, considerando el porcentaje de cada actividad.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción del estudiante
    
    Returns:
        float: Nota definitiva calculada (promedio ponderado)
    """
    calificaciones = db.query(Calificacion, ActividadEvaluativa)\
        .join(Entrega, Calificacion.entrega_id == Entrega.id)\
        .join(ActividadEvaluativa, Entrega.actividad_id == ActividadEvaluativa.id)\
        .filter(Entrega.inscripcion_id == inscripcion_id)\
        .all()
    
    if not calificaciones:
        return 0.0
    
    suma_ponderada = 0.0
    suma_porcentajes = 0.0
    
    for calificacion, actividad in calificaciones:
        peso = float(actividad.porcentaje) / 100.0
        suma_ponderada += float(calificacion.nota_obtenida) * peso
        suma_porcentajes += peso
    
    if suma_porcentajes == 0.0:
        return sum(float(c.nota_obtenida) for c, _ in calificaciones) / len(calificaciones)
    
    return suma_ponderada / suma_porcentajes if suma_porcentajes > 0 else 0.0


def obtener_calificacion_por_id(
    db: Session,
    calificacion_id: int
) -> Optional[Calificacion]:
    """
    Obtiene una calificación por su ID con todas sus relaciones.
    
    Args:
        db: Sesión de base de datos
        calificacion_id: ID de la calificación
    
    Returns:
        Calificacion | None: La calificación o None si no existe
    """
    return db.query(Calificacion)\
        .options(
            joinedload(Calificacion.entrega)
        )\
        .filter(Calificacion.id == calificacion_id)\
        .first()


def obtener_calificacion_por_entrega(
    db: Session,
    entrega_id: int
) -> Optional[Calificacion]:
    """
    Obtiene la calificación de una entrega específica.
    
    Args:
        db: Sesión de base de datos
        entrega_id: ID de la entrega
    
    Returns:
        Calificacion | None: La calificación de la entrega o None si no existe
    """
    return db.query(Calificacion)\
        .filter(Calificacion.entrega_id == entrega_id)\
        .first()


def entrega_esta_calificada(
    db: Session,
    entrega_id: int
) -> bool:
    """
    Verifica si una entrega ya ha sido calificada.
    
    Args:
        db: Sesión de base de datos
        entrega_id: ID de la entrega
    
    Returns:
        bool: True si existe calificación, False en caso contrario
    """
    return db.query(Calificacion)\
        .filter(Calificacion.entrega_id == entrega_id)\
        .first() is not None


def obtener_estadisticas_calificaciones(
    db: Session,
    actividad_id: int
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de calificaciones para una actividad.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        Dict: Diccionario con estadísticas
            - total_calificaciones: Total de entregas calificadas
            - nota_promedio: Promedio de las notas
            - nota_maxima: Nota más alta
            - nota_minima: Nota más baja
            - estudiantes_aprobados: Número de estudiantes con nota >= 3.0
            - estudiantes_reprobados: Número de estudiantes con nota < 3.0
    """
    calificaciones = db.query(Calificacion.nota_obtenida)\
        .join(Entrega, Calificacion.entrega_id == Entrega.id)\
        .filter(Entrega.actividad_id == actividad_id)\
        .all()
    
    if not calificaciones:
        return {
            "total_calificaciones": 0,
            "nota_promedio": 0.0,
            "nota_maxima": 0.0,
            "nota_minima": 0.0,
            "estudiantes_aprobados": 0,
            "estudiantes_reprobados": 0
        }
    
    notas = [float(c.nota_obtenida) for c in calificaciones]
    
    return {
        "total_calificaciones": len(notas),
        "nota_promedio": round(sum(notas) / len(notas), 2),
        "nota_maxima": max(notas),
        "nota_minima": min(notas),
        "estudiantes_aprobados": sum(1 for n in notas if n >= 3.0),
        "estudiantes_reprobados": sum(1 for n in notas if n < 3.0)
    }


def eliminar_calificacion(
    db: Session,
    calificacion_id: int
) -> bool:
    """
    Elimina una calificación.
    
    Args:
        db: Sesión de base de datos
        calificacion_id: ID de la calificación a eliminar
    
    Returns:
        bool: True si se eliminó, False si no se encontró
    """
    calificacion = db.query(Calificacion)\
        .options(joinedload(Calificacion.entrega))\
        .filter(Calificacion.id == calificacion_id)\
        .first()
    
    if not calificacion:
        return False
    
    entrega = calificacion.entrega
    if entrega:
        actividad = db.query(ActividadEvaluativa)\
            .filter(ActividadEvaluativa.id == Entrega.actividad_id)\
            .first()
        
        if actividad and entrega.fecha_entrega > actividad.fecha_entrega:  # type: ignore
            entrega.estado = EstadoEntrega.ENTREGADA_TARDE  # type: ignore
        else:
            entrega.estado = EstadoEntrega.ENTREGADA  # type: ignore
    
    db.delete(calificacion)
    db.commit()
    
    return True


def calificacion_existe(
    db: Session,
    calificacion_id: int
) -> bool:
    """
    Verifica si una calificación existe.
    
    Args:
        db: Sesión de base de datos
        calificacion_id: ID de la calificación
    
    Returns:
        bool: True si existe, False en caso contrario
    """
    return db.query(Calificacion)\
        .filter(Calificacion.id == calificacion_id)\
        .first() is not None


def obtener_promedio_estudiante_en_grupo(
    db: Session,
    inscripcion_id: int
) -> float:
    """
    Obtiene el promedio simple de las calificaciones de un estudiante.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
    
    Returns:
        float: Promedio simple de las notas
    """
    resultado = db.query(func.avg(Calificacion.nota_obtenida))\
        .join(Entrega, Calificacion.entrega_id == Entrega.id)\
        .filter(Entrega.inscripcion_id == inscripcion_id)\
        .scalar()
    
    return float(resultado) if resultado else 0.0


def contar_calificaciones_por_actividad(
    db: Session,
    actividad_id: int
) -> int:
    """
    Cuenta el número de calificaciones para una actividad.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
    
    Returns:
        int: Número de calificaciones
    """
    return db.query(Calificacion)\
        .join(Entrega, Calificacion.entrega_id == Entrega.id)\
        .filter(Entrega.actividad_id == actividad_id)\
        .count()


def obtener_mejores_calificaciones(
    db: Session,
    actividad_id: int,
    limite: int = 10
) -> List[Calificacion]:
    """
    Obtiene las mejores calificaciones de una actividad.
    
    Args:
        db: Sesión de base de datos
        actividad_id: ID de la actividad
        limite: Número máximo de calificaciones a retornar
    
    Returns:
        List[Calificacion]: Lista de calificaciones ordenadas de mayor a menor
    """
    return db.query(Calificacion)\
        .join(Entrega, Calificacion.entrega_id == Entrega.id)\
        .filter(Entrega.actividad_id == actividad_id)\
        .options(
            joinedload(Calificacion.entrega)
        )\
        .order_by(Calificacion.nota_obtenida.desc())\
        .limit(limite)\
        .all()


def actualizar_nota_definitiva_inscripcion(
    db: Session,
    inscripcion_id: int
) -> Optional[float]:
    """
    Calcula y actualiza la nota definitiva en el registro de inscripción.
    
    Args:
        db: Sesión de base de datos
        inscripcion_id: ID de la inscripción
    
    Returns:
        float | None: La nota definitiva calculada y actualizada, o None si no se encontró la inscripción
    """
    nota_definitiva = calcular_nota_definitiva(db, inscripcion_id)
    
    inscripcion = db.query(Inscripcion)\
        .filter(Inscripcion.id == inscripcion_id)\
        .first()
    
    if not inscripcion:
        return None
    
    inscripcion.nota_definitiva = nota_definitiva  # type: ignore
    
    db.commit()
    
    return nota_definitiva
