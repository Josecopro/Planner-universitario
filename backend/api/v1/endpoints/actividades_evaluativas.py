"""
Endpoints de API para Actividades Evaluativas
Rutas: /api/v1/actividades-evaluativas
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_superadmin, require_roles
from models.usuario import Usuario
from schemas.actividad_evaluativa import (
    ActividadEvaluativaCreate,
    ActividadEvaluativaUpdate,
    ActividadEvaluativaPublic,
    ActividadEvaluativaList,
    ActividadEvaluativaEstadoUpdate
)
from services import actividad_evaluativa_service
from models.actividad_evaluativa import TipoActividad, PrioridadActividad


router = APIRouter()


@router.post(
    "/",
    response_model=ActividadEvaluativaPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva actividad evaluativa",
    description="Crea una nueva actividad evaluativa (tarea, examen, quiz, etc.) para un grupo"
)
def crear_actividad(
    actividad_data: ActividadEvaluativaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Superadmin", "Profesor"]))
):
    """
    Crea una nueva actividad evaluativa para un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo al que pertenece la actividad
    - **titulo**: Título de la actividad
    - **descripcion**: Descripción detallada (opcional)
    - **tipo**: Tipo de actividad (Tarea, Quiz, Examen Parcial, etc.)
    - **prioridad**: Prioridad (Baja, Media, Alta, Crítica)
    - **porcentaje**: Porcentaje en la nota final (0-100)
    - **fecha_entrega**: Fecha y hora límite para entregar
    
    **Retorna:**
    - Actividad evaluativa creada con su ID
    
    **Excepciones:**
    - **404**: Grupo no encontrado
    - **400**: Datos inválidos o porcentaje excede el límite del grupo
    """
    try:
        actividad = actividad_evaluativa_service.crear_actividad(
            db=db,
            grupo_id=actividad_data.grupo_id,
            datos_actividad=actividad_data.model_dump()
        )
        return actividad
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear actividad evaluativa: {str(e)}"
        )


@router.get(
    "/grupo/{grupo_id}",
    response_model=List[ActividadEvaluativaList],
    summary="Listar actividades evaluativas de un grupo",
    description="Obtiene todas las actividades evaluativas de un grupo específico con filtros opcionales"
)
def listar_actividades_grupo(
    grupo_id: int,
    tipo: Optional[TipoActividad] = Query(None, description="Filtrar por tipo de actividad"),
    prioridad: Optional[PrioridadActividad] = Query(None, description="Filtrar por prioridad"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Lista actividades evaluativas de un grupo con filtros opcionales.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo (requerido)
    
    **Parámetros de Query:**
    - **tipo**: Filtrar por tipo (Tarea, Quiz, Examen Parcial, etc.)
    - **prioridad**: Filtrar por prioridad (Baja, Media, Alta, Crítica)
    - **estado**: Filtrar por estado (Programada, Abierta, Cerrada)
    
    **Retorna:**
    - Lista de actividades evaluativas del grupo
    """
    try:
        if tipo:
            actividades = actividad_evaluativa_service.obtener_actividades_por_tipo(
                db=db,
                grupo_id=grupo_id,
                tipo=tipo
            )
        elif prioridad:
            actividades = actividad_evaluativa_service.obtener_actividades_por_prioridad(
                db=db,
                grupo_id=grupo_id,
                prioridad=prioridad
            )
        else:
            from models.actividad_evaluativa import EstadoActividad
            estado_enum = None
            if estado:
                try:
                    estado_enum = EstadoActividad(estado)
                except ValueError:
                    pass
            
            actividades = actividad_evaluativa_service.obtener_actividades_filtradas(
                db=db,
                grupo_id=grupo_id,
                estado=estado_enum,
                prioridad=prioridad
            )
        return actividades
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener actividades: {str(e)}"
        )


@router.get(
    "/pendientes/grupo/{grupo_id}",
    response_model=List[ActividadEvaluativaList],
    summary="Obtener actividades pendientes de un grupo",
    description="Obtiene todas las actividades evaluativas pendientes (abiertas) de un grupo específico"
)
def obtener_actividades_pendientes(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene las actividades evaluativas pendientes (con estado 'Abierta') de un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Retorna:**
    - Lista de actividades abiertas del grupo
    
    **Excepciones:**
    - **404**: Grupo no encontrado
    """
    try:
        actividades = actividad_evaluativa_service.obtener_actividades_pendientes_grupo(
            db=db,
            grupo_id=grupo_id
        )
        return actividades
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener actividades pendientes: {str(e)}"
        )


@router.get(
    "/proximas/grupo/{grupo_id}",
    response_model=List[ActividadEvaluativaList],
    summary="Obtener actividades próximas a vencer",
    description="Obtiene actividades evaluativas de un grupo que están próximas a su fecha de entrega"
)
def obtener_actividades_proximas(
    grupo_id: int,
    dias: int = Query(7, ge=1, le=30, description="Número de días hacia adelante"),
    db: Session = Depends(get_db)
):
    """
    Obtiene actividades evaluativas que vencen en los próximos N días.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Parámetros de Query:**
    - **dias**: Número de días hacia adelante (1-30)
    
    **Retorna:**
    - Lista de actividades próximas a vencer
    """
    try:
        actividades = actividad_evaluativa_service.obtener_actividades_proximas(
            db=db,
            grupo_id=grupo_id,
            dias=dias
        )
        return actividades
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener actividades próximas: {str(e)}"
        )


@router.get(
    "/{actividad_id}",
    response_model=ActividadEvaluativaPublic,
    summary="Obtener actividad evaluativa por ID",
    description="Obtiene los detalles completos de una actividad evaluativa específica"
)
def obtener_actividad(
    actividad_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una actividad evaluativa por su ID.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad evaluativa
    
    **Retorna:**
    - Actividad evaluativa con todos sus detalles
    
    **Excepciones:**
    - **404**: Actividad no encontrada
    """
    actividad = actividad_evaluativa_service.obtener_actividad_por_id(
        db=db,
        actividad_id=actividad_id
    )
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actividad evaluativa con ID {actividad_id} no encontrada"
        )
    return actividad


