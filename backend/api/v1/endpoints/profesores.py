"""
Endpoints para Profesores

Gestiona los perfiles de profesores, consultas académicas, carga académica
y estadísticas.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_superadmin, require_roles
from models.usuario import Usuario
from schemas.profesor import (
    ProfesorCreate,
    ProfesorUpdate,
    ProfesorPublic,
    ProfesorConUsuario
)
from services import profesor_service
from models.grupo import EstadoGrupo


router = APIRouter()


@router.post(
    "/",
    response_model=ProfesorPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear perfil de profesor"
)
def crear_perfil_profesor(
    profesor: ProfesorCreate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    """
    Crea un perfil de profesor para un usuario.
    
    **Parámetros:**
    - **usuario_id**: ID del usuario asociado (requerido)
    - **documento**: Número de documento de identidad (opcional)
    - **tipo_documento**: Tipo de documento (opcional)
    - **facultad_id**: ID de la facultad (opcional)
    - **titulo_academico**: Título académico (opcional)
    
    **Validaciones:**
    - El usuario debe existir y tener rol de profesor
    - El usuario no debe tener ya un perfil de profesor
    - La facultad debe existir (si se proporciona)
    
    **Retorna:** Perfil de profesor creado
    
    **Errores:**
    - 400: Datos inválidos o usuario ya tiene perfil
    - 404: Usuario o facultad no encontrado
    """
    try:
        nuevo_profesor = profesor_service.crear_perfil_profesor(
            db=db,
            datos_profesor=profesor.model_dump()
        )
        return nuevo_profesor
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear perfil de profesor: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[ProfesorPublic],
    summary="Listar profesores"
)
def listar_profesores(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros"),
    facultad_id: Optional[int] = Query(None, description="Filtrar por facultad"),
    busqueda: Optional[str] = Query(None, description="Buscar por nombre, apellido o documento"),
    solo_activos: bool = Query(True, description="Solo profesores con usuario activo"),
    db: Session = Depends(get_db)
):
    """
    Lista profesores con filtros opcionales.
    
    **Filtros disponibles:**
    - **facultad_id**: Filtrar por facultad
    - **busqueda**: Buscar por nombre, apellido o documento
    - **solo_activos**: Solo incluir profesores con usuario activo
    
    **Paginación:**
    - **skip**: Número de registros a omitir
    - **limit**: Máximo de registros a retornar (máx: 500)
    
    **Retorna:** Lista de profesores
    """
    try:
        profesores = profesor_service.listar_profesores(
            db=db,
            skip=skip,
            limit=limit,
            facultad_id=facultad_id,
            busqueda=busqueda,
            solo_activos=solo_activos
        )
        return profesores
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar profesores: {str(e)}"
        )


@router.get(
    "/facultad/{facultad_id}",
    response_model=List[ProfesorPublic],
    summary="Obtener profesores por facultad"
)
def obtener_profesores_por_facultad(
    facultad_id: int,
    solo_activos: bool = Query(True, description="Solo profesores activos"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los profesores de una facultad.
    
    **Parámetros:**
    - **facultad_id**: ID de la facultad
    - **solo_activos**: Solo incluir profesores activos
    
    **Retorna:** Lista de profesores de la facultad
    """
    try:
        profesores = profesor_service.obtener_profesores_por_facultad(
            db=db,
            facultad_id=facultad_id,
            solo_activos=solo_activos
        )
        return profesores
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener profesores de la facultad: {str(e)}"
        )


