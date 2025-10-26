"""
Endpoints para Estudiantes

Gestiona los perfiles de estudiantes, consultas académicas y estadísticas.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.estudiante import (
    EstudianteCreate,
    EstudianteUpdate,
    EstudiantePublic,
    EstudianteCompleto,
    EstudianteConUsuario
)
from services import estudiante_service
from models.estudiante import EstadoAcademicoEstudiante
from models.inscripcion import EstadoInscripcion


router = APIRouter()


@router.post(
    "/",
    response_model=EstudiantePublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear perfil de estudiante"
)
def crear_perfil_estudiante(
    estudiante: EstudianteCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un perfil de estudiante para un usuario.
    
    **Parámetros:**
    - **usuario_id**: ID del usuario asociado (requerido)
    - **programa_id**: ID del programa académico (requerido)
    - **documento**: Número de documento de identidad (opcional)
    - **tipo_documento**: Tipo de documento (opcional)
    
    **Validaciones:**
    - El usuario debe existir y tener rol de estudiante
    - El usuario no debe tener ya un perfil de estudiante
    - El programa académico debe existir
    
    **Retorna:** Perfil de estudiante creado
    
    **Errores:**
    - 400: Datos inválidos o usuario ya tiene perfil
    - 404: Usuario o programa no encontrado
    """
    try:
        nuevo_estudiante = estudiante_service.crear_perfil_estudiante(
            db=db,
            datos_estudiante=estudiante.model_dump()
        )
        return nuevo_estudiante
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear perfil de estudiante: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[EstudiantePublic],
    summary="Listar estudiantes"
)
def listar_estudiantes(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    programa_id: Optional[int] = Query(None, description="Filtrar por programa"),
    estado_academico: Optional[EstadoAcademicoEstudiante] = Query(None, description="Filtrar por estado académico"),
    busqueda: Optional[str] = Query(None, description="Buscar por nombre, apellido o documento"),
    solo_activos: bool = Query(True, description="Solo estudiantes con usuario activo"),
    db: Session = Depends(get_db)
):
    """
    Lista estudiantes con filtros opcionales.
    
    **Filtros disponibles:**
    - **programa_id**: Filtrar por programa académico
    - **estado_academico**: Filtrar por estado (Matriculado, Graduado, etc.)
    - **busqueda**: Buscar por nombre, apellido o documento
    - **solo_activos**: Solo incluir estudiantes con usuario activo
    
    **Paginación:**
    - **skip**: Número de registros a omitir
    - **limit**: Máximo de registros a retornar (máx: 500)
    
    **Retorna:** Lista de estudiantes
    """
    try:
        estudiantes = estudiante_service.listar_estudiantes(
            db=db,
            skip=skip,
            limit=limit,
            programa_id=programa_id,
            estado_academico=estado_academico,
            busqueda=busqueda,
            solo_activos=solo_activos
        )
        return estudiantes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar estudiantes: {str(e)}"
        )


@router.get(
    "/programa/{programa_id}",
    response_model=List[EstudiantePublic],
    summary="Obtener estudiantes por programa"
)
def obtener_estudiantes_por_programa(
    programa_id: int,
    estado_academico: Optional[EstadoAcademicoEstudiante] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los estudiantes de un programa académico.
    
    **Parámetros:**
    - **programa_id**: ID del programa académico
    - **estado_academico**: Filtrar por estado (opcional)
    
    **Retorna:** Lista de estudiantes del programa
    """
    try:
        estudiantes = estudiante_service.obtener_estudiantes_por_programa(
            db=db,
            programa_id=programa_id,
            estado_academico=estado_academico
        )
        return estudiantes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estudiantes del programa: {str(e)}"
        )


@router.get(
    "/buscar",
    response_model=List[EstudiantePublic],
    summary="Buscar estudiantes"
)
def buscar_estudiantes(
    grupo_id: Optional[int] = Query(None, description="Filtrar por grupo"),
    nombre: Optional[str] = Query(None, description="Buscar por nombre"),
    estado: Optional[EstadoAcademicoEstudiante] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Busca estudiantes con múltiples criterios.
    
    **Criterios de búsqueda:**
    - **grupo_id**: Filtrar estudiantes inscritos en un grupo específico
    - **nombre**: Buscar por nombre o apellido (búsqueda parcial)
    - **estado**: Filtrar por estado académico
    
    **Retorna:** Lista de estudiantes que coinciden con los criterios
    """
    try:
        estudiantes = estudiante_service.buscar_estudiantes(
            db=db,
            grupo_id=grupo_id,
            nombre=nombre,
            estado=estado,
            limit=limit
        )
        return estudiantes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar estudiantes: {str(e)}"
        )


