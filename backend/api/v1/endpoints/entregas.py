"""
Endpoints de API para Entregas
Rutas: /api/v1/entregas
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_superadmin, get_current_user, require_roles
from models.usuario import Usuario
from schemas.entrega import (
    EntregaCreate,
    EntregaUpdate,
    EntregaPublic,
    EntregaList
)
from services import entrega_service
from models.entrega import EstadoEntrega


router = APIRouter()


@router.post(
    "/",
    response_model=EntregaPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Realizar entrega",
    description="Registra la entrega de un estudiante para una actividad evaluativa"
)
def realizar_entrega(
    entrega_data: EntregaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Registra una entrega de actividad evaluativa.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad a entregar
    - **inscripcion_id**: ID de la inscripción del estudiante
    - **texto_entrega**: Contenido de texto de la entrega (opcional)
    - **archivos_adjuntos**: Lista de URLs de archivos (opcional)
    
    **Retorna:**
    - Entrega creada con su ID, fecha y estado
    - Estado automático: "Entregada" si es a tiempo, "Entregada Tarde" si está atrasado
    
    **Excepciones:**
    - **404**: Actividad o inscripción no encontrada
    - **400**: Ya existe una entrega para esta actividad
    """
    try:
        entrega = entrega_service.realizar_entrega(
            db=db,
            datos_entrega=entrega_data.model_dump()
        )
        return entrega
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al realizar entrega: {str(e)}"
        )


@router.get(
    "/actividad/{actividad_id}",
    response_model=List[EntregaPublic],
    summary="Obtener entregas de una actividad",
    description="Obtiene todas las entregas de una actividad evaluativa"
)
def obtener_entregas_actividad(
    actividad_id: int,
    estado: Optional[EstadoEntrega] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Obtiene las entregas de una actividad.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad evaluativa
    
    **Parámetros de Query:**
    - **estado**: Filtrar por estado (Entregada, Entregada Tarde, Calificada)
    
    **Retorna:**
    - Lista de entregas de la actividad
    """
    try:
        if estado:
            entregas = entrega_service.obtener_entregas_por_estado(
                db=db,
                actividad_id=actividad_id,
                estado=estado
            )
        else:
            entregas = entrega_service.obtener_entregas_por_actividad(
                db=db,
                actividad_id=actividad_id
            )
        return entregas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas: {str(e)}"
        )


@router.get(
    "/actividad/{actividad_id}/tardias",
    response_model=List[EntregaPublic],
    summary="Obtener entregas tardías",
    description="Obtiene las entregas tardías de una actividad"
)
def obtener_entregas_tardias(
    actividad_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene las entregas tardías de una actividad.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad evaluativa
    
    **Retorna:**
    - Lista de entregas con estado "Entregada Tarde"
    """
    try:
        entregas = entrega_service.obtener_entregas_tardias(
            db=db,
            actividad_id=actividad_id
        )
        return entregas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas tardías: {str(e)}"
        )


@router.get(
    "/actividad/{actividad_id}/estudiante/{inscripcion_id}",
    response_model=Optional[EntregaPublic],
    summary="Obtener entrega de un estudiante",
    description="Obtiene la entrega de un estudiante específico para una actividad"
)
def obtener_entrega_estudiante(
    actividad_id: int,
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene la entrega de un estudiante para una actividad.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad
    - **inscripcion_id**: ID de la inscripción del estudiante
    
    **Retorna:**
    - Entrega del estudiante o null si no ha entregado
    """
    entrega = entrega_service.obtener_entrega_de_estudiante(
        db=db,
        actividad_id=actividad_id,
        inscripcion_id=inscripcion_id
    )
    return entrega


@router.get(
    "/grupo/{grupo_id}/pendientes",
    response_model=List[EntregaPublic],
    summary="Obtener entregas pendientes de calificar",
    description="Obtiene todas las entregas de un grupo que no han sido calificadas"
)
def obtener_entregas_pendientes_calificar(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene entregas pendientes de calificación de un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Retorna:**
    - Lista de entregas sin calificación
    
    **Uso:** Para que profesores vean qué entregas deben calificar
    """
    try:
        entregas = entrega_service.obtener_entregas_pendientes_por_calificar(
            db=db,
            grupo_id=grupo_id
        )
        return entregas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas pendientes: {str(e)}"
        )


