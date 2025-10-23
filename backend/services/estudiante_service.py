"""
Servicio de Estudiante
======================

Este módulo contiene toda la lógica de negocio relacionada con los estudiantes.
"""

from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, extract
from datetime import datetime
from decimal import Decimal

from models.estudiante import Estudiante, EstadoAcademicoEstudiante
from models.usuario import Usuario, EstadoUsuario
from models.programa_academico import ProgramaAcademico
from models.inscripcion import Inscripcion, EstadoInscripcion
from models.grupo import Grupo, EstadoGrupo
from models.curso import Curso
from models.calificacion import Calificacion
from models.entrega import Entrega
from models.actividad_evaluativa import ActividadEvaluativa


def crear_perfil_estudiante(
    db: Session,
    datos_estudiante: Dict[str, Any]
) -> Estudiante:
    """
    Crea un perfil de estudiante para un usuario.
    
    Args:
        db: Sesión de base de datos
        datos_estudiante: Diccionario con los datos del estudiante
            - usuario_id (int): ID del usuario (requerido)
            - programa_id (int): ID del programa académico (requerido)
            - documento (str, opcional): Número de documento
            - tipo_documento (str, opcional): Tipo de documento
            - estado_academico (EstadoAcademicoEstudiante, opcional): Estado
    
    Returns:
        Estudiante: El perfil de estudiante creado
    
    Raises:
        ValueError: Si el usuario no existe, ya tiene perfil de estudiante,
                   no tiene rol de estudiante, o el programa no existe
    
    Example:
        >>> estudiante = crear_perfil_estudiante(db, {
        ...     "usuario_id": 10,
        ...     "programa_id": 3,
        ...     "documento": "9876543210",
        ...     "tipo_documento": "Cédula"
        ... })
    """
    usuario_id = datos_estudiante.get("usuario_id")
    programa_id = datos_estudiante.get("programa_id")
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise ValueError(f"El usuario con ID {usuario_id} no existe")
    
    if usuario.rol_id != 3: # type: ignore
        raise ValueError(f"El usuario {usuario.nombre_completo} no tiene rol de estudiante")
    
    estudiante_existente = db.query(Estudiante).filter(
        Estudiante.usuario_id == usuario_id
    ).first()
    if estudiante_existente:
        raise ValueError(f"El usuario {usuario.nombre_completo} ya tiene un perfil de estudiante")
    
    programa = db.query(ProgramaAcademico).filter(
        ProgramaAcademico.id == programa_id
    ).first()
    if not programa:
        raise ValueError(f"El programa académico con ID {programa_id} no existe")
    
    nuevo_estudiante = Estudiante(
        usuario_id=usuario_id,
        programa_id=programa_id,
        documento=datos_estudiante.get("documento"),
        tipo_documento=datos_estudiante.get("tipo_documento"),
        estado_academico=datos_estudiante.get(
            "estado_academico",
            EstadoAcademicoEstudiante.MATRICULADO
        )
    )
    
    db.add(nuevo_estudiante)
    db.commit()
    db.refresh(nuevo_estudiante)
    
    return nuevo_estudiante


def obtener_estudiante_por_id(
    db: Session,
    estudiante_id: int
) -> Optional[Estudiante]:
    """
    Obtiene un estudiante por su ID.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
    
    Returns:
        Estudiante o None si no existe
    
    Example:
        >>> estudiante = obtener_estudiante_por_id(db, 1)
        >>> if estudiante:
        ...     print(estudiante.codigo)
    """
    return db.query(Estudiante).filter(Estudiante.id == estudiante_id).first()


def obtener_estudiante_por_usuario_id(
    db: Session,
    usuario_id: int
) -> Optional[Estudiante]:
    """
    Obtiene un estudiante por el ID de su usuario.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
    
    Returns:
        Estudiante o None si no existe
    
    Example:
        >>> estudiante = obtener_estudiante_por_usuario_id(db, 10)
    """
    return db.query(Estudiante).filter(Estudiante.usuario_id == usuario_id).first()


