"""
Endpoints para Grupos

Gestiona los grupos de cursos (secciones), cupos, inscripciones y horarios.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.grupo import (
    GrupoCreate,
    GrupoUpdate,
    GrupoPublic,
    GrupoConDetalles
)
from services import grupo_service
from models.grupo import EstadoGrupo


router = APIRouter()


@router.post(
    "/",
    response_model=GrupoPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear grupo"
)
def crear_grupo(
    grupo: GrupoCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo grupo para un curso.
    
    **Parámetros:**
    - **curso_id**: ID del curso a dictar (requerido)
    - **profesor_id**: ID del profesor asignado (opcional)
    - **semestre**: Periodo académico formato YYYY-N (ej: 2025-1)
    - **cupo_maximo**: Número máximo de estudiantes (1-100)
    
    **Validaciones:**
    - El curso debe existir
    - El profesor debe existir (si se proporciona)
    - Formato de semestre válido (YYYY-N)
    - Cupo entre 1 y 100 estudiantes
    
    **Retorna:** Grupo creado
    
    **Errores:**
    - 400: Datos inválidos o faltantes
    - 404: Curso o profesor no encontrado
    """
    try:
        nuevo_grupo = grupo_service.crear_grupo(
            db=db,
            datos_grupo=grupo.model_dump()
        )
        return nuevo_grupo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear grupo: {str(e)}"
        )


