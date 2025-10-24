"""
Endpoints de API para Calificaciones
Rutas: /api/v1/calificaciones
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.calificacion import (
    CalificacionCreate,
    CalificacionUpdate,
    CalificacionPublic,
    CalificacionCreateBulk,
    CalificacionBulkResponse
)
from services import calificacion_service


router = APIRouter()


@router.post(
    "/",
    response_model=CalificacionPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear calificación",
    description="Crea una calificación para una entrega de actividad evaluativa"
)
def crear_calificacion(
    calificacion_data: CalificacionCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una calificación para una entrega.
    
    **Parámetros:**
    - **entrega_id**: ID de la entrega a calificar
    - **nota_obtenida**: Nota obtenida por el estudiante (>= 0)
    - **retroalimentacion**: Comentarios del profesor (opcional)
    
    **Retorna:**
    - Calificación creada con su ID y fecha
    
    **Excepciones:**
    - **404**: Entrega no encontrada
    - **400**: Entrega ya está calificada o nota inválida
    """
    try:
        calificacion = calificacion_service.crear_calificacion(
            db=db,
            datos_calificacion=calificacion_data.model_dump()
        )
        return calificacion
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear calificación: {str(e)}"
        )


@router.post(
    "/bulk",
    response_model=CalificacionBulkResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Calificar múltiples entregas",
    description="Crea calificaciones para múltiples entregas a la vez"
)
def crear_calificaciones_bulk(
    calificaciones_data: CalificacionCreateBulk,
    db: Session = Depends(get_db)
):
    """
    Crea múltiples calificaciones en una sola operación.
    
    **Parámetros:**
    - **calificaciones**: Lista de objetos con:
        - entrega_id: ID de la entrega
        - nota_obtenida: Nota
        - retroalimentacion: Feedback opcional
    
    **Retorna:**
    - Resumen de la operación con totales y detalles
    
    **Uso:** Ideal para que profesores califiquen todas las entregas de una actividad
    """
    resultados = {
        "total": len(calificaciones_data.calificaciones),
        "exitosas": 0,
        "fallidas": 0,
        "detalles": []
    }
    
    for item in calificaciones_data.calificaciones:
        try:
            calificacion = calificacion_service.crear_calificacion(
                db=db,
                datos_calificacion=item.model_dump()
            )
            resultados["exitosas"] += 1
            resultados["detalles"].append({
                "entrega_id": item.entrega_id,
                "status": "success",
                "calificacion_id": calificacion.id
            })
        except Exception as e:
            resultados["fallidas"] += 1
            resultados["detalles"].append({
                "entrega_id": item.entrega_id,
                "status": "error",
                "error": str(e)
            })
    
    return resultados


@router.get(
    "/actividad/{actividad_id}",
    response_model=List[CalificacionPublic],
    summary="Obtener calificaciones de una actividad",
    description="Obtiene todas las calificaciones de una actividad evaluativa"
)
def obtener_calificaciones_actividad(
    actividad_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las calificaciones de una actividad.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad evaluativa
    
    **Retorna:**
    - Lista de calificaciones de la actividad
    
    **Uso:** Ver todas las notas de una tarea, examen, etc.
    """
    try:
        calificaciones = calificacion_service.obtener_calificaciones_de_actividad(
            db=db,
            actividad_id=actividad_id
        )
        return calificaciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener calificaciones: {str(e)}"
        )


@router.get(
    "/inscripcion/{inscripcion_id}",
    response_model=List[CalificacionPublic],
    summary="Obtener calificaciones de un estudiante",
    description="Obtiene todas las calificaciones de un estudiante en un grupo"
)
def obtener_calificaciones_estudiante(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las calificaciones de un estudiante.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción del estudiante
    
    **Retorna:**
    - Lista de calificaciones del estudiante en el grupo
    
    **Uso:** Ver historial de notas del estudiante
    """
    try:
        calificaciones = calificacion_service.obtener_calificaciones_de_estudiante(
            db=db,
            inscripcion_id=inscripcion_id
        )
        return calificaciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener calificaciones: {str(e)}"
        )