def listar_estudiantes(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    programa_id: Optional[int] = None,
    estado_academico: Optional[EstadoAcademicoEstudiante] = None,
    busqueda: Optional[str] = None,
    solo_activos: bool = True
) -> List[Estudiante]:
    """
    Lista estudiantes con filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar (paginación)
        limit: Número máximo de registros a retornar
        programa_id: Filtrar por programa académico (opcional)
        estado_academico: Filtrar por estado académico (opcional)
        busqueda: Búsqueda por nombre, apellido o código (opcional)
        solo_activos: Si True, solo retorna estudiantes con usuario activo
    
    Returns:
        Lista de estudiantes
    
    Example:
        >>> estudiantes = listar_estudiantes(db, programa_id=3, skip=0, limit=20)
    """
    query = db.query(Estudiante).join(Usuario)
    
    # Filtrar por programa
    if programa_id:
        query = query.filter(Estudiante.programa_id == programa_id)
    
    # Filtrar por estado académico
    if estado_academico:
        query = query.filter(Estudiante.estado_academico == estado_academico)
    
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
                Estudiante.documento.ilike(busqueda_patron)
            )
        )
    
    return query.offset(skip).limit(limit).all()


def contar_estudiantes(
    db: Session,
    programa_id: Optional[int] = None,
    estado_academico: Optional[EstadoAcademicoEstudiante] = None,
    solo_activos: bool = True
) -> int:
    """
    Cuenta el total de estudiantes con filtros opcionales.
    
    Args:
        db: Sesión de base de datos
        programa_id: Filtrar por programa académico (opcional)
        estado_academico: Filtrar por estado académico (opcional)
        solo_activos: Si True, solo cuenta estudiantes con usuario activo
    
    Returns:
        Total de estudiantes
    
    Example:
        >>> total = contar_estudiantes(db, programa_id=3)
    """
    query = db.query(func.count(Estudiante.id)).join(Usuario)
    
    if programa_id:
        query = query.filter(Estudiante.programa_id == programa_id)
    
    if estado_academico:
        query = query.filter(Estudiante.estado_academico == estado_academico)
    
    if solo_activos:
        query = query.filter(Usuario.estado == EstadoUsuario.ACTIVO)
    
    return query.scalar()


def actualizar_estudiante(
    db: Session,
    estudiante_id: int,
    datos_actualizados: Dict[str, Any]
) -> Estudiante:
    """
    Actualiza los datos de un estudiante.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
        datos_actualizados: Diccionario con los campos a actualizar
    
    Returns:
        Estudiante actualizado
    
    Raises:
        ValueError: Si el estudiante no existe o el programa no es válido
    
    Example:
        >>> estudiante = actualizar_estudiante(db, 1, {
        ...     "creditos_aprobados": 120,
        ...     "estado_academico": EstadoAcademicoEstudiante.MATRICULADO
        ... })
    """
    estudiante = obtener_estudiante_por_id(db, estudiante_id)
    if not estudiante:
        raise ValueError(f"El estudiante con ID {estudiante_id} no existe")
    
    if "programa_id" in datos_actualizados and datos_actualizados["programa_id"]:
        programa = db.query(ProgramaAcademico).filter(
            ProgramaAcademico.id == datos_actualizados["programa_id"]
        ).first()
        if not programa:
            raise ValueError(
                f"El programa académico con ID {datos_actualizados['programa_id']} no existe"
            )
    
    campos_permitidos = [
        "documento",
        "tipo_documento",
        "programa_id",
        "estado_academico"
    ]
    
    for campo, valor in datos_actualizados.items():
        if campo in campos_permitidos:
            setattr(estudiante, campo, valor)
    
    db.commit()
    db.refresh(estudiante)
    
    return estudiante


def eliminar_estudiante(
    db: Session,
    estudiante_id: int
) -> bool:
    """
    Elimina un estudiante del sistema.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
    
    Returns:
        True si se eliminó, False si no existía
    
    Example:
        >>> eliminado = eliminar_estudiante(db, 1)
    """
    estudiante = obtener_estudiante_por_id(db, estudiante_id)
    if not estudiante:
        return False
    
    db.delete(estudiante)
    db.commit()
    
    return True


