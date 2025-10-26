"""
Endpoints para Inscripciones

Gestiona las inscripciones de estudiantes en grupos (matrícula de cursos),
cambios de estado y consultas de inscripciones.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.inscripcion import (
    InscripcionCreate,
    InscripcionUpdate,
    InscripcionPublic,
    InscripcionEstadoUpdate
)
from services import inscripcion_service
from models.inscripcion import EstadoInscripcion


router = APIRouter()


@router.post(
    "/",
    response_model=InscripcionPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Inscribir estudiante"
)
def inscribir_estudiante(
    inscripcion: InscripcionCreate,
    db: Session = Depends(get_db)
):
    """
    Inscribe un estudiante en un grupo.
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    - **grupo_id**: ID del grupo
    
    **Validaciones:**
    - El estudiante debe existir
    - El grupo debe existir y aceptar inscripciones
    - El grupo debe tener cupos disponibles
    - El estudiante no debe estar ya inscrito en el grupo
    - El grupo debe estar en estado Programado o Abierto
    
    **Efectos:**
    - Incrementa el cupo actual del grupo en 1
    - Estado inicial: INSCRITO
    
    **Retorna:** Inscripción creada
    
    **Errores:**
    - 400: Estudiante ya inscrito, sin cupos, o grupo no acepta inscripciones
    - 404: Estudiante o grupo no encontrado
    """
    try:
        nueva_inscripcion = inscripcion_service.inscribir_estudiante(
            db=db,
            datos_inscripcion=inscripcion.model_dump()
        )
        return nueva_inscripcion
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al inscribir estudiante: {str(e)}"
        )


@router.get(
    "/estudiante/{estudiante_id}",
    response_model=List[InscripcionPublic],
    summary="Obtener inscripciones del estudiante"
)
def obtener_inscripciones_estudiante(
    estudiante_id: int,
    semestre: Optional[str] = Query(None, description="Filtrar por semestre"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las inscripciones de un estudiante.
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    - **semestre**: Filtrar por semestre (opcional)
    
    **Retorna:** Lista de inscripciones del estudiante
    
    **Útil para:** Ver el historial académico, cursos actuales
    """
    try:
        inscripciones = inscripcion_service.obtener_inscripciones_por_estudiante(
            db=db,
            estudiante_id=estudiante_id,
            semestre=semestre
        )
        return inscripciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener inscripciones: {str(e)}"
        )


@router.get(
    "/grupo/{grupo_id}",
    response_model=List[InscripcionPublic],
    summary="Obtener inscripciones del grupo"
)
def obtener_inscripciones_grupo(
    grupo_id: int,
    estado: Optional[EstadoInscripcion] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las inscripciones de un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    - **estado**: Filtrar por estado (opcional)
    
    **Estados disponibles:**
    - **Inscrito**: Estudiante actualmente inscrito
    - **Retirado**: Estudiante se retiró del curso
    - **Aprobado**: Estudiante aprobó el curso
    - **Reprobado**: Estudiante reprobó el curso
    - **Cancelado**: Inscripción cancelada
    
    **Retorna:** Lista de inscripciones del grupo
    
    **Útil para:** Ver lista de clase, estudiantes activos
    """
    try:
        inscripciones = inscripcion_service.obtener_inscripciones_por_grupo(
            db=db,
            grupo_id=grupo_id,
            estado=estado
        )
        return inscripciones
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener inscripciones: {str(e)}"
        )


@router.get(
    "/estudiante/{estudiante_id}/grupos",
    summary="Obtener grupos inscritos"
)
def obtener_grupos_inscritos(
    estudiante_id: int,
    semestre: Optional[str] = Query(None, description="Filtrar por semestre"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los grupos en los que está inscrito un estudiante.
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    - **semestre**: Filtrar por semestre (opcional)
    
    **Retorna:** Lista de grupos con información completa
    
    **Información incluida:**
    - Datos del grupo
    - Información del curso
    - Datos del profesor
    - Horarios
    
    **Útil para:** Ver carga académica actual del estudiante
    """
    try:
        grupos = inscripcion_service.obtener_grupos_inscritos(
            db=db,
            estudiante_id=estudiante_id,
            semestre=semestre
        )
        return grupos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener grupos: {str(e)}"
        )


