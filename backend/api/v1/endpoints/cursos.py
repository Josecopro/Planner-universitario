"""
Endpoints de API para Cursos
Rutas: /api/v1/cursos
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.curso import (
    CursoCreate,
    CursoUpdate,
    CursoPublic,
    CursoList,
    CursoEstadoUpdate
)
from services import curso_service
from models.curso import EstadoCurso


router = APIRouter()


@router.post(
    "/",
    response_model=CursoPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Crear curso",
    description="Crea un nuevo curso en el catálogo académico"
)
def crear_curso(
    curso_data: CursoCreate,
    db: Session = Depends(get_db)
):
    """
    Crea un nuevo curso en el catálogo.
    
    **Parámetros:**
    - **codigo**: Código único del curso (ej: IS-101, MAT-201)
    - **nombre**: Nombre del curso
    - **facultad_id**: ID de la facultad a la que pertenece
    
    **Retorna:**
    - Curso creado con su ID
    
    **Excepciones:**
    - **404**: Facultad no encontrada
    - **400**: Código ya existe o formato inválido
    """
    try:
        curso = curso_service.crear_curso(
            db=db,
            datos_curso=curso_data.model_dump()
        )
        return curso
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear curso: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[CursoList],
    summary="Listar cursos",
    description="Obtiene lista de cursos con filtros opcionales"
)
def listar_cursos(
    facultad_id: Optional[int] = Query(None, description="Filtrar por facultad"),
    estado: Optional[EstadoCurso] = Query(None, description="Filtrar por estado"),
    codigo: Optional[str] = Query(None, description="Buscar por código (parcial)"),
    nombre: Optional[str] = Query(None, description="Buscar por nombre (parcial)"),
    db: Session = Depends(get_db)
):
    """
    Lista cursos con filtros opcionales.
    
    **Parámetros de Query:**
    - **facultad_id**: Filtrar por facultad específica
    - **estado**: Filtrar por estado (Activo, Inactivo, En Revision)
    - **codigo**: Buscar por código (búsqueda parcial)
    - **nombre**: Buscar por nombre (búsqueda parcial)
    
    **Retorna:**
    - Lista de cursos que cumplen los criterios
    """
    try:
        filtros = {}
        if facultad_id:
            filtros["facultad_id"] = facultad_id
        if estado:
            filtros["estado"] = estado
        if codigo:
            filtros["codigo"] = codigo
        if nombre:
            filtros["nombre"] = nombre
        
        cursos = curso_service.obtener_cursos(
            db=db,
            filtros=filtros if filtros else None
        )
        return cursos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cursos: {str(e)}"
        )


@router.get(
    "/facultad/{facultad_id}",
    response_model=List[CursoList],
    summary="Obtener cursos de una facultad",
    description="Obtiene todos los cursos de una facultad específica"
)
def obtener_cursos_facultad(
    facultad_id: int,
    solo_activos: bool = Query(True, description="Solo cursos activos"),
    db: Session = Depends(get_db)
):
    """
    Obtiene todos los cursos de una facultad.
    
    **Parámetros:**
    - **facultad_id**: ID de la facultad
    
    **Parámetros de Query:**
    - **solo_activos**: Si es True, solo devuelve cursos activos (default: True)
    
    **Retorna:**
    - Lista de cursos de la facultad
    """
    try:
        cursos = curso_service.obtener_cursos_por_facultad(
            db=db,
            facultad_id=facultad_id,
            solo_activos=solo_activos
        )
        return cursos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cursos: {str(e)}"
        )


@router.get(
    "/buscar",
    response_model=List[CursoList],
    summary="Buscar cursos",
    description="Busca cursos por texto en código o nombre"
)
def buscar_cursos(
    termino: str = Query(..., min_length=1, description="Término de búsqueda"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
    db: Session = Depends(get_db)
):
    """
    Busca cursos por texto en código o nombre.
    
    **Parámetros de Query:**
    - **termino**: Texto a buscar (mínimo 1 carácter)
    - **limit**: Máximo de resultados (default: 20, max: 100)
    
    **Retorna:**
    - Lista de cursos que coinciden con la búsqueda
    """
    try:
        cursos = curso_service.buscar_cursos(
            db=db,
            termino=termino,
            limit=limit
        )
        return cursos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar cursos: {str(e)}"
        )


@router.get(
    "/codigo/{codigo}",
    response_model=CursoPublic,
    summary="Obtener curso por código",
    description="Obtiene un curso específico por su código único"
)
def obtener_curso_por_codigo(
    codigo: str,
    db: Session = Depends(get_db)
):
    """
    Obtiene un curso por su código.
    
    **Parámetros:**
    - **codigo**: Código del curso (ej: IS-101)
    
    **Retorna:**
    - Curso encontrado
    
    **Excepciones:**
    - **404**: Curso no encontrado
    """
    curso = curso_service.obtener_curso_por_codigo(
        db=db,
        codigo=codigo
    )
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con código {codigo} no encontrado"
        )
    return curso


@router.get(
    "/{curso_id}",
    response_model=CursoPublic,
    summary="Obtener curso por ID",
    description="Obtiene un curso específico por su ID"
)
def obtener_curso(
    curso_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene un curso por su ID.
    
    **Parámetros:**
    - **curso_id**: ID del curso
    
    **Retorna:**
    - Curso con todos sus detalles
    
    **Excepciones:**
    - **404**: Curso no encontrado
    """
    curso = curso_service.obtener_curso_por_id(
        db=db,
        curso_id=curso_id
    )
    if not curso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Curso con ID {curso_id} no encontrado"
        )
    return curso


