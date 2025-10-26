"""
Servicio de Horario
Lógica de negocio para gestión y consulta de horarios de grupos
"""
from typing import Optional, List, Dict, Any
from datetime import time
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from models.horario import Horario
from models.grupo import Grupo
from utils.validators import validar_dia_semana, validar_rango_tiempo, validar_duracion_horario
from utils.datetime_utils import calcular_duracion_minutos


def obtener_horarios_por_grupo(
    db: Session,
    grupo_id: int
) -> List[Horario]:
    """
    Obtiene todos los horarios de un grupo específico.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        List[Horario]: Lista de horarios del grupo ordenados por día y hora
    
    Example:
        >>> horarios = obtener_horarios_por_grupo(db, 1)
        >>> for h in horarios:
        ...     print(f"{h.dia} {h.hora_inicio}-{h.hora_fin} en {h.salon}")
    """
    return db.query(Horario)\
        .filter(Horario.grupo_id == grupo_id)\
        .order_by(Horario.dia, Horario.hora_inicio)\
        .all()


def obtener_horarios_por_dia(
    db: Session,
    dia: str,
    semestre: Optional[str] = None
) -> List[Horario]:
    """
    Obtiene todos los horarios de un día específico.
    
    Args:
        db: Sesión de base de datos
        dia: Día de la semana (ej: "Lunes", "Martes")
        semestre: Filtro opcional por semestre
    
    Returns:
        List[Horario]: Lista de horarios del día con información del grupo
    
    Example:
        >>> horarios_lunes = obtener_horarios_por_dia(db, "Lunes", "2025-1")
    """
    query = db.query(Horario)\
        .options(joinedload(Horario.grupo))\
        .filter(Horario.dia == dia)
    
    if semestre:
        query = query.join(Grupo, Horario.grupo_id == Grupo.id)\
            .filter(Grupo.semestre == semestre)
    
    return query.order_by(Horario.hora_inicio).all()


def obtener_horarios_por_salon(
    db: Session,
    salon: str,
    dia: Optional[str] = None,
    semestre: Optional[str] = None
) -> List[Horario]:
    """
    Obtiene todos los horarios que usan un salón específico.
    
    Args:
        db: Sesión de base de datos
        salon: Nombre del salón
        dia: Filtro opcional por día
        semestre: Filtro opcional por semestre
    
    Returns:
        List[Horario]: Lista de horarios que usan el salón
    
    Example:
        >>> horarios = obtener_horarios_por_salon(db, "Bloque 5 - 101", "Lunes", "2025-1")
    """
    query = db.query(Horario)\
        .options(joinedload(Horario.grupo))\
        .filter(Horario.salon == salon)
    
    if dia:
        query = query.filter(Horario.dia == dia)
    
    if semestre:
        query = query.join(Grupo, Horario.grupo_id == Grupo.id)\
            .filter(Grupo.semestre == semestre)
    
    return query.order_by(Horario.dia, Horario.hora_inicio).all()


def obtener_horario_por_id(
    db: Session,
    horario_id: int
) -> Optional[Horario]:
    """
    Obtiene un horario por su ID con relaciones cargadas.
    
    Args:
        db: Sesión de base de datos
        horario_id: ID del horario
    
    Returns:
        Horario | None: El horario o None si no existe
    """
    return db.query(Horario)\
        .options(joinedload(Horario.grupo))\
        .filter(Horario.id == horario_id)\
        .first()


def verificar_conflicto_salon(
    db: Session,
    salon: str,
    dia: str,
    hora_inicio: time,
    hora_fin: time,
    semestre: str,
    excluir_horario_id: Optional[int] = None
) -> tuple[bool, List[Horario]]:
    """
    Verifica si hay conflictos de uso de salón en un horario específico.
    
    Args:
        db: Sesión de base de datos
        salon: Nombre del salón
        dia: Día de la semana
        hora_inicio: Hora de inicio
        hora_fin: Hora de fin
        semestre: Semestre a verificar
        excluir_horario_id: ID de horario a excluir (útil al actualizar)
    
    Returns:
        Tupla (hay_conflicto, lista_de_conflictos)
    
    Example:
        >>> conflicto, horarios = verificar_conflicto_salon(
        ...     db, "Bloque 5 - 101", "Lunes", 
        ...     time(8, 0), time(10, 0), "2025-1"
        ... )
        >>> if conflicto:
        ...     print(f"Hay {len(horarios)} conflicto(s)")
    """
    query = db.query(Horario)\
        .join(Grupo, Horario.grupo_id == Grupo.id)\
        .filter(
            and_(
                Horario.salon == salon,
                Horario.dia == dia,
                Grupo.semestre == semestre,
                or_(
                    and_(
                        Horario.hora_inicio <= hora_inicio,  # type: ignore
                        Horario.hora_fin > hora_inicio  # type: ignore
                    ),
                    and_(
                        Horario.hora_inicio < hora_fin,  # type: ignore
                        Horario.hora_fin >= hora_fin  # type: ignore
                    ),
                    and_(
                        Horario.hora_inicio >= hora_inicio,  # type: ignore
                        Horario.hora_fin <= hora_fin  # type: ignore
                    )
                )
            )
        )
    
    if excluir_horario_id:
        query = query.filter(Horario.id != excluir_horario_id)
    
    conflictos = query.all()
    
    return len(conflictos) > 0, conflictos


