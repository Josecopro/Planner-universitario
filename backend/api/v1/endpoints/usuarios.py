"""
Endpoints para la gestión de usuarios del sistema.

Este módulo maneja las operaciones relacionadas con usuarios
incluyendo creación, consulta, actualización, autenticación y gestión de estados.
"""
from typing import List, Any, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.usuario import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioPublic,
    UsuarioPasswordUpdate,
    UsuarioEstadoUpdate
)
from models.usuario import EstadoUsuario
from services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.post("/", response_model=UsuarioPublic, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    usuario: UsuarioCreate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Crea un nuevo usuario en el sistema.
    
    Args:
        usuario: Datos del usuario a crear
        db: Sesión de base de datos
    
    Returns:
        UsuarioPublic: Usuario creado
    
    Raises:
        HTTPException 400: Si el email ya está registrado o el rol no existe
        HTTPException 500: Si ocurre un error al crear el usuario
    """
    try:
        nuevo_usuario = usuario_service.crear_usuario(db, usuario.model_dump())
        return nuevo_usuario
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}"
        )


@router.get("/", response_model=List[UsuarioPublic])
def listar_usuarios(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros"),
    rol_id: Optional[int] = Query(None, description="Filtrar por rol"),
    estado: Optional[EstadoUsuario] = Query(None, description="Filtrar por estado"),
    busqueda: Optional[str] = Query(None, description="Buscar en nombre, apellido o email"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Lista usuarios con filtros y paginación.
    
    Args:
        skip: Número de registros a saltar (paginación)
        limit: Número máximo de registros a retornar
        rol_id: Filtrar por rol (opcional)
        estado: Filtrar por estado (opcional)
        busqueda: Buscar en nombre, apellido o email (opcional)
        db: Sesión de base de datos
    
    Returns:
        List[UsuarioPublic]: Lista de usuarios
    
    Raises:
        HTTPException 500: Si ocurre un error al listar usuarios
    """
    try:
        usuarios = usuario_service.listar_usuarios(
            db,
            skip=skip,
            limit=limit,
            rol_id=rol_id,
            estado=estado,
            busqueda=busqueda
        )
        return usuarios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar usuarios: {str(e)}"
        )