def obtener_perfil_completo_estudiante(
    db: Session,
    estudiante_id: int
) -> Optional[Dict[str, Any]]:
    """
    Obtiene el perfil completo de un estudiante con toda la información relacionada.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
    
    Returns:
        Diccionario con los datos completos o None si no existe:
        - estudiante: Modelo Estudiante
        - usuario: Modelo Usuario asociado
        - programa: Modelo ProgramaAcademico
        - total_inscripciones: Total de inscripciones históricas
        - inscripciones_activas: Inscripciones en curso
        - cursos_aprobados: Total de cursos aprobados
        - cursos_reprobados: Total de cursos reprobados
        - promedio_actual: Promedio académico calculado
    
    Example:
        >>> perfil = obtener_perfil_completo_estudiante(db, 1)
        >>> print(f"Estudiante: {perfil['usuario'].nombre_completo}")
        >>> print(f"Promedio: {perfil['promedio_actual']}")
    """
    estudiante = db.query(Estudiante).options(
        joinedload(Estudiante.usuario),
        joinedload(Estudiante.programa)
    ).filter(Estudiante.id == estudiante_id).first()
    
    if not estudiante:
        return None
    
    total_inscripciones = db.query(func.count(Inscripcion.id)).filter(
        Inscripcion.estudiante_id == estudiante_id
    ).scalar()
    
    inscripciones_activas = db.query(func.count(Inscripcion.id)).filter(
        and_(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.estado == EstadoInscripcion.INSCRITO
        )
    ).scalar()
    
    cursos_aprobados = db.query(func.count(Inscripcion.id)).filter(
        and_(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.estado == EstadoInscripcion.APROBADO
        )
    ).scalar()
    
    cursos_reprobados = db.query(func.count(Inscripcion.id)).filter(
        and_(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.estado == EstadoInscripcion.REPROBADO
        )
    ).scalar()
    
    promedio_actual = calcular_promedio_academico(db, estudiante_id)
    
    return {
        "estudiante": estudiante,
        "usuario": estudiante.usuario,
        "programa": estudiante.programa,
        "total_inscripciones": total_inscripciones or 0,
        "inscripciones_activas": inscripciones_activas or 0,
        "cursos_aprobados": cursos_aprobados or 0,
        "cursos_reprobados": cursos_reprobados or 0,
        "promedio_actual": promedio_actual
    }


def actualizar_datos_estudiante(
    db: Session,
    estudiante_id: int,
    datos_actualizacion: Dict[str, Any]
) -> Estudiante:
    """
    Actualiza solo los datos específicos del estudiante (no del usuario).
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
        datos_actualizacion: Diccionario con los campos a actualizar
    
    Returns:
        Estudiante actualizado
    
    Raises:
        ValueError: Si el estudiante no existe
    
    Example:
        >>> estudiante = actualizar_datos_estudiante(db, 1, {
        ...     "codigo": "2024001-A",
        ...     "creditos_aprobados": 60
        ... })
    """
    return actualizar_estudiante(db, estudiante_id, datos_actualizacion)


def calcular_promedio_academico(
    db: Session,
    estudiante_id: int
) -> float:
    """
    Calcula el promedio académico ponderado de un estudiante.
    
    El promedio se calcula considerando:
    - Solo cursos con estado APROBADO o REPROBADO
    - Nota final de cada inscripción
    - Créditos del curso como peso
    
    Fórmula: Σ(nota * créditos) / Σ(créditos)
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
    
    Returns:
        Promedio académico (0.0 si no tiene cursos calificados)
    
    Example:
        >>> promedio = calcular_promedio_academico(db, 1)
        >>> print(f"Promedio: {promedio:.2f}")
    """
    inscripciones = db.query(Inscripcion).join(Grupo).join(Curso).filter(
        and_(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.estado.in_([
                EstadoInscripcion.APROBADO,
                EstadoInscripcion.REPROBADO
            ]),
            Inscripcion.nota_definitiva.isnot(None)
        )
    ).all()
    
    if not inscripciones:
        return 0.0
    
    suma_ponderada = 0.0
    suma_creditos = 0
    
    for inscripcion in inscripciones:
        if inscripcion.nota_definitiva is not None:
            nota = float(Decimal(str(inscripcion.nota_definitiva)))
            creditos = inscripcion.grupo.curso.creditos
            
            suma_ponderada += nota * creditos
            suma_creditos += creditos
    
    if suma_creditos == 0:
        return 0.0
    
    promedio = suma_ponderada / suma_creditos
    
    return round(promedio, 2)


