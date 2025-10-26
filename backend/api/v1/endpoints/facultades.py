"""
Endpoints para Facultades

Gestiona las facultades de la universidad.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_superadmin
from schemas.facultad import (
    FacultadCreate,
    FacultadUpdate,
    FacultadPublic,
    FacultadList,
    FacultadConContadores
)
from services import facultad_service


router = APIRouter()


@router.post(
    "/",
    response_model=FacultadPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear facultad"
)
def crear_facultad(
    facultad: FacultadCreate,
    current_user = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva facultad en el sistema.
    
    **REQUIERE:** Rol de Superadmin
    
    **Parámetros:**
    - **codigo**: Código único de la facultad (ej: ING, CIEN, ADMIN)
    - **nombre**: Nombre completo de la facultad
    
    **Validaciones:**
    - El código debe ser único en el sistema
    - El nombre debe ser único en el sistema
    - Ambos campos son requeridos
    
    **Retorna:** Facultad creada
    
    **Errores:**
    - 403: Si no es Superadmin
    - 400: Código o nombre duplicado, o datos faltantes
    """
    try:
        nueva_facultad = facultad_service.crear_facultad(
            db=db,
            datos_facultad=facultad.model_dump()
        )
        return nueva_facultad
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear facultad: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[FacultadList],
    summary="Listar todas las facultades"
)
def listar_facultades(
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las facultades del sistema ordenadas por nombre.
    
    **Retorna:** Lista de todas las facultades
    
    **Información incluida:**
    - ID de la facultad
    - Código único
    - Nombre completo
    """
    try:
        facultades = facultad_service.obtener_facultades(db)
        return facultades
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar facultades: {str(e)}"
        )


@router.get(
    "/resumen",
    summary="Obtener resumen de facultades"
)
def obtener_resumen_facultades(
    db: Session = Depends(get_db)
):
    """
    Obtiene un resumen de todas las facultades con estadísticas.
    
    **Retorna:** Lista de facultades con contadores de:
    - Total de programas académicos
    - Total de cursos ofrecidos
    - Total de profesores adscritos
    
    **Útil para:** Dashboards, reportes administrativos
    """
    try:
        resumen = facultad_service.obtener_resumen_facultades(db)
        return resumen
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener resumen de facultades: {str(e)}"
        )


@router.get(
    "/buscar",
    response_model=List[FacultadPublic],
    summary="Buscar facultades"
)
def buscar_facultades(
    termino: str = Query(..., min_length=1, description="Término de búsqueda"),
    db: Session = Depends(get_db)
):
    """
    Busca facultades por código o nombre.
    
    **Parámetros:**
    - **termino**: Término de búsqueda (requerido)
    
    **Búsqueda:**
    - Busca en código de facultad
    - Busca en nombre de facultad
    - No distingue mayúsculas/minúsculas
    - Soporta búsqueda parcial
    
    **Retorna:** Lista de facultades que coinciden con el término
    
    **Ejemplo:**
    - termino="ING" → Encuentra "Facultad de Ingeniería"
    - termino="ciencias" → Encuentra "Facultad de Ciencias"
    """
    try:
        resultados = facultad_service.buscar_facultades(db, termino)
        return resultados
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar facultades: {str(e)}"
        )


@router.get(
    "/codigo/{codigo}",
    response_model=FacultadPublic,
    summary="Obtener facultad por código"
)
def obtener_facultad_por_codigo(
    codigo: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene una facultad por su código único.
    
    **Parámetros:**
    - **codigo**: Código único de la facultad
    
    **Retorna:** Datos de la facultad
    
    **Errores:**
    - 404: Facultad no encontrada
    """
    facultad = facultad_service.obtener_facultad_por_codigo(db, codigo)
    if not facultad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró facultad con código '{codigo}'"
        )
    return facultad