@router.get(
    "/estudiante/{estudiante_id}/grupo/{grupo_id}",
    response_model=InscripcionPublic,
    summary="Obtener inscripción específica"
)
def obtener_inscripcion_estudiante_grupo(
    estudiante_id: int,
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene la inscripción de un estudiante en un grupo específico.
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    - **grupo_id**: ID del grupo
    
    **Retorna:** Inscripción del estudiante en el grupo
    
    **Errores:**
    - 404: No existe inscripción
    """
    inscripcion = inscripcion_service.obtener_inscripcion_estudiante_grupo(
        db=db,
        estudiante_id=estudiante_id,
        grupo_id=grupo_id
    )
    
    if not inscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe inscripción del estudiante {estudiante_id} en el grupo {grupo_id}"
        )
    
    return inscripcion


@router.get(
    "/{inscripcion_id}",
    response_model=InscripcionPublic,
    summary="Obtener inscripción por ID"
)
def obtener_inscripcion(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una inscripción por su ID.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción
    
    **Retorna:** Datos de la inscripción con relaciones completas
    
    **Errores:**
    - 404: Inscripción no encontrada
    """
    inscripcion = inscripcion_service.obtener_inscripcion_por_id(db, inscripcion_id)
    if not inscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscripción con ID {inscripcion_id} no encontrada"
        )
    return inscripcion


@router.get(
    "/grupo/{grupo_id}/estadisticas",
    summary="Obtener estadísticas de inscripciones"
)
def obtener_estadisticas(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de inscripciones para un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Retorna:**
    - **total_inscripciones**: Total histórico
    - **inscritos**: Estudiantes actualmente inscritos
    - **retirados**: Estudiantes retirados
    - **aprobados**: Estudiantes que aprobaron
    - **reprobados**: Estudiantes que reprobaron
    - **cancelados**: Inscripciones canceladas
    - **cupos_disponibles**: Espacios libres
    
    **Útil para:** Reportes, monitoreo de grupos
    """
    try:
        estadisticas = inscripcion_service.obtener_estadisticas_inscripcion(db, grupo_id)
        return estadisticas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get(
    "/grupo/{grupo_id}/contar",
    summary="Contar inscripciones del grupo"
)
def contar_inscripciones_grupo(
    grupo_id: int,
    estado: Optional[EstadoInscripcion] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Cuenta el número de inscripciones de un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    - **estado**: Filtrar por estado (opcional)
    
    **Retorna:** Número de inscripciones
    """
    try:
        total = inscripcion_service.contar_inscripciones_por_grupo(
            db=db,
            grupo_id=grupo_id,
            estado=estado
        )
        return {"grupo_id": grupo_id, "total_inscripciones": total}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al contar inscripciones: {str(e)}"
        )


@router.get(
    "/verificar/estudiante/{estudiante_id}/grupo/{grupo_id}",
    summary="Verificar si estudiante está inscrito"
)
def verificar_inscripcion(
    estudiante_id: int,
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Verifica si un estudiante está inscrito en un grupo específico.
    
    **Parámetros:**
    - **estudiante_id**: ID del estudiante
    - **grupo_id**: ID del grupo
    
    **Retorna:**
    - **esta_inscrito**: Boolean
    - **mensaje**: Descripción del estado
    
    **Nota:** Solo verifica inscripciones con estado INSCRITO
    """
    esta_inscrito = inscripcion_service.estudiante_inscrito_en_grupo(
        db=db,
        estudiante_id=estudiante_id,
        grupo_id=grupo_id
    )
    
    return {
        "esta_inscrito": esta_inscrito,
        "mensaje": "El estudiante está inscrito en el grupo" if esta_inscrito 
                  else "El estudiante no está inscrito en el grupo"
    }


@router.put(
    "/{inscripcion_id}",
    response_model=InscripcionPublic,
    summary="Actualizar inscripción"
)
def actualizar_inscripcion(
    inscripcion_id: int,
    datos_actualizados: InscripcionUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una inscripción existente.
    
    **Campos actualizables:**
    - **estado**: Cambiar estado de la inscripción
    - **nota_definitiva**: Asignar nota final (0.0 - 5.0)
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción
    - **datos_actualizados**: Campos a actualizar
    
    **Nota:** Al actualizar el estado, se pueden ajustar cupos del grupo
    
    **Retorna:** Inscripción actualizada
    
    **Errores:**
    - 404: Inscripción no encontrada
    """
    inscripcion = inscripcion_service.obtener_inscripcion_por_id(db, inscripcion_id)
    if not inscripcion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscripción con ID {inscripcion_id} no encontrada"
        )
    
    try:
        # Actualizar campos
        datos = datos_actualizados.model_dump(exclude_unset=True)
        
        if "estado" in datos and datos["estado"]:
            inscripcion = inscripcion_service.cambiar_estado_inscripcion(
                db=db,
                inscripcion_id=inscripcion_id,
                nuevo_estado=datos["estado"]
            )
        
        if "nota_definitiva" in datos and datos["nota_definitiva"] is not None:
            inscripcion = inscripcion_service.actualizar_nota_definitiva(
                db=db,
                inscripcion_id=inscripcion_id,
                nota_definitiva=datos["nota_definitiva"]
            )
        
        return inscripcion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar inscripción: {str(e)}"
        )