@router.get(
    "/buscar",
    response_model=List[ProfesorPublic],
    summary="Buscar profesores"
)
def buscar_profesores(
    termino: str = Query(..., min_length=1, description="Término de búsqueda"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Busca profesores por nombre, apellido, documento o título académico.
    
    **Parámetros:**
    - **termino**: Término de búsqueda (requerido)
    - **limit**: Máximo de resultados
    
    **Búsqueda:**
    - Busca en nombre del usuario
    - Busca en apellido del usuario
    - Busca en documento
    - Busca en título académico
    - No distingue mayúsculas/minúsculas
    - Soporta búsqueda parcial
    
    **Retorna:** Lista de profesores que coinciden
    """
    try:
        profesores = profesor_service.buscar_profesores(db, termino, limit)
        return profesores
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar profesores: {str(e)}"
        )


@router.get(
    "/usuario/{usuario_id}",
    response_model=ProfesorPublic,
    summary="Obtener profesor por usuario"
)
def obtener_profesor_por_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el perfil de profesor asociado a un usuario.
    
    **Parámetros:**
    - **usuario_id**: ID del usuario
    
    **Retorna:** Perfil de profesor
    
    **Errores:**
    - 404: Usuario no tiene perfil de profesor
    """
    profesor = profesor_service.obtener_profesor_por_usuario_id(db, usuario_id)
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró perfil de profesor para el usuario {usuario_id}"
        )
    return profesor


@router.get(
    "/{profesor_id}",
    response_model=ProfesorPublic,
    summary="Obtener profesor por ID"
)
def obtener_profesor(
    profesor_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un profesor por su ID.
    
    **Parámetros:**
    - **profesor_id**: ID del profesor
    
    **Retorna:** Datos del profesor
    
    **Errores:**
    - 404: Profesor no encontrado
    """
    profesor = profesor_service.obtener_profesor_por_id(db, profesor_id)
    if not profesor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesor con ID {profesor_id} no encontrado"
        )
    return profesor


@router.get(
    "/{profesor_id}/completo",
    response_model=ProfesorConUsuario,
    summary="Obtener perfil completo del profesor"
)
def obtener_perfil_completo(
    profesor_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el perfil completo de un profesor incluyendo:
    - Datos básicos del profesor
    - Información del usuario (nombre, correo, teléfono)
    - Información de la facultad
    
    **Parámetros:**
    - **profesor_id**: ID del profesor
    
    **Retorna:** Perfil completo con datos del usuario y facultad
    
    **Errores:**
    - 404: Profesor no encontrado
    """
    try:
        perfil = profesor_service.obtener_perfil_completo_profesor(db, profesor_id)
        if not perfil:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profesor con ID {profesor_id} no encontrado"
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
    "/{profesor_id}/grupos",
    summary="Obtener grupos asignados"
)
def obtener_grupos_asignados(
    profesor_id: int,
    semestre: Optional[str] = Query(None, description="Filtrar por semestre"),
    estado: Optional[EstadoGrupo] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los grupos asignados a un profesor.
    
    **Parámetros:**
    - **profesor_id**: ID del profesor
    - **semestre**: Filtrar por semestre (opcional)
    - **estado**: Filtrar por estado del grupo (opcional)
    
    **Retorna:** Lista de grupos con información del curso y horarios
    
    **Útil para:** Ver la carga académica de un profesor
    """
    try:
        grupos = profesor_service.obtener_grupos_asignados(
            db=db,
            profesor_id=profesor_id,
            semestre=semestre,
            estado=estado
        )
        return grupos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener grupos asignados: {str(e)}"
        )


@router.get(
    "/{profesor_id}/grupos-activos",
    summary="Obtener grupos activos"
)
def obtener_grupos_activos(
    profesor_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene los grupos activos (en curso o abiertos) de un profesor.
    
    **Parámetros:**
    - **profesor_id**: ID del profesor
    
    **Retorna:** Lista de grupos activos con información completa
    
    **Estados incluidos:**
    - Abierto: Grupo aceptando inscripciones
    - En Curso: Clases en progreso
    
    **Útil para:** Ver cursos actuales del profesor
    """
    try:
        grupos = profesor_service.obtener_grupos_activos(db, profesor_id)
        return grupos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener grupos activos: {str(e)}"
        )


@router.get(
    "/{profesor_id}/carga-academica",
    summary="Obtener carga académica"
)
def obtener_carga_academica(
    profesor_id: int,
    semestre: str = Query(..., description="Semestre"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la carga académica completa de un profesor en un semestre.
    
    **Parámetros:**
    - **profesor_id**: ID del profesor
    - **semestre**: Semestre a consultar (requerido)
    
    **Retorna:**
    - **semestre**: Periodo académico
    - **total_grupos**: Número de grupos asignados
    - **total_estudiantes**: Suma de estudiantes en todos los grupos
    - **total_horas_semanales**: Horas de clase por semana
    - **grupos**: Detalle de cada grupo con curso, horarios y estudiantes
    
    **Útil para:** Planificación, reportes de carga docente
    """
    try:
        carga = profesor_service.obtener_carga_academica(db, profesor_id, semestre)
        return carga
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener carga académica: {str(e)}"
        )


@router.get(
    "/{profesor_id}/estadisticas",
    summary="Obtener estadísticas del profesor"
)
def obtener_estadisticas(
    profesor_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas generales de un profesor.
    
    **Parámetros:**
    - **profesor_id**: ID del profesor
    
    **Retorna:**
    - **total_grupos_dictados**: Total histórico de grupos
    - **grupos_activos**: Grupos actuales (abiertos o en curso)
    - **total_estudiantes_actuales**: Estudiantes en grupos activos
    - **semestres_activo**: Cantidad de semestres en que ha dictado
    
    **Útil para:** Perfil del profesor, evaluación docente
    """
    try:
        estadisticas = profesor_service.obtener_estadisticas_profesor(db, profesor_id)
        return estadisticas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.put(
    "/{profesor_id}",
    response_model=ProfesorPublic,
    summary="Actualizar profesor"
)
def actualizar_profesor(
    profesor_id: int,
    datos_actualizados: ProfesorUpdate,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    """
    Actualiza los datos de un profesor.
    
    **Campos actualizables:**
    - **documento**: Número de documento
    - **tipo_documento**: Tipo de documento
    - **facultad_id**: Cambiar de facultad
    - **titulo_academico**: Actualizar título académico
    
    **Parámetros:**
    - **profesor_id**: ID del profesor
    - **datos_actualizados**: Campos a actualizar
    
    **Retorna:** Profesor actualizado
    
    **Errores:**
    - 400: Datos inválidos
    - 404: Profesor o facultad no encontrado
    """
    try:
        profesor_actualizado = profesor_service.actualizar_profesor(
            db=db,
            profesor_id=profesor_id,
            datos_actualizados=datos_actualizados.model_dump(exclude_unset=True) # type: ignore
        )
        return profesor_actualizado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar profesor: {str(e)}"
        )


@router.delete(
    "/{profesor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar profesor"
)
def eliminar_profesor(
    profesor_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    """
    Elimina un profesor del sistema.
    
    **Nota:** Esta operación eliminará el perfil de profesor
    pero no el usuario asociado.
    
    **Parámetros:**
    - **profesor_id**: ID del profesor
    
    **Retorna:** 204 No Content si se eliminó correctamente
    
    **Errores:**
    - 404: Profesor no encontrado
    """
    eliminado = profesor_service.eliminar_profesor(db, profesor_id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profesor con ID {profesor_id} no encontrado"
        )
    return None