def buscar_estudiantes(
    db: Session,
    grupo_id: Optional[int] = None,
    nombre: Optional[str] = None,
    estado: Optional[EstadoAcademicoEstudiante] = None,
    limit: int = 50
) -> List[Estudiante]:
    """
    Busca estudiantes con múltiples criterios.
    
    Args:
        db: Sesión de base de datos
        grupo_id: Filtrar por grupo específico (estudiantes inscritos)
        nombre: Buscar por nombre o apellido
        estado: Filtrar por estado académico
        limit: Máximo de resultados
    
    Returns:
        Lista de estudiantes que coinciden con los criterios
    
    Example:
        >>> # Buscar estudiantes inscritos en un grupo
        >>> estudiantes = buscar_estudiantes(db, grupo_id=5)
        
        >>> # Buscar por nombre
        >>> estudiantes = buscar_estudiantes(db, nombre="Juan")
        
        >>> # Buscar por estado
        >>> estudiantes = buscar_estudiantes(
        ...     db,
        ...     estado=EstadoAcademicoEstudiante.MATRICULADO
        ... )
    """
    query = db.query(Estudiante).join(Usuario)
    
    # Filtrar por grupo
    if grupo_id:
        query = query.join(Inscripcion).filter(
            and_(
                Inscripcion.grupo_id == grupo_id,
                Inscripcion.estado.in_([
                    EstadoInscripcion.INSCRITO,
                    EstadoInscripcion.APROBADO,
                    EstadoInscripcion.REPROBADO
                ])
            )
        )
    
    # Filtrar por nombre
    if nombre:
        patron = f"%{nombre}%"
        query = query.filter(
            or_(
                Usuario.nombre.ilike(patron),
                Usuario.apellido.ilike(patron)
            )
        )
    
    # Filtrar por estado académico
    if estado:
        query = query.filter(Estudiante.estado_academico == estado)
    
    return query.limit(limit).all()


