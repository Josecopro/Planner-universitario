"""
Endpoints de API para Asistencias
Rutas: /api/v1/asistencias
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.asistencia import (
    AsistenciaCreate,
    AsistenciaCreateBulk,
    AsistenciaUpdate,
    AsistenciaPublic,
    AsistenciaResumenEstudiante,
    AsistenciaResumenGrupo
)
from services import asistencia_service
from models.asistencia import EstadoAsistencia


router = APIRouter()


@router.post(
    "/",
    response_model=AsistenciaPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar asistencia individual",
    description="Registra la asistencia de un estudiante en una fecha específica"
)
def registrar_asistencia(
    asistencia_data: AsistenciaCreate,
    db: Session = Depends(get_db)
):
    """
    Registra la asistencia de un estudiante individual.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción (estudiante en el grupo)
    - **grupo_id**: ID del grupo
    - **fecha**: Fecha de la sesión
    - **estado**: Estado de asistencia (Presente, Ausente, Tardanza, Justificado)
    
    **Retorna:**
    - Registro de asistencia creado o actualizado
    
    **Excepciones:**
    - **404**: Inscripción no encontrada
    - **400**: Datos inválidos
    """
    try:
        asistencia = asistencia_service.registrar_asistencia_individual(
            db=db,
            inscripcion_id=asistencia_data.inscripcion_id,
            fecha=asistencia_data.fecha,
            estado=asistencia_data.estado,
            grupo_id=asistencia_data.grupo_id
        )
        return asistencia
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar asistencia: {str(e)}"
        )


@router.post(
    "/bulk",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar asistencia masiva",
    description="Registra la asistencia de múltiples estudiantes de un grupo en una fecha"
)
def registrar_asistencia_bulk(
    asistencia_data: AsistenciaCreateBulk,
    db: Session = Depends(get_db)
):
    """
    Registra la asistencia de múltiples estudiantes a la vez.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    - **fecha**: Fecha de la sesión
    - **asistencias**: Lista de objetos con:
        - inscripcion_id: ID de la inscripción
        - estado: Estado de asistencia
    
    **Retorna:**
    - Mensaje de éxito
    
    **Excepciones:**
    - **404**: Grupo no encontrado
    - **400**: Datos inválidos
    """
    try:
        success = asistencia_service.registrar_asistencia_grupo(
            db=db,
            grupo_id=asistencia_data.grupo_id,
            fecha=asistencia_data.fecha,
            asistencias=asistencia_data.asistencias
        )
        
        if success:
            return {
                "message": "Asistencias registradas exitosamente",
                "grupo_id": asistencia_data.grupo_id,
                "fecha": asistencia_data.fecha,
                "total_registros": len(asistencia_data.asistencias)
            }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar asistencias: {str(e)}"
        )


@router.get(
    "/grupo/{grupo_id}",
    response_model=List[AsistenciaPublic],
    summary="Obtener asistencias de un grupo",
    description="Obtiene todos los registros de asistencia de un grupo con filtros opcionales"
)
def obtener_asistencias_grupo(
    grupo_id: int,
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio del rango"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin del rango"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los registros de asistencia de un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Parámetros de Query:**
    - **fecha_inicio**: Filtrar desde esta fecha
    - **fecha_fin**: Filtrar hasta esta fecha
    
    **Retorna:**
    - Lista de registros de asistencia
    """
    try:
        asistencias = asistencia_service.obtener_asistencias_por_grupo(
            db=db,
            grupo_id=grupo_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        return asistencias
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener asistencias: {str(e)}"
        )


@router.get(
    "/grupo/{grupo_id}/fecha/{fecha}",
    response_model=List[AsistenciaPublic],
    summary="Obtener asistencias por fecha",
    description="Obtiene los registros de asistencia de un grupo en una fecha específica"
)
def obtener_asistencias_por_fecha(
    grupo_id: int,
    fecha: date,
    db: Session = Depends(get_db)
):
    """
    Obtiene los registros de asistencia de un grupo en una fecha.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    - **fecha**: Fecha de la sesión (formato: YYYY-MM-DD)
    
    **Retorna:**
    - Lista de registros de asistencia de esa fecha
    """
    try:
        asistencias = asistencia_service.obtener_asistencia_por_fecha(
            db=db,
            grupo_id=grupo_id,
            fecha=fecha
        )
        return asistencias
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener asistencias: {str(e)}"
        )


@router.get(
    "/inscripcion/{inscripcion_id}",
    response_model=List[AsistenciaPublic],
    summary="Obtener asistencias de un estudiante",
    description="Obtiene todos los registros de asistencia de un estudiante (inscripción)"
)
def obtener_asistencias_estudiante(
    inscripcion_id: int,
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio del rango"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin del rango"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los registros de asistencia de un estudiante.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción del estudiante
    
    **Parámetros de Query:**
    - **fecha_inicio**: Filtrar desde esta fecha
    - **fecha_fin**: Filtrar hasta esta fecha
    
    **Retorna:**
    - Lista de registros de asistencia del estudiante
    """
    try:
        asistencias = asistencia_service.obtener_asistencias_por_inscripcion(
            db=db,
            inscripcion_id=inscripcion_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        return asistencias
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener asistencias: {str(e)}"
        )


@router.get(
    "/resumen/inscripcion/{inscripcion_id}",
    response_model=dict,
    summary="Obtener resumen de asistencia de un estudiante",
    description="Obtiene estadísticas de asistencia de un estudiante en un grupo"
)
def obtener_resumen_estudiante(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene el resumen de asistencia de un estudiante.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción del estudiante
    
    **Retorna:**
    - Diccionario con estadísticas:
        - inscripcion_id
        - total_registros
        - porcentaje_asistencia
        - conteo_estados: Diccionario con conteo por estado
        - asistencias: Lista completa de asistencias
    """
    try:
        resumen = asistencia_service.obtener_reporte_asistencia_estudiante(
            db=db,
            inscripcion_id=inscripcion_id
        )
        return resumen
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen: {str(e)}"
        )


