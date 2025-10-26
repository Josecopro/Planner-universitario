"""
Endpoints para la gestión de programas académicos.

Este módulo maneja las operaciones relacionadas con programas académicos
incluyendo creación, consulta, actualización y gestión de estados.
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.programa_academico import (
    ProgramaAcademicoCreate,
    ProgramaAcademicoUpdate,
    ProgramaAcademicoPublic,
    ProgramaAcademicoEstadoUpdate,
    EstadoPrograma
)
from schemas.estudiante import EstudiantePublic
from services import programa_academico_service

router = APIRouter(prefix="/programas-academicos", tags=["programas-academicos"])


@router.post("/", response_model=ProgramaAcademicoPublic, status_code=status.HTTP_201_CREATED)
def crear_programa(
    programa: ProgramaAcademicoCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Crea un nuevo programa académico.
    
    Args:
        programa: Datos del programa a crear
        db: Sesión de base de datos
    
    Returns:
        ProgramaAcademicoPublic: Programa creado
    
    Raises:
        HTTPException 400: Si la facultad no existe o el código ya está registrado
        HTTPException 500: Si ocurre un error al crear el programa
    """
    try:
        nuevo_programa = programa_academico_service.crear_programa(db, programa.model_dump())
        return nuevo_programa
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear programa: {str(e)}"
        )


@router.get("/", response_model=List[ProgramaAcademicoPublic])
def obtener_programas(
    estado: Optional[EstadoPrograma] = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene todos los programas académicos.
    
    Args:
        estado: Filtrar por estado (opcional)
        db: Sesión de base de datos
    
    Returns:
        List[ProgramaAcademicoPublic]: Lista de programas
    
    Raises:
        HTTPException 500: Si ocurre un error al obtener los programas
    """
    try:
        programas = programa_academico_service.obtener_programas(db, estado=estado)
        return programas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener programas: {str(e)}"
        )


@router.get("/activos", response_model=List[ProgramaAcademicoPublic])
def obtener_programas_activos(
    facultad_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene todos los programas académicos activos.
    
    Args:
        facultad_id: Filtrar por facultad (opcional)
        db: Sesión de base de datos
    
    Returns:
        List[ProgramaAcademicoPublic]: Lista de programas activos
    
    Raises:
        HTTPException 500: Si ocurre un error al obtener los programas
    """
    try:
        programas = programa_academico_service.obtener_programas_activos(db, facultad_id=facultad_id)
        return programas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener programas activos: {str(e)}"
        )


@router.get("/facultad/{facultad_id}", response_model=List[ProgramaAcademicoPublic])
def obtener_programas_por_facultad(
    facultad_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene los programas académicos de una facultad.
    
    Args:
        facultad_id: ID de la facultad
        db: Sesión de base de datos
    
    Returns:
        List[ProgramaAcademicoPublic]: Lista de programas de la facultad
    
    Raises:
        HTTPException 500: Si ocurre un error al obtener los programas
    """
    try:
        programas = programa_academico_service.obtener_programas_por_facultad(db, facultad_id)
        return programas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener programas por facultad: {str(e)}"
        )


@router.get("/con-conteo", response_model=List[Dict[str, Any]])
def obtener_programas_con_conteo(
    facultad_id: Optional[int] = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene programas con el conteo de estudiantes.
    
    Args:
        facultad_id: Filtrar por facultad (opcional)
        db: Sesión de base de datos
    
    Returns:
        List[Dict]: Lista con programas y total de estudiantes
    
    Raises:
        HTTPException 500: Si ocurre un error al obtener los programas
    """
    try:
        resultado = programa_academico_service.obtener_programas_con_conteo_estudiantes(
            db, facultad_id=facultad_id
        )
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener programas con conteo: {str(e)}"
        )


@router.get("/buscar", response_model=List[ProgramaAcademicoPublic])
def buscar_programas(
    termino_busqueda: str = Query(..., min_length=1),
    facultad_id: Optional[int] = None,
    estado: Optional[EstadoPrograma] = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    Busca programas por nombre o código.
    
    Args:
        termino_busqueda: Término a buscar en nombre o código
        facultad_id: Filtrar por facultad (opcional)
        estado: Filtrar por estado (opcional)
        db: Sesión de base de datos
    
    Returns:
        List[ProgramaAcademicoPublic]: Lista de programas que coinciden con la búsqueda
    
    Raises:
        HTTPException 500: Si ocurre un error al buscar programas
    """
    try:
        programas = programa_academico_service.buscar_programas(
            db,
            termino_busqueda=termino_busqueda,
            facultad_id=facultad_id,
            estado=estado
        )
        return programas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar programas: {str(e)}"
        )


@router.get("/codigo/{codigo}", response_model=ProgramaAcademicoPublic)
def obtener_programa_por_codigo(
    codigo: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene un programa académico por su código.
    
    Args:
        codigo: Código del programa
        db: Sesión de base de datos
    
    Returns:
        ProgramaAcademicoPublic: Programa académico encontrado
    
    Raises:
        HTTPException 404: Si el programa no existe
        HTTPException 500: Si ocurre un error al obtener el programa
    """
    try:
        programa = programa_academico_service.obtener_programa_por_codigo(db, codigo)
        if not programa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programa con código '{codigo}' no encontrado"
            )
        return programa
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener programa: {str(e)}"
        )