def verificar_conflicto_profesor(
    db: Session,
    profesor_id: int,
    dia: str,
    hora_inicio: time,
    hora_fin: time,
    semestre: str,
    excluir_grupo_id: Optional[int] = None
) -> tuple[bool, List[Horario]]:
    """
    Verifica si un profesor tiene conflictos de horario.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
        dia: Día de la semana
        hora_inicio: Hora de inicio
        hora_fin: Hora de fin
        semestre: Semestre a verificar
        excluir_grupo_id: ID de grupo a excluir (útil al actualizar)
    
    Returns:
        Tupla (hay_conflicto, lista_de_conflictos)
    
    Example:
        >>> conflicto, horarios = verificar_conflicto_profesor(
        ...     db, 5, "Martes", time(14, 0), time(16, 0), "2025-1"
        ... )
    """
    query = db.query(Horario)\
        .join(Grupo, Horario.grupo_id == Grupo.id)\
        .filter(
            and_(
                Grupo.profesor_id == profesor_id,
                Horario.dia == dia,
                Grupo.semestre == semestre,
                or_(
                    and_(
                        Horario.hora_inicio <= hora_inicio,  # type: ignore
                        Horario.hora_fin > hora_inicio  # type: ignore
                    ),
                    and_(
                        Horario.hora_inicio < hora_fin,  # type: ignore
                        Horario.hora_fin >= hora_fin  # type: ignore
                    ),
                    and_(
                        Horario.hora_inicio >= hora_inicio,  # type: ignore
                        Horario.hora_fin <= hora_fin  # type: ignore
                    )
                )
            )
        )
    
    if excluir_grupo_id:
        query = query.filter(Grupo.id != excluir_grupo_id)
    
    conflictos = query.all()
    
    return len(conflictos) > 0, conflictos


def horario_es_valido(
    hora_inicio: time,
    hora_fin: time
) -> tuple[bool, str]:
    """
    Valida que un rango de horas sea válido.
    
    Args:
        hora_inicio: Hora de inicio
        hora_fin: Hora de fin
    
    Returns:
        Tupla (es_valido, mensaje)
    
    Example:
        >>> valido, msg = horario_es_valido(time(8, 0), time(10, 0))
        >>> if not valido:
        ...     print(msg)
    """
    hora_min = time(6, 0)
    hora_max = time(22, 0)
    
    if not validar_rango_tiempo(hora_inicio, hora_fin, hora_min, hora_max):
        if hora_fin <= hora_inicio:
            return False, "La hora de fin debe ser posterior a la hora de inicio"
        elif hora_inicio < hora_min or hora_fin > hora_max:
            return False, "El horario debe estar entre 6:00 AM y 10:00 PM"
        return False, "Rango de tiempo inválido"
    
    if not validar_duracion_horario(hora_inicio, hora_fin, min_minutos=30, max_minutos=240):
        duracion = calcular_duracion_minutos(hora_inicio, hora_fin)
        if duracion > 240:
            return False, "La duración de una clase no puede exceder 4 horas"
        elif duracion < 30:
            return False, "La duración de una clase debe ser al menos 30 minutos"
        return False, "Duración inválida"
    
    return True, "Horario válido"