@router.get(
    "/usuario/{usuario_id}",
    response_model=EstudiantePublic,
    summary="Obtener estudiante por usuario"
)
def obtener_estudiante_por_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el perfil de estudiante asociado a un usuario.
    
    **Parámetros:**
    - **usuario_id**: ID del usuario
    
    **Retorna:** Perfil de estudiante
    
    **Errores:**
    - 404: Usuario no tiene perfil de estudiante
    """
    estudiante = estudiante_service.obtener_estudiante_por_usuario_id(db, usuario_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró perfil de estudiante para el usuario {usuario_id}"
        )
    return estudiante


@router.get(
    "/{estudiante_id}",
    response_model=EstudiantePublic,
    summary="Obtener estudiante por ID"
)
def obtener_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un estudiante por su ID.
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    
    **Retorna:** Datos del estudiante
    
    **Errores:**
    - 404: Estudiante no encontrado
    """
    estudiante = estudiante_service.obtener_estudiante_por_id(db, estudiante_id)
    if not estudiante:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {estudiante_id} no encontrado"
        )
    return estudiante


@router.get(
    "/{estudiante_id}/completo",
    response_model=EstudianteCompleto,
    summary="Obtener perfil completo del estudiante"
)
def obtener_perfil_completo(
    estudiante_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el perfil completo de un estudiante incluyendo:
    - Datos básicos del estudiante
    - Información del usuario (nombre, correo, avatar)
    - Información del programa académico
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    
    **Retorna:** Perfil completo con datos del usuario y programa
    
    **Errores:**
    - 404: Estudiante no encontrado
    """
    try:
        perfil = estudiante_service.obtener_perfil_completo_estudiante(db, estudiante_id)
        if not perfil:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante con ID {estudiante_id} no encontrado"
            )
        return perfil
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener perfil completo: {str(e)}"
        )


@router.get(
    "/{estudiante_id}/inscripciones",
    summary="Obtener inscripciones del estudiante"
)
def obtener_inscripciones(
    estudiante_id: int,
    semestre: Optional[str] = Query(None, description="Filtrar por semestre"),
    estado: Optional[EstadoInscripcion] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Obtiene las inscripciones de un estudiante.
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    - **semestre**: Filtrar por semestre (formato: "YYYY-S", ej: "2024-2")
    - **estado**: Filtrar por estado de inscripción
    
    **Retorna:** Lista de inscripciones con datos del grupo y curso
    """
    try:
        inscripciones = estudiante_service.obtener_inscripciones_estudiante(
            db=db,
            estudiante_id=estudiante_id,
            semestre=semestre,
            estado=estado
        )
        return inscripciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener inscripciones: {str(e)}"
        )


