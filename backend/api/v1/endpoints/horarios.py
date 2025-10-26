"""
Endpoints para Horarios

Gestiona los horarios de los grupos (bloques de clase), validación de conflictos
y consultas de disponibilidad de salones.
"""

from typing import List, Optional
from datetime import time
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_superadmin, require_roles
from models.usuario import Usuario
from schemas.horario import (
    HorarioCreate,
    HorarioUpdate,
    HorarioPublic
)
from services import horario_service


router = APIRouter()


@router.post(
    "/",
    response_model=HorarioPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear horario"
)
def crear_horario(
    horario: HorarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Superadmin", "Profesor"]))
):
    """
    Crea un nuevo horario para un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo al que pertenece
    - **dia**: Día de la semana (Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Domingo)
    - **hora_inicio**: Hora de inicio (formato HH:MM:SS)
    - **hora_fin**: Hora de finalización (formato HH:MM:SS)
    - **salon**: Salón o ubicación (opcional)
    
    **Validaciones:**
    - El grupo debe existir
    - Día de semana válido
    - Hora de fin debe ser posterior a hora de inicio
    - Duración entre 30 minutos y 4 horas
    - Horario entre 6:00 AM y 10:00 PM
    - Sin conflictos de salón (si se especifica)
    - Sin conflictos con otros horarios del profesor
    
    **Retorna:** Horario creado
    
    **Errores:**
    - 400: Datos inválidos o hay conflictos
    - 404: Grupo no encontrado
    """
    try:
        nuevo_horario = horario_service.crear_horario(
            db=db,
            datos_horario=horario.model_dump()
        )
        return nuevo_horario
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear horario: {str(e)}"
        )


@router.get(
    "/grupo/{grupo_id}",
    response_model=List[HorarioPublic],
    summary="Obtener horarios por grupo"
)
def obtener_horarios_por_grupo(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los horarios de un grupo específico.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Retorna:** Lista de horarios del grupo ordenados por día y hora
    
    **Útil para:** Ver el horario completo de una sección/grupo
    """
    try:
        horarios = horario_service.obtener_horarios_por_grupo(db, grupo_id)
        return horarios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener horarios: {str(e)}"
        )


@router.get(
    "/dia/{dia}",
    response_model=List[HorarioPublic],
    summary="Obtener horarios por día"
)
def obtener_horarios_por_dia(
    dia: str,
    semestre: Optional[str] = Query(None, description="Filtrar por semestre"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los horarios de un día específico.
    
    **Parámetros:**
    - **dia**: Día de la semana (Lunes, Martes, Miércoles, etc.)
    - **semestre**: Filtrar por semestre (opcional)
    
    **Retorna:** Lista de horarios del día ordenados por hora de inicio
    
    **Útil para:** Ver qué clases hay en un día específico
    """
    try:
        horarios = horario_service.obtener_horarios_por_dia(db, dia, semestre)
        return horarios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener horarios del día: {str(e)}"
        )


