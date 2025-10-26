"""
Endpoints para la gestión de roles del sistema.

Este módulo maneja las operaciones relacionadas con roles
incluyendo creación, consulta, actualización y eliminación.
"""
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from core.security import get_current_superadmin, get_current_active_user
from schemas.rol import (
    RolCreate,
    RolUpdate,
    RolPublic
)
from schemas.usuario import UsuarioPublic
from services import rol_service

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RolPublic, status_code=status.HTTP_201_CREATED)
def crear_rol(
    rol: RolCreate,
    current_user = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Crea un nuevo rol en el sistema.
    
    **REQUIERE:** Rol de Superadmin
    
    Args:
        rol: Datos del rol a crear
        current_user: Usuario autenticado (Superadmin)
        db: Sesión de base de datos
    
    Returns:
        RolPublic: Rol creado
    
    Raises:
        HTTPException 403: Si no es Superadmin
        HTTPException 400: Si el nombre del rol ya existe
        HTTPException 500: Si ocurre un error al crear el rol
    """
    try:
        nuevo_rol = rol_service.crear_rol(db, rol.model_dump())
        return nuevo_rol
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear rol: {str(e)}"
        )


@router.get("/", response_model=List[RolPublic])
def obtener_roles(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene todos los roles del sistema.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        List[RolPublic]: Lista de roles ordenados por nombre
    
    Raises:
        HTTPException 500: Si ocurre un error al obtener los roles
    """
    try:
        roles = rol_service.obtener_roles(db)
        return roles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener roles: {str(e)}"
        )


@router.get("/inicializar", response_model=List[RolPublic])
def inicializar_roles(
    db: Session = Depends(get_db)
) -> Any:
    """
    Inicializa los roles básicos del sistema (Superadmin, Profesor, Estudiante).
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        List[RolPublic]: Lista de roles creados o existentes
    
    Raises:
        HTTPException 500: Si ocurre un error al inicializar roles
    """
    try:
        roles = rol_service.inicializar_roles_sistema(db)
        return roles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al inicializar roles: {str(e)}"
        )


@router.get("/buscar", response_model=List[RolPublic])
def buscar_roles(
    termino: str = Query(..., min_length=1, description="Término de búsqueda en nombre o descripción"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Busca roles por nombre o descripción.
    
    Args:
        termino: Término a buscar en nombre o descripción
        db: Sesión de base de datos
    
    Returns:
        List[RolPublic]: Lista de roles que coinciden con la búsqueda
    
    Raises:
        HTTPException 500: Si ocurre un error al buscar roles
    """
    try:
        roles = rol_service.buscar_roles(db, termino)
        return roles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar roles: {str(e)}"
        )


@router.get("/nombre/{nombre}", response_model=RolPublic)
def obtener_rol_por_nombre(
    nombre: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene un rol por su nombre.
    
    Args:
        nombre: Nombre del rol
        db: Sesión de base de datos
    
    Returns:
        RolPublic: Rol encontrado
    
    Raises:
        HTTPException 404: Si el rol no existe
        HTTPException 500: Si ocurre un error al obtener el rol
    """
    try:
        rol = rol_service.obtener_rol_por_nombre(db, nombre)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con nombre '{nombre}' no encontrado"
            )
        return rol
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener rol: {str(e)}"
        )


@router.get("/{rol_id}", response_model=RolPublic)
def obtener_rol(
    rol_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene un rol por su ID.
    
    Args:
        rol_id: ID del rol
        db: Sesión de base de datos
    
    Returns:
        RolPublic: Rol encontrado
    
    Raises:
        HTTPException 404: Si el rol no existe
        HTTPException 500: Si ocurre un error al obtener el rol
    """
    try:
        rol = rol_service.obtener_rol_por_id(db, rol_id)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rol con ID {rol_id} no encontrado"
            )
        return rol
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener rol: {str(e)}"
        )


@router.get("/{rol_id}/usuarios", response_model=List[UsuarioPublic])
def obtener_usuarios_del_rol(
    rol_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene todos los usuarios que tienen un rol específico.
    
    Args:
        rol_id: ID del rol
        db: Sesión de base de datos
    
    Returns:
        List[UsuarioPublic]: Lista de usuarios con ese rol
    
    Raises:
        HTTPException 404: Si el rol no existe
        HTTPException 500: Si ocurre un error al obtener los usuarios
    """
    try:
        usuarios = rol_service.obtener_usuarios_por_rol(db, rol_id)
        return usuarios
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios del rol: {str(e)}"
        )


@router.get("/{rol_id}/conteo-usuarios", response_model=dict)
def contar_usuarios_del_rol(
    rol_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Cuenta cuántos usuarios tienen un rol específico.
    
    Args:
        rol_id: ID del rol
        db: Sesión de base de datos
    
    Returns:
        dict: Diccionario con el total de usuarios
    
    Raises:
        HTTPException 404: Si el rol no existe
        HTTPException 500: Si ocurre un error al contar usuarios
    """
    try:
        total = rol_service.contar_usuarios_por_rol(db, rol_id)
        return {"total_usuarios": total}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al contar usuarios: {str(e)}"
        )


@router.patch("/{rol_id}/descripcion", response_model=RolPublic)
def actualizar_descripcion(
    rol_id: int,
    nueva_descripcion: str = Query(..., min_length=1, description="Nueva descripción del rol"),
    current_user = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
) -> Any:
    """
    Actualiza la descripción de un rol.
    
    **REQUIERE:** Rol de Superadmin
    
    Args:
        rol_id: ID del rol a actualizar
        nueva_descripcion: Nueva descripción del rol
        current_user: Usuario autenticado (Superadmin)
        db: Sesión de base de datos
    
    Returns:
        RolPublic: Rol con descripción actualizada
    
    Raises:
        HTTPException 403: Si no es Superadmin
        HTTPException 404: Si el rol no existe
        HTTPException 500: Si ocurre un error al actualizar el rol
    """
    try:
        rol_actualizado = rol_service.actualizar_descripcion_rol(db, rol_id, nueva_descripcion)
        return rol_actualizado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar rol: {str(e)}"
        )


@router.delete("/{rol_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rol(
    rol_id: int,
    current_user = Depends(get_current_superadmin),
    db: Session = Depends(get_db)
) -> None:
    """
    Elimina un rol del sistema.
    
    **REQUIERE:** Rol de Superadmin
    **SEGURIDAD:** Solo el Superadmin puede eliminar roles del sistema.
    
    Args:
        rol_id: ID del rol a eliminar
        current_user: Usuario autenticado (Superadmin)
        db: Sesión de base de datos
    
    Returns:
        None
    
    Raises:
        HTTPException 403: Si no es Superadmin
        HTTPException 404: Si el rol no existe
        HTTPException 400: Si el rol tiene usuarios asociados
        HTTPException 500: Si ocurre un error al eliminar el rol
    """
    try:
        rol_service.eliminar_rol(db, rol_id)
    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar rol: {str(e)}"
        )