@router.get(
    "/{estudiante_id}/horario",
    summary="Obtener horario del estudiante"
)
def obtener_horario(
    estudiante_id: int,
    semestre: str = Query(..., description="Semestre (YYYY-S)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene el horario completo de un estudiante en un semestre.
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    - **semestre**: Semestre a consultar (requerido)
    
    **Retorna:** Lista de bloques horarios con información del curso y grupo
    
    **Información incluida:**
    - Horario (día, hora inicio, hora fin, salón)
    - Grupo (número de grupo, profesor)
    - Curso (nombre, código, créditos)
    - Inscripción (estado)
    """
    try:
        horario = estudiante_service.obtener_horario_estudiante(
            db=db,
            estudiante_id=estudiante_id,
            semestre=semestre
        )
        return horario
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener horario: {str(e)}"
        )


@router.get(
    "/{estudiante_id}/estadisticas",
    summary="Obtener estadísticas académicas"
)
def obtener_estadisticas(
    estudiante_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas académicas completas de un estudiante.
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    
    **Retorna:**
    - **total_cursos_inscritos**: Total histórico de inscripciones
    - **cursos_aprobados**: Cursos aprobados
    - **cursos_reprobados**: Cursos reprobados
    - **cursos_en_curso**: Cursos actualmente inscritos
    - **promedio_academico**: Promedio ponderado por créditos
    - **tasa_aprobacion**: Porcentaje de aprobación
    
    **Errores:**
    - 404: Estudiante no encontrado
    """
    try:
        estadisticas = estudiante_service.obtener_estadisticas_estudiante(db, estudiante_id)
        return estadisticas
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get(
    "/{estudiante_id}/promedio",
    summary="Calcular promedio académico"
)
def calcular_promedio(
    estudiante_id: int,
    db: Session = Depends(get_db)
):
    """
    Calcula el promedio académico ponderado de un estudiante.
    
    **Cálculo:**
    - Solo considera cursos aprobados o reprobados (con nota final)
    - Pondera por créditos del curso
    - Fórmula: Σ(nota × créditos) / Σ(créditos)
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    
    **Retorna:** Objeto con el promedio calculado
    """
    try:
        promedio = estudiante_service.calcular_promedio_academico(db, estudiante_id)
        return {"promedio_academico": promedio}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular promedio: {str(e)}"
        )


@router.get(
    "/grupo/{grupo_id}/estudiantes",
    summary="Obtener estudiantes de un grupo"
)
def obtener_estudiantes_grupo(
    grupo_id: int,
    estado_inscripcion: Optional[EstadoInscripcion] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los estudiantes inscritos en un grupo específico.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    - **estado_inscripcion**: Filtrar por estado (opcional)
    
    **Retorna:** Lista de estudiantes con información de inscripción
    
    **Información incluida:**
    - Datos del estudiante
    - Datos de la inscripción (fecha, estado, nota)
    """
    try:
        estudiantes = estudiante_service.obtener_estudiantes_por_grupo(
            db=db,
            grupo_id=grupo_id,
            estado_inscripcion=estado_inscripcion
        )
        return estudiantes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estudiantes del grupo: {str(e)}"
        )


@router.put(
    "/{estudiante_id}",
    response_model=EstudiantePublic,
    summary="Actualizar estudiante"
)
def actualizar_estudiante(
    estudiante_id: int,
    datos_actualizados: EstudianteUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un estudiante.
    
    **Campos actualizables:**
    - **documento**: Número de documento
    - **tipo_documento**: Tipo de documento
    - **programa_id**: Cambiar de programa académico
    - **estado_academico**: Cambiar estado académico
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    - **datos_actualizados**: Campos a actualizar
    
    **Retorna:** Estudiante actualizado
    
    **Errores:**
    - 400: Datos inválidos
    - 404: Estudiante o programa no encontrado
    """
    try:
        estudiante_actualizado = estudiante_service.actualizar_estudiante(
            db=db,
            estudiante_id=estudiante_id,
            datos_actualizados=datos_actualizados.model_dump(exclude_unset=True)
        )
        return estudiante_actualizado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar estudiante: {str(e)}"
        )


@router.delete(
    "/{estudiante_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar estudiante"
)
def eliminar_estudiante(
    estudiante_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un estudiante del sistema.
    
    **Nota:** Esta operación eliminará el perfil de estudiante
    pero no el usuario asociado.
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    
    **Retorna:** 204 No Content si se eliminó correctamente
    
    **Errores:**
    - 404: Estudiante no encontrado
    """
    eliminado = estudiante_service.eliminar_estudiante(db, estudiante_id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con ID {estudiante_id} no encontrado"
        )
    return None