@router.get(
    "/{facultad_id}",
    response_model=FacultadPublic,
    summary="Obtener facultad por ID"
)
def obtener_facultad(
    facultad_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una facultad por su ID.
    
    **Parámetros:**
    - **facultad_id**: ID de la facultad
    
    **Retorna:** Datos de la facultad
    
    **Errores:**
    - 404: Facultad no encontrada
    """
    facultad = facultad_service.obtener_facultad_por_id(db, facultad_id)
    if not facultad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facultad con ID {facultad_id} no encontrada"
        )
    return facultad


@router.get(
    "/{facultad_id}/estadisticas",
    response_model=FacultadConContadores,
    summary="Obtener estadísticas de la facultad"
)
def obtener_estadisticas(
    facultad_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas completas de una facultad.
    
    **Parámetros:**
    - **facultad_id**: ID de la facultad
    
    **Retorna:**
    - Datos básicos de la facultad
    - **total_programas**: Número de programas académicos
    - **total_cursos**: Número de cursos ofrecidos
    - **total_profesores**: Número de profesores adscritos
    
    **Errores:**
    - 404: Facultad no encontrada
    """
    try:
        facultad = facultad_service.obtener_facultad_por_id(db, facultad_id)
        if not facultad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Facultad con ID {facultad_id} no encontrada"
            )
        
        estadisticas = facultad_service.obtener_estadisticas_facultad(db, facultad_id)
        
        return {
            "id": facultad.id,
            "codigo": facultad.codigo,
            "nombre": facultad.nombre,
            "total_programas": estadisticas["total_programas"],
            "total_cursos": estadisticas["total_cursos"],
            "total_profesores": estadisticas["total_profesores"]
        }
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
    "/{facultad_id}/profesores",
    summary="Obtener profesores de la facultad"
)
def obtener_profesores(
    facultad_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los profesores adscritos a una facultad.
    
    **Parámetros:**
    - **facultad_id**: ID de la facultad
    
    **Retorna:** Lista de profesores de la facultad
    
    **Información incluida:**
    - Datos del profesor
    - Información del usuario asociado
    
    **Errores:**
    - 404: Facultad no encontrada
    """
    try:
        profesores = facultad_service.obtener_profesores_por_facultad(db, facultad_id)
        return profesores
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener profesores: {str(e)}"
        )


@router.get(
    "/{facultad_id}/cursos",
    summary="Obtener cursos de la facultad"
)
def obtener_cursos(
    facultad_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los cursos que pertenecen a una facultad.
    
    **Parámetros:**
    - **facultad_id**: ID de la facultad
    
    **Retorna:** Lista de cursos de la facultad
    
    **Información incluida:**
    - Código del curso
    - Nombre del curso
    - Créditos
    - Horas semanales
    - Estado
    
    **Errores:**
    - 404: Facultad no encontrada
    """
    try:
        cursos = facultad_service.obtener_cursos_por_facultad(db, facultad_id)
        return cursos
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cursos: {str(e)}"
        )


@router.put(
    "/{facultad_id}",
    response_model=FacultadPublic,
    summary="Actualizar facultad"
)
def actualizar_facultad(
    facultad_id: int,
    datos_actualizados: FacultadUpdate,
    current_user = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
):
    """
    Actualiza los datos de una facultad.
    
    **REQUIERE:** Rol de Superadmin
    
    **Campos actualizables:**
    - **codigo**: Código único de la facultad
    - **nombre**: Nombre completo de la facultad
    
    **Parámetros:**
    - **facultad_id**: ID de la facultad
    - **datos_actualizados**: Campos a actualizar
    
    **Validaciones:**
    - El nuevo código no debe existir (si se cambia)
    - El nuevo nombre no debe existir (si se cambia)
    
    **Retorna:** Facultad actualizada
    
    **Errores:**
    - 403: Si no es Superadmin
    - 400: Código o nombre duplicado
    - 404: Facultad no encontrada
    """
    try:
        facultad_actualizada = facultad_service.actualizar_facultad(
            db=db,
            facultad_id=facultad_id,
            datos_actualizados=datos_actualizados.model_dump(exclude_unset=True)
        )
        return facultad_actualizada
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar facultad: {str(e)}"
        )