@router.get(
    "/entrega/{entrega_id}",
    response_model=Optional[CalificacionPublic],
    summary="Obtener calificación de una entrega",
    description="Obtiene la calificación de una entrega específica"
)
def obtener_calificacion_entrega(
    entrega_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene la calificación de una entrega.
    
    **Parámetros:**
    - **entrega_id**: ID de la entrega
    
    **Retorna:**
    - Calificación de la entrega o null si no está calificada
    """
    calificacion = calificacion_service.obtener_calificacion_por_entrega(
        db=db,
        entrega_id=entrega_id
    )
    return calificacion


@router.get(
    "/estadisticas/actividad/{actividad_id}",
    response_model=dict,
    summary="Obtener estadísticas de una actividad",
    description="Obtiene estadísticas de calificaciones de una actividad evaluativa"
)
def obtener_estadisticas_actividad(
    actividad_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de calificaciones de una actividad.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad evaluativa
    
    **Retorna:**
    - Diccionario con estadísticas:
        - total_calificaciones: Total de entregas calificadas
        - nota_promedio: Promedio de las notas
        - nota_maxima: Nota más alta
        - nota_minima: Nota más baja
        - estudiantes_aprobados: Número con nota >= 3.0
        - estudiantes_reprobados: Número con nota < 3.0
    """
    try:
        estadisticas = calificacion_service.obtener_estadisticas_calificaciones(
            db=db,
            actividad_id=actividad_id
        )
        return estadisticas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get(
    "/promedio/inscripcion/{inscripcion_id}",
    response_model=dict,
    summary="Obtener promedio de un estudiante",
    description="Calcula el promedio simple de calificaciones de un estudiante"
)
def obtener_promedio_estudiante(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el promedio simple de un estudiante.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción del estudiante
    
    **Retorna:**
    - Diccionario con el promedio simple
    """
    try:
        promedio = calificacion_service.obtener_promedio_estudiante_en_grupo(
            db=db,
            inscripcion_id=inscripcion_id
        )
        return {
            "inscripcion_id": inscripcion_id,
            "promedio": promedio
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular promedio: {str(e)}"
        )


@router.get(
    "/definitiva/inscripcion/{inscripcion_id}",
    response_model=dict,
    summary="Calcular nota definitiva",
    description="Calcula la nota definitiva ponderada de un estudiante en un grupo"
)
def calcular_nota_definitiva(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    """
    Calcula la nota definitiva ponderada de un estudiante.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción del estudiante
    
    **Retorna:**
    - Diccionario con:
        - inscripcion_id
        - nota_definitiva: Promedio ponderado considerando porcentajes de actividades
        - porcentaje_calculado: Porcentaje del total de actividades que está calificado
    
    **Nota:** La nota definitiva considera el peso (porcentaje) de cada actividad
    """
    try:
        nota_definitiva = calificacion_service.calcular_nota_definitiva(
            db=db,
            inscripcion_id=inscripcion_id
        )
        return {
            "inscripcion_id": inscripcion_id,
            "nota_definitiva": nota_definitiva
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular nota definitiva: {str(e)}"
        )


@router.get(
    "/{calificacion_id}",
    response_model=CalificacionPublic,
    summary="Obtener calificación por ID",
    description="Obtiene una calificación específica por su ID"
)
def obtener_calificacion(
    calificacion_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una calificación por su ID.
    
    **Parámetros:**
    - **calificacion_id**: ID de la calificación
    
    **Retorna:**
    - Calificación con todos sus detalles
    
    **Excepciones:**
    - **404**: Calificación no encontrada
    """
    calificacion = calificacion_service.obtener_calificacion_por_id(
        db=db,
        calificacion_id=calificacion_id
    )
    if not calificacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calificación con ID {calificacion_id} no encontrada"
        )
    return calificacion


@router.put(
    "/{calificacion_id}",
    response_model=CalificacionPublic,
    summary="Actualizar calificación",
    description="Actualiza una calificación existente (cambiar nota o retroalimentación)"
)
def actualizar_calificacion(
    calificacion_id: int,
    calificacion_data: CalificacionUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una calificación existente.
    
    **Parámetros:**
    - **calificacion_id**: ID de la calificación a actualizar
    - **calificacion_data**: Datos a actualizar:
        - nota_obtenida: Nueva nota (opcional)
        - retroalimentacion: Nueva retroalimentación (opcional)
    
    **Retorna:**
    - Calificación actualizada
    
    **Excepciones:**
    - **404**: Calificación no encontrada
    - **400**: Datos inválidos
    """
    try:
        calificacion = calificacion_service.actualizar_calificacion(
            db=db,
            calificacion_id=calificacion_id,
            datos_actualizacion=calificacion_data.model_dump(exclude_unset=True)
        )
        if not calificacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Calificación con ID {calificacion_id} no encontrada"
            )
        return calificacion
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar calificación: {str(e)}"
        )


@router.delete(
    "/{calificacion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar calificación",
    description="Elimina una calificación (cambia estado de entrega a ENTREGADA)"
)
def eliminar_calificacion(
    calificacion_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina una calificación.
    
    **Parámetros:**
    - **calificacion_id**: ID de la calificación a eliminar
    
    **Retorna:**
    - 204 No Content si se elimina exitosamente
    
    **Excepciones:**
    - **404**: Calificación no encontrada
    
    **Nota:** Al eliminar la calificación, la entrega vuelve al estado ENTREGADA
    """
    try:
        success = calificacion_service.eliminar_calificacion(
            db=db,
            calificacion_id=calificacion_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Calificación con ID {calificacion_id} no encontrada"
            )
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar calificación: {str(e)}"
        )
