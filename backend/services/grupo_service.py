"""
Servicio de Grupo

Este módulo contiene toda la lógica de negocio relacionada con los grupos.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from models.grupo import Grupo, EstadoGrupo
from models.curso import Curso
from models.profesor import Profesor
from models.horario import Horario
from utils.validators import validar_cupo, validar_semestre


def crear_grupo(
    db: Session,
    datos_grupo: Dict[str, Any],
    horario: Optional[List[Dict[str, Any]]] = None
) -> Grupo:
    """
    Crea un nuevo grupo con horarios opcionales.
    
    Args:
        db: Sesión de base de datos
        datos_grupo: Diccionario con los datos del grupo
            - curso_id (int): ID del curso (requerido)
            - profesor_id (int, opcional): ID del profesor
            - semestre (str): Periodo académico (requerido)
            - cupo_maximo (int): Cupo máximo del grupo (requerido)
            - estado (EstadoGrupo, opcional): Estado inicial
        horario: Lista opcional de horarios para el grupo
    
    Returns:
        Grupo creado
    
    Raises:
        ValueError: Si faltan datos requeridos o son inválidos
    
    Example:
        >>> grupo = crear_grupo(db, {
        ...     "curso_id": 1,
        ...     "profesor_id": 2,
        ...     "semestre": "2025-1",
        ...     "cupo_maximo": 30
        ... })
    """
    if not datos_grupo.get("curso_id"):
        raise ValueError("El curso_id es requerido")
    if not datos_grupo.get("semestre"):
        raise ValueError("El semestre es requerido")
    if not datos_grupo.get("cupo_maximo"):
        raise ValueError("El cupo_maximo es requerido")
    
    if not validar_semestre(datos_grupo["semestre"]):
        raise ValueError("Formato de semestre inválido. Use formato YYYY-N (ej: 2025-1, 2024-2)")
    
    if not validar_cupo(datos_grupo["cupo_maximo"], minimo=1, maximo=100):
        raise ValueError("El cupo_maximo debe estar entre 1 y 100")
    
    curso = db.query(Curso).filter(Curso.id == datos_grupo["curso_id"]).first()
    if not curso:
        raise ValueError(f"El curso con ID {datos_grupo['curso_id']} no existe")
    
    if datos_grupo.get("profesor_id"):
        profesor = db.query(Profesor).filter(
            Profesor.id == datos_grupo["profesor_id"]
        ).first()
        if not profesor:
            raise ValueError(
                f"El profesor con ID {datos_grupo['profesor_id']} no existe"
            )
    
    nuevo_grupo = Grupo(
        curso_id=datos_grupo["curso_id"],
        profesor_id=datos_grupo.get("profesor_id"),
        semestre=datos_grupo["semestre"],
        cupo_maximo=datos_grupo["cupo_maximo"],
        cupo_actual=0,
        estado=datos_grupo.get("estado", EstadoGrupo.PROGRAMADO)
    )
    
    db.add(nuevo_grupo)
    db.commit()
    db.refresh(nuevo_grupo)
    
    if horario:
        for horario_data in horario:
            horario_obj = Horario(
                grupo_id=nuevo_grupo.id,
                **horario_data
            )
            db.add(horario_obj)
        db.commit()
        db.refresh(nuevo_grupo)
    
    return nuevo_grupo


def obtener_grupo_por_id(
    db: Session,
    grupo_id: int
) -> Optional[Grupo]:
    """
    Obtiene un grupo por su ID con relaciones cargadas.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        Grupo encontrado o None
    
    Example:
        >>> grupo = obtener_grupo_por_id(db, 1)
        >>> if grupo:
        ...     print(f"Grupo de {grupo.curso.nombre}")
    """
    return db.query(Grupo).options(
        joinedload(Grupo.curso),  # type: ignore
        joinedload(Grupo.profesor),  # type: ignore
        joinedload(Grupo.horarios),  # type: ignore
        joinedload(Grupo.inscripciones)  # type: ignore
    ).filter(Grupo.id == grupo_id).first()


def obtener_grupos_por_curso(
    db: Session,
    curso_id: int,
    semestre: Optional[str] = None
) -> List[Grupo]:
    """
    Obtiene todos los grupos de un curso.
    
    Args:
        db: Sesión de base de datos
        curso_id: ID del curso
        semestre: Filtro opcional por semestre
    
    Returns:
        Lista de grupos del curso
    
    Example:
        >>> grupos = obtener_grupos_por_curso(db, 1, "2025-1")
    """
    query = db.query(Grupo).filter(Grupo.curso_id == curso_id)
    
    if semestre:
        query = query.filter(Grupo.semestre == semestre)
    
    return query.all()


def actualizar_profesor(
    db: Session,
    grupo_id: int,
    profesor_id: Optional[int]
) -> Grupo:
    """
    Actualiza el profesor asignado a un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        profesor_id: ID del nuevo profesor (None para desasignar)
    
    Returns:
        Grupo actualizado
    
    Raises:
        ValueError: Si el grupo o profesor no existen
    
    Example:
        >>> grupo = actualizar_profesor(db, 1, 5)
    """
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        raise ValueError(f"El grupo con ID {grupo_id} no existe")
    
    if profesor_id is not None:
        profesor = db.query(Profesor).filter(Profesor.id == profesor_id).first()
        if not profesor:
            raise ValueError(f"El profesor con ID {profesor_id} no existe")
    
    grupo.profesor_id = profesor_id  # type: ignore
    db.commit()
    db.refresh(grupo)
    
    return grupo


def cancelar_grupo(
    db: Session,
    grupo_id: int
) -> Grupo:
    """
    Cancela un grupo cambiando su estado a CANCELADO.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo a cancelar
    
    Returns:
        Grupo cancelado
    
    Raises:
        ValueError: Si el grupo no existe
    
    Example:
        >>> grupo = cancelar_grupo(db, 1)
    """
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        raise ValueError(f"El grupo con ID {grupo_id} no existe")
    
    grupo.estado = EstadoGrupo.CANCELADO  # type: ignore
    db.commit()
    db.refresh(grupo)
    
    return grupo


def obtener_estudiantes_inscritos(
    db: Session,
    grupo_id: int
) -> List:
    """
    Obtiene la lista de estudiantes inscritos en un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        Lista de estudiantes inscritos
    
    Raises:
        ValueError: Si el grupo no existe
    
    Example:
        >>> estudiantes = obtener_estudiantes_inscritos(db, 1)
        >>> print(f"Total inscritos: {len(estudiantes)}")
    """
    from models.estudiante import Estudiante
    from models.inscripcion import Inscripcion
    
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        raise ValueError(f"El grupo con ID {grupo_id} no existe")
    
    return db.query(Estudiante).join(Inscripcion).filter(
        Inscripcion.grupo_id == grupo_id
    ).all()


def incrementar_cupo_actual(
    db: Session,
    grupo_id: int
) -> Grupo:
    """
    Incrementa en 1 el cupo actual del grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        Grupo actualizado
    
    Raises:
        ValueError: Si el grupo no existe o no hay cupos disponibles
    
    Example:
        >>> grupo = incrementar_cupo_actual(db, 1)
    """
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        raise ValueError(f"El grupo con ID {grupo_id} no existe")
    
    if grupo.cupo_actual >= grupo.cupo_maximo:  # type: ignore
        raise ValueError(
            f"No hay cupos disponibles. Cupo actual: {grupo.cupo_actual}/{grupo.cupo_maximo}"
        )
    
    grupo.cupo_actual = grupo.cupo_actual + 1  # type: ignore
    db.commit()
    db.refresh(grupo)
    
    return grupo


def decrementar_cupo_actual(
    db: Session,
    grupo_id: int
) -> Grupo:
    """
    Decrementa en 1 el cupo actual del grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        Grupo actualizado
    
    Raises:
        ValueError: Si el grupo no existe o el cupo ya es 0
    
    Example:
        >>> grupo = decrementar_cupo_actual(db, 1)
    """
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        raise ValueError(f"El grupo con ID {grupo_id} no existe")
    
    if grupo.cupo_actual <= 0:  # type: ignore
        raise ValueError("El cupo actual ya es 0, no se puede decrementar")
    
    grupo.cupo_actual = grupo.cupo_actual - 1  # type: ignore
    db.commit()
    db.refresh(grupo)
    
    return grupo


def obtener_dashboard(
    db: Session,
    grupo_id: int
) -> Dict[str, Any]:
    """
    Obtiene un dashboard completo de información del grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        Diccionario con información del dashboard:
        - grupo: Información del grupo
        - curso: Información del curso
        - profesor: Información del profesor
        - cupos: Información de cupos
        - total_estudiantes: Total de estudiantes inscritos
        - horarios: Lista de horarios
        - actividades_pendientes: Actividades próximas
    
    Raises:
        ValueError: Si el grupo no existe
    
    Example:
        >>> dashboard = obtener_dashboard(db, 1)
        >>> print(f"Cupos: {dashboard['cupos']['actual']}/{dashboard['cupos']['maximo']}")
    """
    from models.actividad_evaluativa import ActividadEvaluativa
    from datetime import datetime
    
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        raise ValueError(f"El grupo con ID {grupo_id} no existe")
    
    cupos_disponibles = grupo.cupo_maximo - grupo.cupo_actual
    porcentaje_ocupacion = (
        (grupo.cupo_actual / grupo.cupo_maximo * 100) if grupo.cupo_maximo > 0 else 0  # type: ignore
    )
    
    total_estudiantes = len(obtener_estudiantes_inscritos(db, grupo_id))
    
    actividades_pendientes = db.query(ActividadEvaluativa).filter(
        ActividadEvaluativa.grupo_id == grupo_id
    ).limit(5).all()
    
    return {
        "grupo": {
            "id": grupo.id,
            "semestre": grupo.semestre,
            "estado": grupo.estado.value
        },
        "curso": {
            "id": grupo.curso.id,
            "codigo": grupo.curso.codigo,
            "nombre": grupo.curso.nombre
        } if grupo.curso else None,
        "profesor": {
            "id": grupo.profesor.id,
            "nombre": f"{grupo.profesor.usuario.nombre} {grupo.profesor.usuario.apellido}"
        } if grupo.profesor else None,
        "cupos": {
            "maximo": grupo.cupo_maximo,
            "actual": grupo.cupo_actual,
            "disponibles": cupos_disponibles,
            "porcentaje_ocupacion": round(float(porcentaje_ocupacion), 2)  # type: ignore
        },
        "total_estudiantes": total_estudiantes,
        "horarios": [
            {
                "dia": h.dia,
                "hora_inicio": str(h.hora_inicio),
                "hora_fin": str(h.hora_fin),
                "salon": h.salon
            } for h in grupo.horarios
        ] if grupo.horarios else [],
        "actividades_pendientes": len(actividades_pendientes)
    }


def obtener_grupos_por_profesor(
    db: Session,
    profesor_id: int,
    semestre: Optional[str] = None
) -> List[Grupo]:
    """
    Obtiene todos los grupos de un profesor.
    
    Args:
        db: Sesión de base de datos
        profesor_id: ID del profesor
        semestre: Filtro opcional por semestre
    
    Returns:
        Lista de grupos del profesor
    
    Example:
        >>> grupos = obtener_grupos_por_profesor(db, 2, "2025-1")
    """
    query = db.query(Grupo).filter(Grupo.profesor_id == profesor_id)
    
    if semestre:
        query = query.filter(Grupo.semestre == semestre)
    
    return query.all()


def obtener_grupos_por_semestre(
    db: Session,
    semestre: str,
    estado: Optional[EstadoGrupo] = None
) -> List[Grupo]:
    """
    Obtiene todos los grupos de un semestre.
    
    Args:
        db: Sesión de base de datos
        semestre: Periodo académico
        estado: Filtro opcional por estado
    
    Returns:
        Lista de grupos del semestre
    
    Example:
        >>> grupos = obtener_grupos_por_semestre(db, "2025-1", EstadoGrupo.ABIERTO)
    """
    query = db.query(Grupo).filter(Grupo.semestre == semestre)
    
    if estado:
        query = query.filter(Grupo.estado == estado)
    
    return query.all()


def grupo_tiene_cupos_disponibles(
    db: Session,
    grupo_id: int
) -> bool:
    """
    Verifica si un grupo tiene cupos disponibles.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        True si hay cupos, False en caso contrario
    
    Example:
        >>> if grupo_tiene_cupos_disponibles(db, 1):
        ...     print("Puedes inscribirte")
    """
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        return False
    
    return grupo.cupo_actual < grupo.cupo_maximo  # type: ignore


def obtener_cupos_disponibles(
    db: Session,
    grupo_id: int
) -> int:
    """
    Obtiene la cantidad de cupos disponibles en un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        Cantidad de cupos disponibles
    
    Raises:
        ValueError: Si el grupo no existe
    
    Example:
        >>> cupos = obtener_cupos_disponibles(db, 1)
        >>> print(f"Cupos disponibles: {cupos}")
    """
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        raise ValueError(f"El grupo con ID {grupo_id} no existe")
    
    return grupo.cupo_maximo - grupo.cupo_actual  # type: ignore


def grupo_existe(
    db: Session,
    grupo_id: int
) -> bool:
    """
    Verifica si existe un grupo con el ID dado.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        True si existe, False en caso contrario
    
    Example:
        >>> if grupo_existe(db, 1):
        ...     print("El grupo existe")
    """
    return db.query(Grupo).filter(Grupo.id == grupo_id).first() is not None


def grupo_puede_aceptar_inscripciones(
    db: Session,
    grupo_id: int
) -> tuple[bool, str]:
    """
    Verifica si un grupo puede aceptar nuevas inscripciones.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
    
    Returns:
        Tupla (puede_inscribir, mensaje)
    
    Example:
        >>> puede, msg = grupo_puede_aceptar_inscripciones(db, 1)
        >>> if not puede:
        ...     print(msg)
    """
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        return False, "El grupo no existe"
    
    if grupo.estado not in [EstadoGrupo.ABIERTO, EstadoGrupo.PROGRAMADO]:
        return False, f"El grupo está en estado {grupo.estado.value}"
    
    if grupo.cupo_actual >= grupo.cupo_maximo:  # type: ignore
        return False, "No hay cupos disponibles"
    
    if not grupo.profesor_id:  # type: ignore
        return False, "El grupo no tiene profesor asignado"
    
    return True, "El grupo puede aceptar inscripciones"


def cambiar_estado_grupo(
    db: Session,
    grupo_id: int,
    nuevo_estado: EstadoGrupo
) -> Grupo:
    """
    Cambia el estado de un grupo.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        nuevo_estado: Nuevo estado del grupo
    
    Returns:
        Grupo actualizado
    
    Raises:
        ValueError: Si el grupo no existe
    
    Example:
        >>> grupo = cambiar_estado_grupo(db, 1, EstadoGrupo.EN_CURSO)
    """
    grupo = obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        raise ValueError(f"El grupo con ID {grupo_id} no existe")
    
    grupo.estado = nuevo_estado  # type: ignore
    db.commit()
    db.refresh(grupo)
    
    return grupo