@router.get(
    "/inscripcion/{inscripcion_id}",
    response_model=List[EntregaPublic],
    summary="Obtener entregas de un estudiante",
    description="Obtiene todas las entregas de un estudiante en un grupo"
)
def obtener_entregas_estudiante(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las entregas de un estudiante.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción del estudiante
    
    **Retorna:**
    - Lista de entregas del estudiante en el grupo
    
    **Uso:** Ver historial de entregas del estudiante
    """
    try:
        entregas = entrega_service.obtener_entregas_de_estudiante(
            db=db,
            inscripcion_id=inscripcion_id
        )
        return entregas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas: {str(e)}"
        )


@router.get(
    "/estadisticas/actividad/{actividad_id}",
    response_model=dict,
    summary="Obtener estadísticas de entregas",
    description="Obtiene estadísticas de entregas de una actividad evaluativa"
)
def obtener_estadisticas_entregas(
    actividad_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de entregas de una actividad.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad evaluativa
    
    **Retorna:**
    - Diccionario con estadísticas:
        - total_estudiantes: Total de estudiantes inscritos
        - total_entregas: Entregas realizadas
        - pendientes: Estudiantes sin entregar
        - entregadas_tiempo: Entregas a tiempo
        - entregadas_tarde: Entregas tardías
        - calificadas: Entregas ya calificadas
        - porcentaje_entrega: % de estudiantes que entregaron
    """
    try:
        estadisticas = entrega_service.obtener_estadisticas_entregas(
            db=db,
            actividad_id=actividad_id
        )
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
    "/{entrega_id}",
    response_model=EntregaPublic,
    summary="Obtener entrega por ID",
    description="Obtiene una entrega específica por su ID"
)
def obtener_entrega(
    entrega_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una entrega por su ID.
    
    **Parámetros:**
    - **entrega_id**: ID de la entrega
    
    **Retorna:**
    - Entrega con todos sus detalles
    
    **Excepciones:**
    - **404**: Entrega no encontrada
    """
    entrega = entrega_service.obtener_entrega_por_id(
        db=db,
        entrega_id=entrega_id
    )
    if not entrega:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entrega con ID {entrega_id} no encontrada"
        )
    return entrega


@router.put(
    "/{entrega_id}",
    response_model=EntregaPublic,
    summary="Actualizar entrega",
    description="Actualiza una entrega existente (solo si no está calificada)"
)
def actualizar_entrega(
    entrega_id: int,
    entrega_data: EntregaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza una entrega existente.
    
    **Parámetros:**
    - **entrega_id**: ID de la entrega a actualizar
    - **entrega_data**: Datos a actualizar:
        - texto_entrega: Nuevo texto
        - archivos_adjuntos: Nuevos archivos
    
    **Retorna:**
    - Entrega actualizada
    
    **Excepciones:**
    - **404**: Entrega no encontrada
    - **400**: No se puede actualizar (ya está calificada)
    
    **Nota:** Solo se pueden actualizar entregas que no han sido calificadas
    """
    try:
        datos_actualizacion = entrega_data.model_dump(exclude_unset=True)
        datos_actualizacion["entrega_id"] = entrega_id
        
        entrega = entrega_service.actualizar_entrega(
            db=db,
            datos_actualizacion=datos_actualizacion
        )
        if not entrega:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entrega con ID {entrega_id} no encontrada"
            )
        return entrega
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar entrega: {str(e)}"
        )


@router.delete(
    "/{entrega_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar entrega",
    description="Elimina una entrega (solo si no está calificada)"
)
def eliminar_entrega(
    entrega_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina una entrega.
    
    **Parámetros:**
    - **entrega_id**: ID de la entrega a eliminar
    
    **Retorna:**
    - 204 No Content si se elimina exitosamente
    
    **Excepciones:**
    - **404**: Entrega no encontrada
    - **400**: No se puede eliminar (ya está calificada)
    """
    try:
        success = entrega_service.eliminar_entrega(
            db=db,
            entrega_id=entrega_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Entrega con ID {entrega_id} no encontrada"
            )
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar entrega: {str(e)}"
        )