@router.get("/contar", response_model=Dict[str, int])
def contar_usuarios(
    rol_id: Optional[int] = Query(None, description="Filtrar por rol"),
    estado: Optional[EstadoUsuario] = Query(None, description="Filtrar por estado"),
    busqueda: Optional[str] = Query(None, description="Buscar en nombre, apellido o email"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Cuenta el total de usuarios según filtros.
    
    Args:
        rol_id: Filtrar por rol (opcional)
        estado: Filtrar por estado (opcional)
        busqueda: Buscar en nombre, apellido o email (opcional)
        db: Sesión de base de datos
    
    Returns:
        Dict: Diccionario con el total de usuarios
    
    Raises:
        HTTPException 500: Si ocurre un error al contar usuarios
    """
    try:
        total = usuario_service.contar_usuarios(
            db,
            rol_id=rol_id,
            estado=estado,
            busqueda=busqueda
        )
        return {"total_usuarios": total}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al contar usuarios: {str(e)}"
        )


@router.get("/estadisticas", response_model=Dict[str, Any])
def obtener_estadisticas(
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene estadísticas generales de usuarios.
    
    Args:
        db: Sesión de base de datos
    
    Returns:
        Dict: Estadísticas de usuarios (total, activos, inactivos, por rol, etc.)
    
    Raises:
        HTTPException 500: Si ocurre un error al obtener estadísticas
    """
    try:
        estadisticas = usuario_service.obtener_estadisticas_usuarios(db)
        return estadisticas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


@router.get("/buscar", response_model=List[UsuarioPublic])
def buscar_usuarios(
    termino: str = Query(..., min_length=1, description="Término de búsqueda"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de resultados"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Busca usuarios por nombre, apellido o email.
    
    Args:
        termino: Término de búsqueda
        limit: Número máximo de resultados
        db: Sesión de base de datos
    
    Returns:
        List[UsuarioPublic]: Lista de usuarios que coinciden con la búsqueda
    
    Raises:
        HTTPException 500: Si ocurre un error al buscar usuarios
    """
    try:
        usuarios = usuario_service.buscar_usuarios(db, termino, limit=limit)
        return usuarios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar usuarios: {str(e)}"
        )


@router.get("/rol/{rol_nombre}", response_model=List[UsuarioPublic])
def obtener_usuarios_por_rol(
    rol_nombre: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene todos los usuarios de un rol específico.
    
    Args:
        rol_nombre: Nombre del rol (Superadmin, Profesor, Estudiante, etc.)
        db: Sesión de base de datos
    
    Returns:
        List[UsuarioPublic]: Lista de usuarios con ese rol
    
    Raises:
        HTTPException 500: Si ocurre un error al obtener usuarios
    """
    try:
        usuarios = usuario_service.obtener_usuarios_por_rol(db, rol_nombre)
        return usuarios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios por rol: {str(e)}"
        )


@router.get("/email/{email}", response_model=UsuarioPublic)
def obtener_usuario_por_email(
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene un usuario por su email.
    
    Args:
        email: Email del usuario
        db: Sesión de base de datos
    
    Returns:
        UsuarioPublic: Usuario encontrado
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si ocurre un error al obtener el usuario
    """
    try:
        usuario = usuario_service.obtener_usuario_por_email(db, email)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con email '{email}' no encontrado"
            )
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}"
        )


@router.get("/verificar-email/{email}", response_model=Dict[str, bool])
def verificar_email_existe(
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verifica si un email ya está registrado.
    
    Args:
        email: Email a verificar
        db: Sesión de base de datos
    
    Returns:
        Dict: Diccionario indicando si el email existe
    
    Raises:
        HTTPException 500: Si ocurre un error al verificar el email
    """
    try:
        existe = usuario_service.email_existe(db, email)
        return {"email_existe": existe}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar email: {str(e)}"
        )


@router.get("/{usuario_id}", response_model=UsuarioPublic)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene un usuario por su ID.
    
    Args:
        usuario_id: ID del usuario
        db: Sesión de base de datos
    
    Returns:
        UsuarioPublic: Usuario encontrado
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si ocurre un error al obtener el usuario
    """
    try:
        usuario = usuario_service.obtener_usuario_por_id(db, usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}"
        )


@router.get("/{usuario_id}/perfil-completo", response_model=Dict[str, Any])
def obtener_perfil_completo(
    usuario_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Obtiene el perfil completo del usuario incluyendo datos de rol y perfil específico.
    
    Args:
        usuario_id: ID del usuario
        db: Sesión de base de datos
    
    Returns:
        Dict: Perfil completo con usuario, rol, profesor y/o estudiante
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si ocurre un error al obtener el perfil
    """
    try:
        perfil = usuario_service.obtener_perfil_completo(db, usuario_id)
        if not perfil:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        return perfil
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener perfil completo: {str(e)}"
        )


@router.get("/{usuario_id}/puede-iniciar-sesion", response_model=Dict[str, Any])
def verificar_puede_iniciar_sesion(
    usuario_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verifica si un usuario puede iniciar sesión.
    
    Args:
        usuario_id: ID del usuario
        db: Sesión de base de datos
    
    Returns:
        Dict: Indica si puede iniciar sesión y el mensaje correspondiente
    
    Raises:
        HTTPException 500: Si ocurre un error al verificar
    """
    try:
        puede, mensaje = usuario_service.usuario_puede_iniciar_sesion(db, usuario_id)
        return {
            "puede_iniciar_sesion": puede,
            "mensaje": mensaje
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar estado: {str(e)}"
        )


@router.put("/{usuario_id}", response_model=UsuarioPublic)
def actualizar_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Actualiza los datos de un usuario.
    
    Args:
        usuario_id: ID del usuario a actualizar
        usuario: Datos actualizados del usuario
        db: Sesión de base de datos
    
    Returns:
        UsuarioPublic: Usuario actualizado
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 400: Si el nuevo email ya está en uso
        HTTPException 500: Si ocurre un error al actualizar el usuario
    """
    try:
        usuario_actualizado = usuario_service.actualizar_usuario(
            db, usuario_id, usuario.model_dump(exclude_unset=True)
        )
        if not usuario_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        return usuario_actualizado
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
            detail=f"Error al actualizar usuario: {str(e)}"
        )


@router.patch("/{usuario_id}/datos-personales", response_model=UsuarioPublic)
def actualizar_datos_personales(
    usuario_id: int,
    datos: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Any:
    """
    Actualiza datos personales del usuario (nombre, apellido, avatar).
    
    Args:
        usuario_id: ID del usuario
        datos: Diccionario con los datos a actualizar
        db: Sesión de base de datos
    
    Returns:
        UsuarioPublic: Usuario con datos actualizados
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si ocurre un error al actualizar
    """
    try:
        usuario_actualizado = usuario_service.actualizar_datos_personales(
            db, usuario_id, datos
        )
        if not usuario_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        return usuario_actualizado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar datos personales: {str(e)}"
        )


@router.patch("/{usuario_id}/password", response_model=Dict[str, str])
def cambiar_password(
    usuario_id: int,
    password_data: UsuarioPasswordUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Cambia la contraseña de un usuario verificando la antigua.
    
    Args:
        usuario_id: ID del usuario
        password_data: Datos con contraseña actual y nueva
        db: Sesión de base de datos
    
    Returns:
        Dict: Mensaje de éxito
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 400: Si la contraseña actual es incorrecta
        HTTPException 500: Si ocurre un error al cambiar la contraseña
    """
    try:
        cambiado = usuario_service.cambiar_password(
            db,
            usuario_id,
            password_data.password_actual,
            password_data.password_nueva
        )
        if not cambiado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta"
            )
        return {"mensaje": "Contraseña actualizada exitosamente"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )


@router.patch("/{usuario_id}/resetear-password", response_model=Dict[str, str])
def resetear_password(
    usuario_id: int,
    password_nueva: str = Query(..., min_length=8, description="Nueva contraseña"),
    db: Session = Depends(get_db)
) -> Any:
    """
    Resetea la contraseña sin verificar la antigua (para recuperación).
    
    Args:
        usuario_id: ID del usuario
        password_nueva: Nueva contraseña
        db: Sesión de base de datos
    
    Returns:
        Dict: Mensaje de éxito
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si ocurre un error al resetear la contraseña
    """
    try:
        reseteado = usuario_service.resetear_password(db, usuario_id, password_nueva)
        if not reseteado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        return {"mensaje": "Contraseña reseteada exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al resetear contraseña: {str(e)}"
        )


@router.patch("/{usuario_id}/estado", response_model=UsuarioPublic)
def cambiar_estado(
    usuario_id: int,
    estado_update: UsuarioEstadoUpdate,
    db: Session = Depends(get_db)
) -> Any:
    """
    Cambia el estado de un usuario.
    
    Args:
        usuario_id: ID del usuario
        estado_update: Nuevo estado del usuario
        db: Sesión de base de datos
    
    Returns:
        UsuarioPublic: Usuario con estado actualizado
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si ocurre un error al cambiar el estado
    """
    try:
        usuario_actualizado = usuario_service.cambiar_estado_usuario(
            db, usuario_id, estado_update.estado
        )
        if not usuario_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        return usuario_actualizado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar estado: {str(e)}"
        )


@router.patch("/{usuario_id}/activar", response_model=UsuarioPublic)
def activar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Activa un usuario (cambia estado a ACTIVO).
    
    Args:
        usuario_id: ID del usuario
        db: Sesión de base de datos
    
    Returns:
        UsuarioPublic: Usuario activado
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si ocurre un error al activar el usuario
    """
    try:
        usuario_actualizado = usuario_service.activar_usuario(db, usuario_id)
        if not usuario_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        return usuario_actualizado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al activar usuario: {str(e)}"
        )


@router.patch("/{usuario_id}/desactivar", response_model=UsuarioPublic)
def desactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Desactiva un usuario (cambia estado a INACTIVO).
    
    Args:
        usuario_id: ID del usuario
        db: Sesión de base de datos
    
    Returns:
        UsuarioPublic: Usuario desactivado
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si ocurre un error al desactivar el usuario
    """
    try:
        usuario_actualizado = usuario_service.desactivar_usuario(db, usuario_id)
        if not usuario_actualizado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
        return usuario_actualizado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desactivar usuario: {str(e)}"
        )


@router.patch("/{usuario_id}/ultimo-acceso", response_model=Dict[str, str])
def actualizar_ultimo_acceso(
    usuario_id: int,
    db: Session = Depends(get_db)
) -> Any:
    """
    Actualiza la fecha y hora del último acceso del usuario.
    
    Args:
        usuario_id: ID del usuario
        db: Sesión de base de datos
    
    Returns:
        Dict: Mensaje de confirmación
    
    Raises:
        HTTPException 500: Si ocurre un error al actualizar el último acceso
    """
    try:
        usuario_service.actualizar_ultimo_acceso(db, usuario_id)
        return {"mensaje": "Último acceso actualizado"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar último acceso: {str(e)}"
        )


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db)
) -> None:
    """
    Elimina un usuario del sistema.
    
    Args:
        usuario_id: ID del usuario a eliminar
        db: Sesión de base de datos
    
    Returns:
        None
    
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 500: Si ocurre un error al eliminar el usuario
    """
    try:
        eliminado = usuario_service.eliminar_usuario(db, usuario_id)
        if not eliminado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con ID {usuario_id} no encontrado"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar usuario: {str(e)}"
        )