def obtener_estudiantes_por_grupo(
    db: Session,
    grupo_id: int,
    estado_inscripcion: Optional[EstadoInscripcion] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene todos los estudiantes inscritos en un grupo específico.
    
    Args:
        db: Sesión de base de datos
        grupo_id: ID del grupo
        estado_inscripcion: Filtrar por estado de inscripción (opcional)
    
    Returns:
        Lista de diccionarios con estudiante e inscripción
    
    Example:
        >>> estudiantes_grupo = obtener_estudiantes_por_grupo(db, grupo_id=5)
        >>> for item in estudiantes_grupo:
        ...     print(f"{item['estudiante'].codigo}: {item['inscripcion'].nota_final}")
    """
    query = db.query(Estudiante, Inscripcion).join(
        Inscripcion,
        Estudiante.id == Inscripcion.estudiante_id
    ).options(
        joinedload(Estudiante.usuario)
    ).filter(Inscripcion.grupo_id == grupo_id)
    
    if estado_inscripcion:
        query = query.filter(Inscripcion.estado == estado_inscripcion)
    
    resultados = query.all()
    
    return [
        {
            "estudiante": estudiante,
            "inscripcion": inscripcion,
            "usuario": estudiante.usuario
        }
        for estudiante, inscripcion in resultados
    ]


def obtener_inscripciones_estudiante(
    db: Session,
    estudiante_id: int,
    semestre: Optional[str] = None,
    estado: Optional[EstadoInscripcion] = None
) -> List[Inscripcion]:
    """
    Obtiene las inscripciones de un estudiante.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
        semestre: Filtrar por semestre (opcional)
        estado: Filtrar por estado de inscripción (opcional)
    
    Returns:
        Lista de inscripciones con datos del grupo y curso
    
    Example:
        >>> inscripciones = obtener_inscripciones_estudiante(
        ...     db,
        ...     estudiante_id=1,
        ...     semestre="2024-2",
        ...     estado=EstadoInscripcion.INSCRITO
        ... )
    """
    query = db.query(Inscripcion).options(
        joinedload(Inscripcion.grupo).joinedload(Grupo.curso),
        joinedload(Inscripcion.grupo).joinedload(Grupo.profesor)
    ).filter(Inscripcion.estudiante_id == estudiante_id)
    
    if semestre:
        query = query.join(Grupo).filter(Grupo.semestre == semestre)
    
    if estado:
        query = query.filter(Inscripcion.estado == estado)
    
    return query.order_by(Inscripcion.fecha_inscripcion.desc()).all()


def obtener_horario_estudiante(
    db: Session,
    estudiante_id: int,
    semestre: str
) -> List[Dict[str, Any]]:
    """
    Obtiene el horario completo de un estudiante en un semestre.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
        semestre: Semestre a consultar
    
    Returns:
        Lista de horarios con información del curso y grupo
    
    Example:
        >>> horario = obtener_horario_estudiante(db, 1, "2024-2")
        >>> for bloque in horario:
        ...     print(f"{bloque['curso'].nombre}: {bloque['horario'].dia_semana}")
    """
    from models.horario import Horario
    
    inscripciones = db.query(Inscripcion).join(Grupo).filter(
        and_(
            Inscripcion.estudiante_id == estudiante_id,
            Grupo.semestre == semestre,
            Inscripcion.estado == EstadoInscripcion.INSCRITO
        )
    ).all()
    
    horarios = []
    for inscripcion in inscripciones:
        grupo = inscripcion.grupo
        curso = grupo.curso
        
        bloques = db.query(Horario).filter(Horario.grupo_id == grupo.id).all()
        
        for bloque in bloques:
            horarios.append({
                "horario": bloque,
                "grupo": grupo,
                "curso": curso,
                "inscripcion": inscripcion
            })
    
    return horarios


def obtener_estadisticas_estudiante(
    db: Session,
    estudiante_id: int
) -> Dict[str, Any]:
    """
    Obtiene estadísticas académicas completas de un estudiante.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
    
    Returns:
        Diccionario con estadísticas:
        - total_cursos_inscritos: Total histórico
        - cursos_aprobados: Cursos aprobados
        - cursos_reprobados: Cursos reprobados
        - cursos_en_curso: Cursos actuales
        - promedio_academico: Promedio ponderado
        - creditos_aprobados: Créditos acumulados
        - tasa_aprobacion: Porcentaje de aprobación
    
    Example:
        >>> stats = obtener_estadisticas_estudiante(db, 1)
        >>> print(f"Tasa de aprobación: {stats['tasa_aprobacion']}%")
    """
    estudiante = obtener_estudiante_por_id(db, estudiante_id)
    if not estudiante:
        raise ValueError(f"El estudiante con ID {estudiante_id} no existe")
    
    total_inscritos = db.query(func.count(Inscripcion.id)).filter(
        Inscripcion.estudiante_id == estudiante_id
    ).scalar() or 0
    
    aprobados = db.query(func.count(Inscripcion.id)).filter(
        and_(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.estado == EstadoInscripcion.APROBADO
        )
    ).scalar() or 0
    
    reprobados = db.query(func.count(Inscripcion.id)).filter(
        and_(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.estado == EstadoInscripcion.REPROBADO
        )
    ).scalar() or 0
    
    en_curso = db.query(func.count(Inscripcion.id)).filter(
        and_(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.estado == EstadoInscripcion.INSCRITO
        )
    ).scalar() or 0
    
    promedio = calcular_promedio_academico(db, estudiante_id)
    
    cursos_finalizados = aprobados + reprobados
    tasa_aprobacion = (aprobados / cursos_finalizados * 100) if cursos_finalizados > 0 else 0
    
    return {
        "total_cursos_inscritos": total_inscritos,
        "cursos_aprobados": aprobados,
        "cursos_reprobados": reprobados,
        "cursos_en_curso": en_curso,
        "promedio_academico": promedio,
        "tasa_aprobacion": round(tasa_aprobacion, 2)
    }


def obtener_estudiantes_por_programa(
    db: Session,
    programa_id: int,
    estado_academico: Optional[EstadoAcademicoEstudiante] = None
) -> List[Estudiante]:
    """
    Obtiene todos los estudiantes de un programa académico.
    
    Args:
        db: Sesión de base de datos
        programa_id: ID del programa académico
        estado_academico: Filtrar por estado académico (opcional)
    
    Returns:
        Lista de estudiantes del programa
    
    Example:
        >>> estudiantes = obtener_estudiantes_por_programa(db, 3)
    """
    query = db.query(Estudiante).join(Usuario).filter(
        and_(
            Estudiante.programa_id == programa_id,
            Usuario.estado == EstadoUsuario.ACTIVO
        )
    )
    
    if estado_academico:
        query = query.filter(Estudiante.estado_academico == estado_academico)
    
    return query.all()


def estudiante_existe(
    db: Session,
    estudiante_id: int
) -> bool:
    """
    Verifica si existe un estudiante con el ID dado.
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
    
    Returns:
        True si existe, False en caso contrario
    
    Example:
        >>> if estudiante_existe(db, 1):
        ...     print("El estudiante existe")
    """
    return db.query(Estudiante).filter(Estudiante.id == estudiante_id).first() is not None


def usuario_tiene_perfil_estudiante(
    db: Session,
    usuario_id: int
) -> bool:
    """
    Verifica si un usuario tiene perfil de estudiante.
    
    Args:
        db: Sesión de base de datos
        usuario_id: ID del usuario
    
    Returns:
        True si tiene perfil, False en caso contrario
    
    Example:
        >>> if usuario_tiene_perfil_estudiante(db, 10):
        ...     print("Este usuario es estudiante")
    """
    return db.query(Estudiante).filter(
        Estudiante.usuario_id == usuario_id
    ).first() is not None


def estudiante_puede_inscribirse(
    db: Session,
    estudiante_id: int,
    grupo_id: int
) -> Tuple[bool, str]:
    """
    Verifica si un estudiante puede inscribirse en un grupo.
    
    Valida que:
    - El estudiante existe y está activo
    - El grupo existe y está abierto
    - Hay cupos disponibles
    - No está ya inscrito en el grupo
    - El curso pertenece al programa del estudiante (opcional)
    
    Args:
        db: Sesión de base de datos
        estudiante_id: ID del estudiante
        grupo_id: ID del grupo
    
    Returns:
        Tupla (puede_inscribirse, mensaje)
    
    Example:
        >>> puede, msg = estudiante_puede_inscribirse(db, 1, 5)
        >>> if puede:
        ...     # Proceder con inscripción
        ...     pass
    """
    estudiante = obtener_estudiante_por_id(db, estudiante_id)
    if not estudiante:
        return False, "El estudiante no existe"
    
    if estudiante.usuario.estado != EstadoUsuario.ACTIVO:
        return False, "El estudiante no está activo"
    
    if estudiante.estado_academico not in [
        EstadoAcademicoEstudiante.MATRICULADO,
        EstadoAcademicoEstudiante.EN_PRUEBA_ACADEMICA
    ]:
        return False, f"El estudiante está en estado: {estudiante.estado_academico.value}"
    
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        return False, "El grupo no existe"
    
    if grupo.estado.value != EstadoGrupo.ABIERTO.value:
        return False, f"El grupo está en estado: {grupo.estado.value}"
    
    if grupo.cupo_actual is not None and grupo.cupo_maximo is not None:
        if grupo.cupo_actual >= grupo.cupo_maximo: # type: ignore
            return False, "El grupo no tiene cupos disponibles"
    
    inscripcion_existente = db.query(Inscripcion).filter(
        and_(
            Inscripcion.estudiante_id == estudiante_id,
            Inscripcion.grupo_id == grupo_id,
            Inscripcion.estado != EstadoInscripcion.CANCELADO
        )
    ).first()
    
    if inscripcion_existente:
        return False, "El estudiante ya está inscrito en este grupo"
    
    return True, "El estudiante puede inscribirse en el grupo"