@router.get(
    "/{actividad_id}/estadisticas",
    response_model=dict,
    summary="Obtener estadísticas de una actividad",
    description="Obtiene estadísticas sobre entregas y calificaciones de una actividad evaluativa"
)
def obtener_estadisticas(
    actividad_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de una actividad evaluativa.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad evaluativa
    
    **Retorna:**
    - Diccionario con estadísticas:
        - total_inscripciones: Total de estudiantes inscritos en el grupo
        - total_entregas: Total de entregas realizadas
        - entregas_a_tiempo: Entregas antes de la fecha límite
        - entregas_tarde: Entregas después de la fecha límite
        - sin_entregar: Estudiantes que no han entregado
        - promedio_nota: Promedio de calificaciones
        - nota_maxima: Nota más alta
        - nota_minima: Nota más baja
        - porcentaje_entregas: Porcentaje de estudiantes que entregaron
    
    **Excepciones:**
    - **404**: Actividad no encontrada
    """
    actividad = actividad_evaluativa_service.obtener_actividad_por_id(
        db=db,
        actividad_id=actividad_id
    )
    if not actividad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actividad evaluativa con ID {actividad_id} no encontrada"
        )
    
    try:
        estadisticas = actividad_evaluativa_service.obtener_estadisticas_actividad(
            db=db,
            actividad_id=actividad_id
        )
        return estadisticas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.put(
    "/{actividad_id}",
    response_model=ActividadEvaluativaPublic,
    summary="Actualizar actividad evaluativa",
    description="Actualiza completamente una actividad evaluativa existente"
)
def actualizar_actividad(
    actividad_id: int,
    actividad_data: ActividadEvaluativaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Superadmin", "Profesor"]))
):
    """
    Actualiza una actividad evaluativa existente.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad a actualizar
    - **actividad_data**: Datos a actualizar (todos opcionales)
    
    **Retorna:**
    - Actividad evaluativa actualizada
    
    **Excepciones:**
    - **404**: Actividad no encontrada
    - **400**: Datos inválidos
    """
    try:
        actividad = actividad_evaluativa_service.actualizar_actividad(
            db=db,
            actividad_id=actividad_id,
            datos_actualizacion=actividad_data.model_dump(exclude_unset=True)
        )
        if not actividad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Actividad evaluativa con ID {actividad_id} no encontrada"
            )
        return actividad
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar actividad: {str(e)}"
        )


@router.patch(
    "/{actividad_id}/estado",
    response_model=ActividadEvaluativaPublic,
    summary="Cambiar estado de actividad",
    description="Cambia únicamente el estado de una actividad evaluativa (Programada, Abierta, Cerrada)"
)
def cambiar_estado(
    actividad_id: int,
    estado_data: ActividadEvaluativaEstadoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Superadmin", "Profesor"]))
):
    """
    Cambia el estado de una actividad evaluativa.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad
    - **estado_data**: Nuevo estado (Programada, Abierta, Cerrada)
    
    **Retorna:**
    - Actividad evaluativa con estado actualizado
    
    **Excepciones:**
    - **404**: Actividad no encontrada
    - **400**: Estado inválido
    """
    try:
        actividad = actividad_evaluativa_service.cambiar_estado_actividad(
            db=db,
            actividad_id=actividad_id,
            nuevo_estado=estado_data.estado
        )
        if not actividad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Actividad evaluativa con ID {actividad_id} no encontrada"
            )
        return actividad
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar estado: {str(e)}"
        )


@router.delete(
    "/{actividad_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar actividad evaluativa",
    description="Elimina una actividad evaluativa (solo si no tiene entregas)"
)
def eliminar_actividad(
    actividad_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    """
    Elimina una actividad evaluativa.
    
    **Parámetros:**
    - **actividad_id**: ID de la actividad a eliminar
    
    **Retorna:**
    - 204 No Content si se elimina exitosamente
    
    **Excepciones:**
    - **404**: Actividad no encontrada
    - **400**: No se puede eliminar (tiene entregas asociadas)
    """
    try:
        success = actividad_evaluativa_service.eliminar_actividad(
            db=db,
            actividad_id=actividad_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Actividad evaluativa con ID {actividad_id} no encontrada"
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
            detail=f"Error al eliminar actividad: {str(e)}"
        )