def crear_horario(
    db: Session,
    datos_horario: Dict[str, Any]
) -> Horario:
    """
    Crea un nuevo horario para un grupo con validaciones.
    
    Args:
        db: Sesión de base de datos
        datos_horario: Diccionario con los datos del horario
            - grupo_id: int (requerido)
            - dia: str (requerido)
            - hora_inicio: time (requerido)
            - hora_fin: time (requerido)
            - salon: str (opcional)
    
    Returns:
        Horario: El horario creado
    
    Raises:
        ValueError: Si los datos son inválidos o hay conflictos
    
    Example:
        >>> horario = crear_horario(db, {
        ...     "grupo_id": 1,
        ...     "dia": "Lunes",
        ...     "hora_inicio": time(8, 0),
        ...     "hora_fin": time(10, 0),
        ...     "salon": "Bloque 5 - 101"
        ... })
    """
    grupo = db.query(Grupo).filter(Grupo.id == datos_horario["grupo_id"]).first()
    if not grupo:
        raise ValueError(f"El grupo con ID {datos_horario['grupo_id']} no existe")
    
    if not validar_dia_semana(datos_horario["dia"]):
        raise ValueError(
            f"Día '{datos_horario['dia']}' no es válido. Use: Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Domingo"
        )
    
    valido, mensaje = horario_es_valido(
        datos_horario["hora_inicio"],
        datos_horario["hora_fin"]
    )
    if not valido:
        raise ValueError(mensaje)
    
    if datos_horario.get("salon"):
        conflicto, horarios_conflicto = verificar_conflicto_salon(
            db,
            datos_horario["salon"],
            datos_horario["dia"],
            datos_horario["hora_inicio"],
            datos_horario["hora_fin"],
            grupo.semestre  # type: ignore
        )
        if conflicto:
            raise ValueError(
                f"El salón '{datos_horario['salon']}' ya está ocupado en ese horario"
            )
    
    if grupo.profesor_id:  # type: ignore
        conflicto, horarios_conflicto = verificar_conflicto_profesor(
            db,
            grupo.profesor_id,  # type: ignore
            datos_horario["dia"],
            datos_horario["hora_inicio"],
            datos_horario["hora_fin"],
            grupo.semestre  # type: ignore
        )
        if conflicto:
            raise ValueError(
                "El profesor ya tiene clases asignadas en ese horario"
            )
    
    nuevo_horario = Horario(
        grupo_id=datos_horario["grupo_id"],
        dia=datos_horario["dia"],
        hora_inicio=datos_horario["hora_inicio"],
        hora_fin=datos_horario["hora_fin"],
        salon=datos_horario.get("salon")
    )
    
    db.add(nuevo_horario)
    db.commit()
    db.refresh(nuevo_horario)
    
    return nuevo_horario


def actualizar_horario(
    db: Session,
    horario_id: int,
    datos_actualizacion: Dict[str, Any]
) -> Optional[Horario]:
    """
    Actualiza un horario existente con validaciones.
    
    Args:
        db: Sesión de base de datos
        horario_id: ID del horario a actualizar
        datos_actualizacion: Diccionario con los campos a actualizar
    
    Returns:
        Horario | None: El horario actualizado o None si no existe
    
    Raises:
        ValueError: Si los datos son inválidos o hay conflictos
    """
    horario = obtener_horario_por_id(db, horario_id)
    if not horario:
        return None
    
    dia = datos_actualizacion.get("dia", horario.dia)
    hora_inicio = datos_actualizacion.get("hora_inicio", horario.hora_inicio)
    hora_fin = datos_actualizacion.get("hora_fin", horario.hora_fin)
    salon = datos_actualizacion.get("salon", horario.salon)
    
    if "hora_inicio" in datos_actualizacion or "hora_fin" in datos_actualizacion:
        valido, mensaje = horario_es_valido(hora_inicio, hora_fin)
        if not valido:
            raise ValueError(mensaje)
    
    grupo = horario.grupo
    if salon and ("dia" in datos_actualizacion or "hora_inicio" in datos_actualizacion 
                  or "hora_fin" in datos_actualizacion or "salon" in datos_actualizacion):
        conflicto, _ = verificar_conflicto_salon(
            db, salon, dia, hora_inicio, hora_fin, grupo.semestre, horario_id
        )
        if conflicto:
            raise ValueError(f"El salón '{salon}' ya está ocupado en ese horario")
    
    if grupo.profesor_id and ("dia" in datos_actualizacion or "hora_inicio" in datos_actualizacion 
                              or "hora_fin" in datos_actualizacion):
        conflicto, _ = verificar_conflicto_profesor(
            db, grupo.profesor_id, dia, hora_inicio, hora_fin, grupo.semestre, grupo.id
        )
        if conflicto:
            raise ValueError("El profesor ya tiene clases asignadas en ese horario")
    
    for campo, valor in datos_actualizacion.items():
        if hasattr(horario, campo):
            setattr(horario, campo, valor)
    
    db.commit()
    db.refresh(horario)
    
    return horario


