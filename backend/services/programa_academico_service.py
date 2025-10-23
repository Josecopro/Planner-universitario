"""
Servicio de Programa Académico
Lógica de negocio para gestión de programas académicos (carreras)
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from models.programa_academico import ProgramaAcademico, EstadoPrograma
from models.facultad import Facultad
from models.estudiante import Estudiante
from models.inscripcion import Inscripcion


def crear_programa(
    db: Session,
    datos_programa: Dict[str, Any]
) -> ProgramaAcademico:
    """
    Crea un nuevo programa académico.
    
    Args:
        db: Sesión de base de datos
        datos_programa: Diccionario con los datos del programa
            - nombre: str (requerido)
            - codigo: str (requerido, único)
            - facultad_id: int (requerido)
            - duracion_semestres: int (opcional)
            - estado: EstadoPrograma (opcional, default: ACTIVO)
    
    Returns:
        ProgramaAcademico: El programa creado
    
    Raises:
        ValueError: Si la facultad no existe o el código ya está en uso
        IntegrityError: Si se viola la constraint de unicidad del código
    """
    facultad_id = datos_programa["facultad_id"]
    codigo = datos_programa["codigo"]
    
    facultad = db.query(Facultad).filter(Facultad.id == facultad_id).first()
    
    if not facultad:
        raise ValueError(f"Facultad con ID {facultad_id} no encontrada")
    
    programa_existente = db.query(ProgramaAcademico)\
        .filter(ProgramaAcademico.codigo == codigo)\
        .first()
    
    if programa_existente:
        raise ValueError(f"Ya existe un programa con el código '{codigo}'")
    
    nuevo_programa = ProgramaAcademico(
        nombre=datos_programa["nombre"],
        codigo=codigo,
        facultad_id=facultad_id,
        duracion_semestres=datos_programa.get("duracion_semestres"),
        estado=datos_programa.get("estado", EstadoPrograma.ACTIVO)
    )
    
    try:
        db.add(nuevo_programa)
        db.commit()
        db.refresh(nuevo_programa)
    except IntegrityError:
        db.rollback()
        raise ValueError(f"Error de integridad: El código '{codigo}' ya está en uso")
    
    return nuevo_programa


def obtener_programas(
    db: Session,
    estado: Optional[EstadoPrograma] = None
) -> List[ProgramaAcademico]:
    """
    Obtiene todos los programas académicos.
    
    Args:
        db: Sesión de base de datos
        estado: Filtrar por estado (opcional)
    
    Returns:
        List[ProgramaAcademico]: Lista de programas académicos
    """
    query = db.query(ProgramaAcademico)
    
    if estado:
        query = query.filter(ProgramaAcademico.estado == estado)
    
    return query.order_by(ProgramaAcademico.nombre).all()


def obtener_programas_por_facultad(
    db: Session,
    facultad_id: int
) -> List[ProgramaAcademico]:
    """
    Obtiene todos los programas académicos de una facultad específica.
    
    Args:
        db: Sesión de base de datos
        facultad_id: ID de la facultad
    
    Returns:
        List[ProgramaAcademico]: Lista de programas de la facultad
    """
    return db.query(ProgramaAcademico)\
        .filter(ProgramaAcademico.facultad_id == facultad_id)\
        .order_by(ProgramaAcademico.nombre)\
        .all()


def obtener_programa_por_id(
    db: Session,
    programa_id: int
) -> Optional[ProgramaAcademico]:
    """
    Obtiene un programa académico por su ID con todas sus relaciones.
    
    Args:
        db: Sesión de base de datos
        programa_id: ID del programa
    
    Returns:
        ProgramaAcademico | None: El programa o None si no existe
    """
    return db.query(ProgramaAcademico)\
        .filter(ProgramaAcademico.id == programa_id)\
        .first()


def actualizar_programa(
    db: Session,
    programa_id: int,
    datos_actualizados: Dict[str, Any]
) -> Optional[ProgramaAcademico]:
    """
    Actualiza los datos de un programa académico.
    
    Args:
        db: Sesión de base de datos
        programa_id: ID del programa a actualizar
        datos_actualizados: Diccionario con los campos a actualizar
            Campos permitidos: nombre, codigo, duracion_semestres, estado
    
    Returns:
        ProgramaAcademico | None: El programa actualizado o None si no existe
    
    Raises:
        ValueError: Si el nuevo código ya está en uso
    """
    programa = db.query(ProgramaAcademico)\
        .filter(ProgramaAcademico.id == programa_id)\
        .first()
    
    if not programa:
        return None
    
    # Verificar código si se está actualizando
    if "codigo" in datos_actualizados:
        nuevo_codigo = datos_actualizados["codigo"]
        if nuevo_codigo != programa.codigo:  # type: ignore
            codigo_existente = db.query(ProgramaAcademico)\
                .filter(
                    and_(
                        ProgramaAcademico.codigo == nuevo_codigo,
                        ProgramaAcademico.id != programa_id
                    )
                )\
                .first()
            
            if codigo_existente:
                raise ValueError(f"Ya existe un programa con el código '{nuevo_codigo}'")
    
    campos_permitidos = ["nombre", "codigo", "duracion_semestres", "estado"]
    
    for campo, valor in datos_actualizados.items():
        if campo in campos_permitidos and hasattr(programa, campo):
            setattr(programa, campo, valor)
    
    db.commit()
    db.refresh(programa)
    
    return programa


def obtener_estudiantes_por_programa(
    db: Session,
    programa_id: int,
    semestre: Optional[str] = None
) -> List[Estudiante]:
    """
    Obtiene los estudiantes inscritos en un programa académico.
    
    Args:
        db: Sesión de base de datos
        programa_id: ID del programa
        semestre: Filtrar por estudiantes activos en un semestre específico (opcional)
    
    Returns:
        List[Estudiante]: Lista de estudiantes del programa
    """
    query = db.query(Estudiante)\
        .filter(Estudiante.programa_id == programa_id)
    
    if semestre:
        from models.grupo import Grupo
        query = query.join(Inscripcion, Inscripcion.estudiante_id == Estudiante.id)\
            .join(Grupo, Inscripcion.grupo_id == Grupo.id)\
            .filter(Grupo.semestre == semestre)\
            .distinct()
    
    return query.order_by(Estudiante.id).all()


def obtener_programa_por_codigo(
    db: Session,
    codigo: str
) -> Optional[ProgramaAcademico]:
    """
    Obtiene un programa académico por su código único.
    
    Args:
        db: Sesión de base de datos
        codigo: Código del programa
    
    Returns:
        ProgramaAcademico | None: El programa o None si no existe
    """
    return db.query(ProgramaAcademico)\
        .filter(ProgramaAcademico.codigo == codigo)\
        .first()


def programa_existe(
    db: Session,
    programa_id: int
) -> bool:
    """
    Verifica si un programa académico existe.
    
    Args:
        db: Sesión de base de datos
        programa_id: ID del programa
    
    Returns:
        bool: True si existe, False en caso contrario
    """
    return db.query(ProgramaAcademico)\
        .filter(ProgramaAcademico.id == programa_id)\
        .first() is not None


def codigo_programa_existe(
    db: Session,
    codigo: str,
    excluir_id: Optional[int] = None
) -> bool:
    """
    Verifica si un código de programa ya está en uso.
    
    Args:
        db: Sesión de base de datos
        codigo: Código a verificar
        excluir_id: ID de programa a excluir de la búsqueda (opcional)
    
    Returns:
        bool: True si el código existe, False en caso contrario
    """
    query = db.query(ProgramaAcademico)\
        .filter(ProgramaAcademico.codigo == codigo)
    
    if excluir_id:
        query = query.filter(ProgramaAcademico.id != excluir_id)
    
    return query.first() is not None


def contar_estudiantes_programa(
    db: Session,
    programa_id: int
) -> int:
    """
    Cuenta el número de estudiantes inscritos en un programa.
    
    Args:
        db: Sesión de base de datos
        programa_id: ID del programa
    
    Returns:
        int: Número de estudiantes
    """
    return db.query(Estudiante)\
        .filter(Estudiante.programa_id == programa_id)\
        .count()


def cambiar_estado_programa(
    db: Session,
    programa_id: int,
    nuevo_estado: EstadoPrograma
) -> Optional[ProgramaAcademico]:
    """
    Cambia el estado de un programa académico.
    
    Args:
        db: Sesión de base de datos
        programa_id: ID del programa
        nuevo_estado: Nuevo estado del programa
    
    Returns:
        ProgramaAcademico | None: El programa actualizado o None si no existe
    """
    programa = db.query(ProgramaAcademico)\
        .filter(ProgramaAcademico.id == programa_id)\
        .first()
    
    if not programa:
        return None
    
    programa.estado = nuevo_estado  # type: ignore
    db.commit()
    db.refresh(programa)
    
    return programa


def obtener_programas_activos(
    db: Session,
    facultad_id: Optional[int] = None
) -> List[ProgramaAcademico]:
    """
    Obtiene todos los programas académicos activos.
    
    Args:
        db: Sesión de base de datos
        facultad_id: Filtrar por facultad (opcional)
    
    Returns:
        List[ProgramaAcademico]: Lista de programas activos
    """
    query = db.query(ProgramaAcademico)\
        .filter(ProgramaAcademico.estado == EstadoPrograma.ACTIVO)
    
    if facultad_id:
        query = query.filter(ProgramaAcademico.facultad_id == facultad_id)
    
    return query.order_by(ProgramaAcademico.nombre).all()


def eliminar_programa(
    db: Session,
    programa_id: int
) -> bool:
    """
    Elimina un programa académico.
    
    Nota: Fallará si hay estudiantes asociados debido al cascade delete-orphan.
    
    Args:
        db: Sesión de base de datos
        programa_id: ID del programa a eliminar
    
    Returns:
        bool: True si se eliminó, False si no se encontró
    
    Raises:
        ValueError: Si hay estudiantes asociados al programa
    """
    programa = db.query(ProgramaAcademico)\
        .filter(ProgramaAcademico.id == programa_id)\
        .first()
    
    if not programa:
        return False
    
    num_estudiantes = contar_estudiantes_programa(db, programa_id)
    if num_estudiantes > 0:
        raise ValueError(
            f"No se puede eliminar el programa porque tiene {num_estudiantes} estudiante(s) asociado(s)"
        )
    
    db.delete(programa)
    db.commit()
    
    return True


def obtener_estadisticas_programa(
    db: Session,
    programa_id: int
) -> Dict[str, Any]:
    """
    Obtiene estadísticas de un programa académico.
    
    Args:
        db: Sesión de base de datos
        programa_id: ID del programa
    
    Returns:
        Dict: Diccionario con estadísticas
            - programa: Objeto ProgramaAcademico
            - total_estudiantes: Total de estudiantes en el programa
            - estudiantes_activos: Estudiantes con inscripciones activas
            - duracion_semestres: Duración del programa
    """
    programa = obtener_programa_por_id(db, programa_id)
    
    if not programa:
        return {
            "programa": None,
            "total_estudiantes": 0,
            "estudiantes_activos": 0,
            "duracion_semestres": None
        }
    
    total_estudiantes = contar_estudiantes_programa(db, programa_id)
    
    from models.inscripcion import EstadoInscripcion
    estudiantes_activos = db.query(Estudiante.id)\
        .join(Inscripcion, Inscripcion.estudiante_id == Estudiante.id)\
        .filter(
            and_(
                Estudiante.programa_id == programa_id,
                Inscripcion.estado == EstadoInscripcion.INSCRITO
            )
        )\
        .distinct()\
        .count()
    
    return {
        "programa": programa,
        "total_estudiantes": total_estudiantes,
        "estudiantes_activos": estudiantes_activos,
        "duracion_semestres": programa.duracion_semestres
    }


def buscar_programas(
    db: Session,
    termino_busqueda: str,
    facultad_id: Optional[int] = None,
    estado: Optional[EstadoPrograma] = None
) -> List[ProgramaAcademico]:
    """
    Busca programas por nombre o código.
    
    Args:
        db: Sesión de base de datos
        termino_busqueda: Término a buscar en nombre o código
        facultad_id: Filtrar por facultad (opcional)
        estado: Filtrar por estado (opcional)
    
    Returns:
        List[ProgramaAcademico]: Lista de programas que coinciden con la búsqueda
    """
    termino = f"%{termino_busqueda}%"
    
    query = db.query(ProgramaAcademico)\
        .filter(
            (ProgramaAcademico.nombre.ilike(termino)) |  # type: ignore
            (ProgramaAcademico.codigo.ilike(termino))  # type: ignore
        )
    
    if facultad_id:
        query = query.filter(ProgramaAcademico.facultad_id == facultad_id)
    
    if estado:
        query = query.filter(ProgramaAcademico.estado == estado)
    
    return query.order_by(ProgramaAcademico.nombre).all()


def obtener_programas_con_conteo_estudiantes(
    db: Session,
    facultad_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Obtiene programas con el conteo de estudiantes.
    
    Args:
        db: Sesión de base de datos
        facultad_id: Filtrar por facultad (opcional)
    
    Returns:
        List[Dict]: Lista de diccionarios con programa y conteo de estudiantes
    """
    query = db.query(ProgramaAcademico)
    
    if facultad_id:
        query = query.filter(ProgramaAcademico.facultad_id == facultad_id)
    
    programas = query.all()
    
    resultado = []
    for programa in programas:
        num_estudiantes = contar_estudiantes_programa(db, programa.id)  # type: ignore
        resultado.append({
            "programa": programa,
            "total_estudiantes": num_estudiantes
        })
    
    return resultado