@router.get(
    "/curso/{curso_id}",
    response_model=List[GrupoPublic],
    summary="Obtener grupos por curso"
)
def obtener_grupos_por_curso(
    curso_id: int,
    semestre: Optional[str] = Query(None, description="Filtrar por semestre"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los grupos de un curso.
    
    **Parámetros:**
    - **curso_id**: ID del curso
    - **semestre**: Filtrar por semestre específico (opcional)
    
    **Retorna:** Lista de grupos del curso
    
    **Útil para:** Ver todas las secciones disponibles de un curso
    """
    try:
        grupos = grupo_service.obtener_grupos_por_curso(
            db=db,
            curso_id=curso_id,
            semestre=semestre
        )
        return grupos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener grupos del curso: {str(e)}"
        )


@router.get(
    "/profesor/{profesor_id}",
    response_model=List[GrupoPublic],
    summary="Obtener grupos por profesor"
)
def obtener_grupos_por_profesor(
    profesor_id: int,
    semestre: Optional[str] = Query(None, description="Filtrar por semestre"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los grupos de un profesor.
    
    **Parámetros:**
    - **profesor_id**: ID del profesor
    - **semestre**: Filtrar por semestre específico (opcional)
    
    **Retorna:** Lista de grupos del profesor
    
    **Útil para:** Ver la carga académica de un profesor
    """
    try:
        grupos = grupo_service.obtener_grupos_por_profesor(
            db=db,
            profesor_id=profesor_id,
            semestre=semestre
        )
        return grupos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener grupos del profesor: {str(e)}"
        )


@router.get(
    "/semestre/{semestre}",
    response_model=List[GrupoPublic],
    summary="Obtener grupos por semestre"
)
def obtener_grupos_por_semestre(
    semestre: str,
    estado: Optional[EstadoGrupo] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los grupos de un semestre.
    
    **Parámetros:**
    - **semestre**: Periodo académico (formato: YYYY-N)
    - **estado**: Filtrar por estado del grupo (opcional)
    
    **Retorna:** Lista de grupos del semestre
    
    **Estados disponibles:**
    - Programado: Grupo planificado
    - Abierto: Aceptando inscripciones
    - En Curso: Clases en progreso
    - Finalizado: Curso completado
    - Cancelado: Grupo cancelado
    """
    try:
        grupos = grupo_service.obtener_grupos_por_semestre(
            db=db,
            semestre=semestre,
            estado=estado
        )
        return grupos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener grupos del semestre: {str(e)}"
        )


@router.get(
    "/{grupo_id}",
    response_model=GrupoPublic,
    summary="Obtener grupo por ID"
)
def obtener_grupo(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un grupo por su ID.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Retorna:** Datos del grupo
    
    **Errores:**
    - 404: Grupo no encontrado
    """
    grupo = grupo_service.obtener_grupo_por_id(db, grupo_id)
    if not grupo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Grupo con ID {grupo_id} no encontrado"
        )
    return grupo


@router.get(
    "/{grupo_id}/dashboard",
    summary="Obtener dashboard del grupo"
)
def obtener_dashboard(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un dashboard completo de información del grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Retorna:**
    - **grupo**: Información básica del grupo
    - **curso**: Datos del curso
    - **profesor**: Datos del profesor
    - **cupos**: Información de cupos (actual, máximo, disponibles)
    - **total_estudiantes**: Número de estudiantes inscritos
    - **horarios**: Lista de bloques horarios
    - **actividades_pendientes**: Actividades evaluativas próximas
    
    **Errores:**
    - 404: Grupo no encontrado
    """
    try:
        dashboard = grupo_service.obtener_dashboard(db, grupo_id)
        return dashboard
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener dashboard: {str(e)}"
        )


@router.get(
    "/{grupo_id}/estudiantes",
    summary="Obtener estudiantes inscritos"
)
def obtener_estudiantes_inscritos(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de estudiantes inscritos en un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Retorna:** Lista de estudiantes con sus datos completos
    
    **Información incluida:**
    - Datos del estudiante
    - Datos del usuario (nombre, correo)
    - Información de inscripción
    
    **Errores:**
    - 404: Grupo no encontrado
    """
    try:
        estudiantes = grupo_service.obtener_estudiantes_inscritos(db, grupo_id)
        return estudiantes
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estudiantes: {str(e)}"
        )


@router.get(
    "/{grupo_id}/cupos",
    summary="Obtener información de cupos"
)
def obtener_cupos(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene información detallada de cupos del grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Retorna:**
    - **cupo_maximo**: Capacidad máxima del grupo
    - **cupo_actual**: Estudiantes inscritos actualmente
    - **cupos_disponibles**: Espacios libres
    - **tiene_cupos**: Boolean indicando si hay cupos
    - **porcentaje_ocupacion**: % de ocupación del grupo
    
    **Errores:**
    - 404: Grupo no encontrado
    """
    try:
        grupo = grupo_service.obtener_grupo_por_id(db, grupo_id)
        if not grupo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Grupo con ID {grupo_id} no encontrado"
            )
        
        cupos_disponibles = grupo_service.obtener_cupos_disponibles(db, grupo_id)
        tiene_cupos = grupo_service.grupo_tiene_cupos_disponibles(db, grupo_id)
        
        # Calcular porcentaje de ocupación
        cupo_max = int(grupo.cupo_maximo)  # type: ignore
        cupo_act = int(grupo.cupo_actual)  # type: ignore
        porcentaje = (cupo_act / cupo_max * 100) if cupo_max > 0 else 0.0
        
        return {
            "cupo_maximo": grupo.cupo_maximo,
            "cupo_actual": grupo.cupo_actual,
            "cupos_disponibles": cupos_disponibles,
            "tiene_cupos": tiene_cupos,
            "porcentaje_ocupacion": round(porcentaje, 2)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener información de cupos: {str(e)}"
        )


@router.get(
    "/{grupo_id}/puede-inscribirse",
    summary="Verificar si se puede inscribir"
)
def verificar_inscripcion(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Verifica si un grupo puede aceptar nuevas inscripciones.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Validaciones realizadas:**
    - Grupo existe
    - Estado permite inscripciones (Abierto o Programado)
    - Hay cupos disponibles
    - Tiene profesor asignado
    
    **Retorna:**
    - **puede_inscribir**: Boolean
    - **mensaje**: Razón si no puede inscribirse
    """
    puede, mensaje = grupo_service.grupo_puede_aceptar_inscripciones(db, grupo_id)
    return {
        "puede_inscribir": puede,
        "mensaje": mensaje
    }


@router.put(
    "/{grupo_id}",
    response_model=GrupoPublic,
    summary="Actualizar grupo"
)
def actualizar_grupo(
    grupo_id: int,
    datos_actualizados: GrupoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de un grupo.
    
    **Campos actualizables:**
    - **profesor_id**: Cambiar profesor asignado
    - **semestre**: Cambiar periodo académico
    - **cupo_maximo**: Ajustar capacidad máxima
    - **estado**: Cambiar estado del grupo
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    - **datos_actualizados**: Campos a actualizar
    
    **Retorna:** Grupo actualizado
    
    **Errores:**
    - 404: Grupo no encontrado
    - 400: Datos inválidos
    """
    try:
        # Si se está cambiando el profesor, usar la función específica
        if datos_actualizados.profesor_id is not None:
            grupo = grupo_service.actualizar_profesor(
                db=db,
                grupo_id=grupo_id,
                profesor_id=datos_actualizados.profesor_id
            )
        else:
            # Para otros cambios, obtener el grupo y actualizar
            grupo = grupo_service.obtener_grupo_por_id(db, grupo_id)
            if not grupo:
                raise ValueError(f"El grupo con ID {grupo_id} no existe")
            
            # Actualizar campos permitidos
            datos = datos_actualizados.model_dump(exclude_unset=True)
            for campo, valor in datos.items():
                if campo == "estado" and valor is not None:
                    grupo = grupo_service.cambiar_estado_grupo(db, grupo_id, valor)
                elif campo in ["semestre", "cupo_maximo"]:
                    setattr(grupo, campo, valor)
            
            db.commit()
            db.refresh(grupo)
        
        return grupo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar grupo: {str(e)}"
        )


@router.patch(
    "/{grupo_id}/profesor",
    response_model=GrupoPublic,
    summary="Cambiar profesor del grupo"
)
def cambiar_profesor(
    grupo_id: int,
    nuevo_profesor_id: int = Query(..., description="ID del nuevo profesor"),
    db: Session = Depends(get_db)
):
    """
    Cambia el profesor asignado a un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    - **nuevo_profesor_id**: ID del nuevo profesor
    
    **Validaciones:**
    - El grupo debe existir
    - El profesor debe existir
    
    **Retorna:** Grupo con el profesor actualizado
    
    **Errores:**
    - 404: Grupo o profesor no encontrado
    """
    try:
        grupo = grupo_service.actualizar_profesor(
            db=db,
            grupo_id=grupo_id,
            profesor_id=nuevo_profesor_id
        )
        return grupo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar profesor: {str(e)}"
        )


@router.patch(
    "/{grupo_id}/estado",
    response_model=GrupoPublic,
    summary="Cambiar estado del grupo"
)
def cambiar_estado(
    grupo_id: int,
    nuevo_estado: EstadoGrupo = Query(..., description="Nuevo estado del grupo"),
    db: Session = Depends(get_db)
):
    """
    Cambia el estado de un grupo.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    - **nuevo_estado**: Nuevo estado
    
    **Estados disponibles:**
    - **Programado**: Grupo planificado para futuro
    - **Abierto**: Aceptando inscripciones
    - **En Curso**: Clases en progreso
    - **Finalizado**: Curso completado
    - **Cancelado**: Grupo cancelado
    
    **Retorna:** Grupo con el estado actualizado
    
    **Errores:**
    - 404: Grupo no encontrado
    """
    try:
        grupo = grupo_service.cambiar_estado_grupo(
            db=db,
            grupo_id=grupo_id,
            nuevo_estado=nuevo_estado
        )
        return grupo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar estado: {str(e)}"
        )


@router.patch(
    "/{grupo_id}/cancelar",
    response_model=GrupoPublic,
    summary="Cancelar grupo"
)
def cancelar_grupo(
    grupo_id: int,
    db: Session = Depends(get_db)
):
    """
    Cancela un grupo cambiando su estado a CANCELADO.
    
    **Parámetros:**
    - **grupo_id**: ID del grupo
    
    **Acción:** Cambia el estado del grupo a Cancelado
    
    **Retorna:** Grupo cancelado
    
    **Errores:**
    - 404: Grupo no encontrado
    
    **Nota:** Esta es una operación de solo cambio de estado.
    No elimina el grupo ni afecta inscripciones existentes.
    """
    try:
        grupo = grupo_service.cancelar_grupo(db, grupo_id)
        return grupo
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar grupo: {str(e)}"
        )