@router.get(
    "/salon/{salon}",
    response_model=List[HorarioPublic],
    summary="Obtener horarios por salón"
)
def obtener_horarios_por_salon(
    salon: str,
    dia: Optional[str] = Query(None, description="Filtrar por día"),
    semestre: Optional[str] = Query(None, description="Filtrar por semestre"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los horarios que usan un salón específico.
    
    **Parámetros:**
    - **salon**: Nombre del salón (ej: "Bloque 5 - 101")
    - **dia**: Filtrar por día de la semana (opcional)
    - **semestre**: Filtrar por semestre (opcional)
    
    **Retorna:** Lista de horarios que usan el salón
    
    **Útil para:** Ver la ocupación de un salón, planificación de espacios
    """
    try:
        horarios = horario_service.obtener_horarios_por_salon(
            db=db,
            salon=salon,
            dia=dia,
            semestre=semestre
        )
        return horarios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener horarios del salón: {str(e)}"
        )


@router.get(
    "/salon/{salon}/disponibilidad",
    summary="Obtener disponibilidad de salón"
)
def obtener_disponibilidad_salon(
    salon: str,
    dia: str = Query(..., description="Día de la semana"),
    semestre: str = Query(..., description="Semestre"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los bloques ocupados de un salón en un día específico.
    
    **Parámetros:**
    - **salon**: Nombre del salón
    - **dia**: Día de la semana (requerido)
    - **semestre**: Semestre (requerido)
    
    **Retorna:** Lista de bloques ocupados con información del curso y profesor
    
    **Información incluida:**
    - Hora de inicio y fin
    - Curso que ocupa el salón
    - Profesor asignado
    - ID del grupo
    
    **Útil para:** Encontrar horas libres en un salón específico
    """
    try:
        disponibilidad = horario_service.obtener_horarios_disponibles_salon(
            db=db,
            salon=salon,
            dia=dia,
            semestre=semestre
        )
        return disponibilidad
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener disponibilidad: {str(e)}"
        )


@router.get(
    "/{horario_id}",
    response_model=HorarioPublic,
    summary="Obtener horario por ID"
)
def obtener_horario(
    horario_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un horario por su ID.
    
    **Parámetros:**
    - **horario_id**: ID del horario
    
    **Retorna:** Datos del horario
    
    **Errores:**
    - 404: Horario no encontrado
    """
    horario = horario_service.obtener_horario_por_id(db, horario_id)
    if not horario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Horario con ID {horario_id} no encontrado"
        )
    return horario


@router.get(
    "/verificar-conflicto/salon",
    summary="Verificar conflicto de salón"
)
def verificar_conflicto_salon(
    salon: str = Query(..., description="Nombre del salón"),
    dia: str = Query(..., description="Día de la semana"),
    hora_inicio: str = Query(..., description="Hora de inicio (HH:MM:SS)"),
    hora_fin: str = Query(..., description="Hora de fin (HH:MM:SS)"),
    semestre: str = Query(..., description="Semestre"),
    excluir_horario_id: Optional[int] = Query(None, description="ID de horario a excluir"),
    db: Session = Depends(get_db)
):
    """
    Verifica si hay conflictos de uso de salón en un horario específico.
    
    **Parámetros:**
    - **salon**: Nombre del salón
    - **dia**: Día de la semana
    - **hora_inicio**: Hora de inicio en formato HH:MM:SS
    - **hora_fin**: Hora de fin en formato HH:MM:SS
    - **semestre**: Semestre a verificar
    - **excluir_horario_id**: ID de horario a excluir (útil al actualizar)
    
    **Retorna:**
    - **hay_conflicto**: Boolean indicando si hay conflicto
    - **conflictos**: Lista de horarios que entran en conflicto
    
    **Útil para:** Validar antes de crear/actualizar un horario
    """
    try:
        # Convertir strings a time
        from datetime import datetime as dt
        hora_inicio_obj = dt.strptime(hora_inicio, "%H:%M:%S").time()
        hora_fin_obj = dt.strptime(hora_fin, "%H:%M:%S").time()
        
        hay_conflicto, conflictos = horario_service.verificar_conflicto_salon(
            db=db,
            salon=salon,
            dia=dia,
            hora_inicio=hora_inicio_obj,
            hora_fin=hora_fin_obj,
            semestre=semestre,
            excluir_horario_id=excluir_horario_id
        )
        
        return {
            "hay_conflicto": hay_conflicto,
            "conflictos": conflictos
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en el formato de hora: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar conflicto: {str(e)}"
        )


@router.get(
    "/verificar-conflicto/profesor",
    summary="Verificar conflicto de profesor"
)
def verificar_conflicto_profesor(
    profesor_id: int = Query(..., description="ID del profesor"),
    dia: str = Query(..., description="Día de la semana"),
    hora_inicio: str = Query(..., description="Hora de inicio (HH:MM:SS)"),
    hora_fin: str = Query(..., description="Hora de fin (HH:MM:SS)"),
    semestre: str = Query(..., description="Semestre"),
    excluir_grupo_id: Optional[int] = Query(None, description="ID de grupo a excluir"),
    db: Session = Depends(get_db)
):
    """
    Verifica si un profesor tiene conflictos de horario.
    
    **Parámetros:**
    - **profesor_id**: ID del profesor
    - **dia**: Día de la semana
    - **hora_inicio**: Hora de inicio en formato HH:MM:SS
    - **hora_fin**: Hora de fin en formato HH:MM:SS
    - **semestre**: Semestre a verificar
    - **excluir_grupo_id**: ID de grupo a excluir (útil al actualizar)
    
    **Retorna:**
    - **hay_conflicto**: Boolean indicando si hay conflicto
    - **conflictos**: Lista de horarios que entran en conflicto
    
    **Útil para:** Validar que el profesor no tenga dos clases al mismo tiempo
    """
    try:
        # Convertir strings a time
        from datetime import datetime as dt
        hora_inicio_obj = dt.strptime(hora_inicio, "%H:%M:%S").time()
        hora_fin_obj = dt.strptime(hora_fin, "%H:%M:%S").time()
        
        hay_conflicto, conflictos = horario_service.verificar_conflicto_profesor(
            db=db,
            profesor_id=profesor_id,
            dia=dia,
            hora_inicio=hora_inicio_obj,
            hora_fin=hora_fin_obj,
            semestre=semestre,
            excluir_grupo_id=excluir_grupo_id
        )
        
        return {
            "hay_conflicto": hay_conflicto,
            "conflictos": conflictos
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en el formato de hora: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar conflicto: {str(e)}"
        )


@router.put(
    "/{horario_id}",
    response_model=HorarioPublic,
    summary="Actualizar horario"
)
def actualizar_horario(
    horario_id: int,
    datos_actualizados: HorarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["Superadmin", "Profesor"]))
):
    """
    Actualiza un horario existente.
    
    **Campos actualizables:**
    - **dia**: Cambiar día de la semana
    - **hora_inicio**: Cambiar hora de inicio
    - **hora_fin**: Cambiar hora de finalización
    - **salon**: Cambiar salón
    
    **Parámetros:**
    - **horario_id**: ID del horario
    - **datos_actualizados**: Campos a actualizar
    
    **Validaciones:**
    - Mismas validaciones que al crear
    - Verifica conflictos con el nuevo horario
    
    **Retorna:** Horario actualizado
    
    **Errores:**
    - 400: Datos inválidos o hay conflictos
    - 404: Horario no encontrado
    """
    try:
        horario_actualizado = horario_service.actualizar_horario(
            db=db,
            horario_id=horario_id,
            datos_actualizacion=datos_actualizados.model_dump(exclude_unset=True)
        )
        
        if not horario_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Horario con ID {horario_id} no encontrado"
            )
        
        return horario_actualizado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar horario: {str(e)}"
        )


@router.delete(
    "/{horario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar horario"
)
def eliminar_horario(
    horario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    """
    Elimina un horario.
    
    **Parámetros:**
    - **horario_id**: ID del horario
    
    **Retorna:** 204 No Content si se eliminó correctamente
    
    **Errores:**
    - 404: Horario no encontrado
    """
    eliminado = horario_service.eliminar_horario(db, horario_id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Horario con ID {horario_id} no encontrado"
        )
    return None


@router.delete(
    "/grupo/{grupo_id}/todos",
    summary="Eliminar todos los horarios de un grupo"
)
def eliminar_horarios_grupo(
    grupo_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_superadmin)
):
    """
    Elimina todos los horarios de un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Retorna:** Número de horarios eliminados
    
    **Útil para:** Limpiar horarios antes de recrearlos,
    eliminar horarios de grupos cancelados
    """
    try:
        total_eliminados = horario_service.eliminar_horarios_por_grupo(db, grupo_id)
        return {
            "grupo_id": grupo_id,
            "horarios_eliminados": total_eliminados
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar horarios: {str(e)}"
        )