@router.get(
    "/{curso_id}/grupos",
    response_model=List[dict],
    summary="Obtener grupos de un curso",
    description="Obtiene todos los grupos asociados a un curso"
)
def obtener_grupos_curso(
    curso_id: int,
    semestre: Optional[str] = Query(None, description="Filtrar por semestre (ej: 2025-1)"),
    db: Session = Depends(get_db)
):
    """
    Obtiene los grupos de un curso.
    
    **Parámetros:**
    - **curso_id**: ID del curso
    
    **Parámetros de Query:**
    - **semestre**: Filtrar por semestre específico (opcional)
    
    **Retorna:**
    - Lista de grupos del curso
    
    **Excepciones:**
    - **404**: Curso no encontrado
    """
    try:
        grupos = curso_service.obtener_grupos_por_curso(
            db=db,
            curso_id=curso_id,
            semestre=semestre
        )
        return [
            {
                "id": g.id,
                "semestre": g.semestre,
                "cupo_maximo": g.cupo_maximo,
                "cupo_actual": g.cupo_actual,
                "estado": g.estado.value if hasattr(g.estado, 'value') else g.estado,
                "profesor_id": g.profesor_id
            }
            for g in grupos
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener grupos: {str(e)}"
        )


@router.get(
    "/{curso_id}/estadisticas",
    response_model=dict,
    summary="Obtener estadísticas de un curso",
    description="Obtiene estadísticas generales de un curso"
)
def obtener_estadisticas_curso(
    curso_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas de un curso.
    
    **Parámetros:**
    - **curso_id**: ID del curso
    
    **Retorna:**
    - Diccionario con estadísticas:
        - total_grupos: Total de grupos históricos
        - grupos_activos: Grupos actualmente activos
        - total_estudiantes: Total de estudiantes que lo han cursado
        - promedio_estudiantes: Promedio por grupo
    
    **Excepciones:**
    - **404**: Curso no encontrado
    """
    try:
        estadisticas = curso_service.obtener_estadisticas_curso(
            db=db,
            curso_id=curso_id
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


@router.put(
    "/{curso_id}",
    response_model=CursoPublic,
    summary="Actualizar curso",
    description="Actualiza la información de un curso existente"
)
def actualizar_curso(
    curso_id: int,
    curso_data: CursoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un curso existente.
    
    **Parámetros:**
    - **curso_id**: ID del curso a actualizar
    - **curso_data**: Datos a actualizar (todos opcionales):
        - codigo: Nuevo código
        - nombre: Nuevo nombre
        - estado: Nuevo estado
        - facultad_id: Nueva facultad
    
    **Retorna:**
    - Curso actualizado
    
    **Excepciones:**
    - **404**: Curso no encontrado
    - **400**: Código ya existe o facultad inválida
    """
    try:
        curso = curso_service.actualizar_curso(
            db=db,
            curso_id=curso_id,
            datos_actualizacion=curso_data.model_dump(exclude_unset=True)
        )
        return curso
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar curso: {str(e)}"
        )


@router.patch(
    "/{curso_id}/estado",
    response_model=CursoPublic,
    summary="Cambiar estado de curso",
    description="Cambia únicamente el estado de un curso (Activo, Inactivo, En Revision)"
)
def cambiar_estado_curso(
    curso_id: int,
    estado_data: CursoEstadoUpdate,
    db: Session = Depends(get_db)
):
    """
    Cambia el estado de un curso.
    
    **Parámetros:**
    - **curso_id**: ID del curso
    - **estado_data**: Nuevo estado
    
    **Retorna:**
    - Curso con estado actualizado
    
    **Excepciones:**
    - **404**: Curso no encontrado
    """
    try:
        curso = curso_service.actualizar_curso(
            db=db,
            curso_id=curso_id,
            datos_actualizacion={"estado": estado_data.estado}
        )
        return curso
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
    "/{curso_id}/desactivar",
    response_model=CursoPublic,
    summary="Desactivar curso",
    description="Desactiva un curso (cambia estado a Inactivo)"
)
def desactivar_curso(
    curso_id: int,
    db: Session = Depends(get_db)
):
    """
    Desactiva un curso.
    
    **Parámetros:**
    - **curso_id**: ID del curso a desactivar
    
    **Retorna:**
    - Curso desactivado
    
    **Excepciones:**
    - **404**: Curso no encontrado
    - **400**: Curso tiene grupos activos (no se puede desactivar)
    """
    try:
        curso = curso_service.desactivar_curso(
            db=db,
            curso_id=curso_id
        )
        return curso
    except ValueError as e:
        # Puede ser 404 o 400 dependiendo del mensaje
        if "no existe" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desactivar curso: {str(e)}"
        )