def eliminar_horario(
    db: Session,
    horario_id: int
) -> bool:
    """
    Elimina un horario.
    
    Args:
        db: Sesión de base de datos
        horario_id: ID del horario a eliminar
    
    Returns:
        bool: True si se eliminó, False si no se encontró
    
    Example:
        >>> if eliminar_horario(db, 1):
        ...     print("Horario eliminado exitosamente")
    """
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    
    if not horario:
        return False
    
    db.delete(horario)
    db.commit()
    
    return True


def eliminar_horarios_por_grupo(
    db: Session,
    grupo_id: int
) -> int:
    """
    Elimina todos los horarios de un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        int: Número de horarios eliminados
    
    Example:
        >>> total = eliminar_horarios_por_grupo(db, 1)
        >>> print(f"Se eliminaron {total} horarios")
    """
    horarios = db.query(Horario).filter(Horario.grupo_id == grupo_id).all()
    total = len(horarios)
    
    for horario in horarios:
        db.delete(horario)
    
    db.commit()
    
    return total


def obtener_horarios_disponibles_salon(
    db: Session,
    salon: str,
    dia: str,
    semestre: str
) -> List[Dict[str, Any]]:
    """
    Obtiene los horarios disponibles de un salón en un día.
    
    Args:
        db: Sesión de base de datos
        salon: Nombre del salón
        dia: Día de la semana
        semestre: Semestre a consultar
    
    Returns:
        List[Dict]: Lista de bloques ocupados con información
    
    Example:
        >>> ocupados = obtener_horarios_disponibles_salon(db, "Bloque 5 - 101", "Lunes", "2025-1")
        >>> for bloque in ocupados:
        ...     print(f"{bloque['hora_inicio']}-{bloque['hora_fin']}: {bloque['curso']}")
    """
    horarios = obtener_horarios_por_salon(db, salon, dia, semestre)
    
    resultado = []
    for h in horarios:
        resultado.append({
            "horario_id": h.id,
            "hora_inicio": h.hora_inicio,
            "hora_fin": h.hora_fin,
            "grupo_id": h.grupo_id,
            "curso": h.grupo.curso.nombre if h.grupo and h.grupo.curso else "N/A",
            "profesor": f"{h.grupo.profesor.usuario.nombre} {h.grupo.profesor.usuario.apellido}" 
                       if h.grupo and h.grupo.profesor else "Sin asignar"
        })
    
    return resultado


def contar_horarios_por_grupo(
    db: Session,
    grupo_id: int
) -> int:
    """
    Cuenta el número de horarios de un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        int: Número de horarios
    """
    return db.query(Horario).filter(Horario.grupo_id == grupo_id).count()


def horario_existe(
    db: Session,
    horario_id: int
) -> bool:
    """
    Verifica si un horario existe.
    
    Args:
        db: Sesión de base de datos
        horario_id: ID del horario
    
    Returns:
        bool: True si existe, False en caso contrario
    """
    return db.query(Horario).filter(Horario.id == horario_id).first() is not None


def obtener_estadisticas_horarios(
    db: Session,
    semestre: str
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de uso de horarios en un semestre.
    
    Args:
        db: Sesión de base de datos
        semestre: Semestre a analizar
    
    Returns:
        Dict: Diccionario con estadísticas
    """
    from sqlalchemy import func, distinct
    
    total_horarios = db.query(Horario)\
        .join(Grupo, Horario.grupo_id == Grupo.id)\
        .filter(Grupo.semestre == semestre)\
        .count()
    
    salones_unicos = db.query(func.count(distinct(Horario.salon)))\
        .join(Grupo, Horario.grupo_id == Grupo.id)\
        .filter(
            and_(
                Grupo.semestre == semestre,
                Horario.salon.isnot(None)  # type: ignore
            )
        )\
        .scalar() or 0
    
    grupos_con_horarios = db.query(func.count(distinct(Horario.grupo_id)))\
        .join(Grupo, Horario.grupo_id == Grupo.id)\
        .filter(Grupo.semestre == semestre)\
        .scalar() or 0
    
    return {
        "semestre": semestre,
        "total_horarios": total_horarios,
        "salones_en_uso": salones_unicos,
        "grupos_con_horarios": grupos_con_horarios
    }