@router.patch(
    "/{inscripcion_id}/estado",
    response_model=InscripcionPublic,
    summary="Cambiar estado de inscripción"
)
def cambiar_estado(
    inscripcion_id: int,
    estado_update: InscripcionEstadoUpdate,
    db: Session = Depends(get_db)
):
    """
    Cambia el estado de una inscripción.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción
    - **estado**: Nuevo estado
    
    **Estados disponibles:**
    - **Inscrito**: Activo en el curso
    - **Retirado**: Estudiante se retira
    - **Aprobado**: Curso aprobado
    - **Reprobado**: Curso reprobado
    - **Cancelado**: Inscripción cancelada
    
    **Efectos según el estado:**
    - Retirado/Cancelado: Libera 1 cupo del grupo
    - Inscrito (desde retirado): Ocupa 1 cupo del grupo
    
    **Retorna:** Inscripción actualizada
    
    **Errores:**
    - 404: Inscripción no encontrada
    """
    try:
        inscripcion = inscripcion_service.cambiar_estado_inscripcion(
            db=db,
            inscripcion_id=inscripcion_id,
            nuevo_estado=estado_update.estado
        )
        
        if not inscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscripción con ID {inscripcion_id} no encontrada"
            )
        
        return inscripcion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar estado: {str(e)}"
        )


@router.patch(
    "/{inscripcion_id}/nota",
    response_model=InscripcionPublic,
    summary="Actualizar nota definitiva"
)
def actualizar_nota(
    inscripcion_id: int,
    nota_definitiva: float = Query(..., ge=0.0, le=5.0, description="Nota definitiva"),
    db: Session = Depends(get_db)
):
    """
    Actualiza la nota definitiva de una inscripción.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción
    - **nota_definitiva**: Nota final (0.0 - 5.0)
    
    **Efecto:** Si la nota es >= 3.0, se considera aprobado,
    de lo contrario reprobado (al cerrar la inscripción)
    
    **Retorna:** Inscripción actualizada
    
    **Errores:**
    - 404: Inscripción no encontrada
    """
    try:
        inscripcion = inscripcion_service.actualizar_nota_definitiva(
            db=db,
            inscripcion_id=inscripcion_id,
            nota_definitiva=nota_definitiva
        )
        
        if not inscripcion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inscripción con ID {inscripcion_id} no encontrada"
            )
        
        return inscripcion
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar nota: {str(e)}"
        )


@router.patch(
    "/{inscripcion_id}/retirar",
    response_model=InscripcionPublic,
    summary="Retirar estudiante"
)
def retirar_estudiante(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    """
    Retira un estudiante de un grupo.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción
    
    **Efectos:**
    - Cambia el estado a RETIRADO
    - Libera 1 cupo en el grupo
    
    **Validaciones:**
    - La inscripción no debe estar ya retirada o cancelada
    
    **Retorna:** Inscripción con estado actualizado
    
    **Errores:**
    - 400: Ya está retirado o cancelado
    - 404: Inscripción no encontrada
    """
    try:
        inscripcion = inscripcion_service.retirar_estudiante(db, inscripcion_id)
        return inscripcion
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al retirar estudiante: {str(e)}"
        )


@router.delete(
    "/{inscripcion_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar inscripción"
)
def eliminar_inscripcion(
    inscripcion_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina una inscripción del sistema.
    
    **Parámetros:**
    - **inscripcion_id**: ID de la inscripción
    
    **Retorna:** 204 No Content si se eliminó correctamente
    
    **Errores:**
    - 404: Inscripción no encontrada
    
    **Nota:** Esta operación elimina físicamente el registro.
    Para retirar un estudiante sin eliminar el historial, use PATCH /retirar
    """
    eliminado = inscripcion_service.eliminar_inscripcion(db, inscripcion_id)
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inscripción con ID {inscripcion_id} no encontrada"
        )
    return None