@router.get(
    "/resumen/grupo/{grupo_id}",
    response_model=dict,
    summary="Obtener estadísticas de asistencia de un grupo",
    description="Obtiene estadísticas generales de asistencia de un grupo"
)
def obtener_estadisticas_grupo(
    grupo_id: int,
    fecha: Optional[date] = Query(None, description="Fecha específica (opcional)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de asistencia de un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Parámetros de Query:**
    - **fecha**: Fecha específica (si no se proporciona, calcula sobre todas las fechas)
    
    **Retorna:**
    - Diccionario con estadísticas del grupo:
        - total_estudiantes: Total de estudiantes inscritos
        - total_registros: Total de registros de asistencia
        - presentes, ausentes, justificados, tardanzas
        - porcentaje_asistencia: Porcentaje promedio
    """
    try:
        estadisticas = asistencia_service.obtener_estadisticas_asistencia_grupo(
            db=db,
            grupo_id=grupo_id,
            fecha=fecha
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
    "/ausentes/grupo/{grupo_id}/fecha/{fecha}",
    response_model=List[AsistenciaPublic],
    summary="Obtener estudiantes ausentes",
    description="Obtiene lista de estudiantes ausentes en una fecha específica"
)
def obtener_estudiantes_ausentes(
    grupo_id: int,
    fecha: date,
    db: Session = Depends(get_db)
):
    """
    Obtiene estudiantes ausentes en una fecha específica.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    - **fecha**: Fecha de la sesión (formato: YYYY-MM-DD)
    
    **Retorna:**
    - Lista de registros de asistencia con estado AUSENTE
    """
    try:
        estudiantes = asistencia_service.obtener_estudiantes_ausentes(
            db=db,
            grupo_id=grupo_id,
            fecha=fecha
        )
        return estudiantes
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estudiantes ausentes: {str(e)}"
        )


@router.get(
    "/fechas/grupo/{grupo_id}",
    response_model=List[date],
    summary="Obtener fechas con asistencia registrada",
    description="Obtiene lista de fechas en las que se ha registrado asistencia para un grupo"
)
def obtener_fechas_asistencia(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene las fechas en las que se ha registrado asistencia.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Retorna:**
    - Lista de fechas con asistencia registrada
    """
    try:
        fechas = asistencia_service.obtener_fechas_asistencia_grupo(
            db=db,
            grupo_id=grupo_id
        )
        return fechas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener fechas: {str(e)}"
        )


@router.get(
    "/{asistencia_id}",
    response_model=AsistenciaPublic,
    summary="Obtener asistencia por ID",
    description="Obtiene un registro de asistencia específico por su ID"
)
def obtener_asistencia(
    asistencia_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un registro de asistencia por su ID.
    
    **Parámetros:**
    - **asistencia_id**: ID del registro de asistencia
    
    **Retorna:**
    - Registro de asistencia
    
    **Excepciones:**
    - **404**: Asistencia no encontrada
    """
    asistencia = asistencia_service.obtener_asistencia_por_id(
        db=db,
        asistencia_id=asistencia_id
    )
    if not asistencia:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asistencia con ID {asistencia_id} no encontrada"
        )
    return asistencia


@router.patch(
    "/{asistencia_id}",
    response_model=AsistenciaPublic,
    summary="Actualizar estado de asistencia",
    description="Actualiza el estado de un registro de asistencia existente"
)
def actualizar_estado_asistencia(
    asistencia_id: int,
    asistencia_data: AsistenciaUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado de un registro de asistencia.
    
    **Parámetros:**
    - **asistencia_id**: ID del registro de asistencia
    - **asistencia_data**: Nuevo estado
    
    **Retorna:**
    - Registro de asistencia actualizado
    
    **Excepciones:**
    - **404**: Asistencia no encontrada
    - **400**: Estado inválido
    """
    if asistencia_data.estado is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'estado' es requerido"
        )
    
    try:
        asistencia = asistencia_service.actualizar_asistencia(
            db=db,
            asistencia_id=asistencia_id,
            nuevo_estado=asistencia_data.estado
        )
        if not asistencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asistencia con ID {asistencia_id} no encontrada"
            )
        return asistencia
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar asistencia: {str(e)}"
        )


@router.delete(
    "/{asistencia_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar registro de asistencia",
    description="Elimina un registro de asistencia"
)
def eliminar_asistencia(
    asistencia_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina un registro de asistencia.
    
    **Parámetros:**
    - **asistencia_id**: ID del registro a eliminar
    
    **Retorna:**
    - 204 No Content si se elimina exitosamente
    
    **Excepciones:**
    - **404**: Asistencia no encontrada
    """
    try:
        success = asistencia_service.eliminar_asistencia(
            db=db,
            asistencia_id=asistencia_id
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asistencia con ID {asistencia_id} no encontrada"
            )
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar asistencia: {str(e)}"
        )