@router.get("/{programa_id}", response_model=ProgramaAcademicoPublic)
def obtener_programa(
    programa_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene un programa académico por su ID.
    
    Args:
        programa_id: ID del programa
        db: Sesión de base de datos
    
    Returns:
        ProgramaAcademicoPublic: Programa académico encontrado
    
    Raises:
        HTTPException 404: Si el programa no existe
        HTTPException 500: Si ocurre un error al obtener el programa
    """
    try:
        programa = programa_academico_service.obtener_programa_por_id(db, programa_id)
        if not programa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programa con ID {programa_id} no encontrado"
            )
        return programa
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener programa: {str(e)}"
        )


@router.get("/{programa_id}/estudiantes", response_model=List[EstudiantePublic])
def obtener_estudiantes_programa(
    programa_id: int,
    semestre: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene los estudiantes inscritos en un programa.
    
    Args:
        programa_id: ID del programa
        semestre: Filtrar por semestre (opcional)
        db: Sesión de base de datos
    
    Returns:
        List[EstudiantePublic]: Lista de estudiantes del programa
    
    Raises:
        HTTPException 404: Si el programa no existe
        HTTPException 500: Si ocurre un error al obtener los estudiantes
    """
    try:
        if not programa_academico_service.programa_existe(db, programa_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programa con ID {programa_id} no encontrado"
            )
        
        estudiantes = programa_academico_service.obtener_estudiantes_por_programa(
            db, programa_id, semestre=semestre
        )
        return estudiantes
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estudiantes: {str(e)}"
        )


@router.get("/{programa_id}/conteo-estudiantes", response_model=Dict[str, int])
def contar_estudiantes(
    programa_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Cuenta el número de estudiantes en un programa.
    
    Args:
        programa_id: ID del programa
        db: Sesión de base de datos
    
    Returns:
        Dict: Diccionario con el total de estudiantes
    
    Raises:
        HTTPException 404: Si el programa no existe
        HTTPException 500: Si ocurre un error al contar estudiantes
    """
    try:
        if not programa_academico_service.programa_existe(db, programa_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programa con ID {programa_id} no encontrado"
            )
        
        total = programa_academico_service.contar_estudiantes_programa(db, programa_id)
        return {"total_estudiantes": total}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al contar estudiantes: {str(e)}"
        )


@router.get("/{programa_id}/estadisticas", response_model=Dict[str, Any])
def obtener_estadisticas(
    programa_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene estadísticas de un programa académico.
    
    Args:
        programa_id: ID del programa
        db: Sesión de base de datos
    
    Returns:
        Dict: Estadísticas del programa
    
    Raises:
        HTTPException 404: Si el programa no existe
        HTTPException 500: Si ocurre un error al obtener estadísticas
    """
    try:
        estadisticas = programa_academico_service.obtener_estadisticas_programa(db, programa_id)
        
        if estadisticas["programa"] is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programa con ID {programa_id} no encontrado"
            )
        
        return estadisticas
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.put("/{programa_id}", response_model=ProgramaAcademicoPublic)
def actualizar_programa(
    programa_id: int,
    programa: ProgramaAcademicoUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Actualiza un programa académico existente.
    
    Args:
        programa_id: ID del programa a actualizar
        programa: Datos actualizados del programa
        db: Sesión de base de datos
    
    Returns:
        ProgramaAcademicoPublic: Programa actualizado
    
    Raises:
        HTTPException 404: Si el programa no existe
        HTTPException 400: Si el código ya está en uso
        HTTPException 500: Si ocurre un error al actualizar el programa
    """
    try:
        programa_actualizado = programa_academico_service.actualizar_programa(
            db, programa_id, programa.model_dump(exclude_unset=True)
        )
        if not programa_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programa con ID {programa_id} no encontrado"
            )
        return programa_actualizado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar programa: {str(e)}"
        )


@router.patch("/{programa_id}/estado", response_model=ProgramaAcademicoPublic)
def cambiar_estado(
    programa_id: int,
    estado_update: ProgramaAcademicoEstadoUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Cambia el estado de un programa académico.
    
    Args:
        programa_id: ID del programa
        estado_update: Nuevo estado del programa
        db: Sesión de base de datos
    
    Returns:
        ProgramaAcademicoPublic: Programa con estado actualizado
    
    Raises:
        HTTPException 404: Si el programa no existe
        HTTPException 500: Si ocurre un error al cambiar el estado
    """
    try:
        programa_actualizado = programa_academico_service.cambiar_estado_programa(
            db, programa_id, estado_update.estado
        )
        if not programa_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programa con ID {programa_id} no encontrado"
            )
        return programa_actualizado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar estado del programa: {str(e)}"
        )


@router.delete("/{programa_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_programa(
    programa_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Elimina un programa académico.
    
    Args:
        programa_id: ID del programa a eliminar
        db: Sesión de base de datos
    
    Returns:
        None
    
    Raises:
        HTTPException 404: Si el programa no existe
        HTTPException 400: Si el programa tiene estudiantes registrados
        HTTPException 500: Si ocurre un error al eliminar el programa
    """
    try:
        eliminado = programa_academico_service.eliminar_programa(db, programa_id)
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Programa con ID {programa_id} no encontrado"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar programa: {str(e)}"
        )
