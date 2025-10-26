"""
API Router v1

Agrupa todos los routers de endpoints de la API v1.
Organiza las rutas por dominio de negocio.
"""

from fastapi import APIRouter

from api.v1.endpoints import (
    auth,
    usuarios,
    roles,
    facultades,
    programas_academicos,
    cursos,
    profesores,
    estudiantes,
    grupos,
    horarios,
    inscripciones,
    actividades_evaluativas,
    entregas,
    calificaciones,
    asistencias
)

api_router = APIRouter()


api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Autenticación"]
)


api_router.include_router(
    usuarios.router,
    prefix="/usuarios",
    tags=["Usuarios"]
)

api_router.include_router(
    roles.router,
    prefix="/roles",
    tags=["Roles"]
)


api_router.include_router(
    facultades.router,
    prefix="/facultades",
    tags=["Facultades"]
)

api_router.include_router(
    programas_academicos.router,
    prefix="/programas-academicos",
    tags=["Programas Académicos"]
)

api_router.include_router(
    cursos.router,
    prefix="/cursos",
    tags=["Cursos"]
)


api_router.include_router(
    profesores.router,
    prefix="/profesores",
    tags=["Profesores"]
)

api_router.include_router(
    estudiantes.router,
    prefix="/estudiantes",
    tags=["Estudiantes"]
)


api_router.include_router(
    grupos.router,
    prefix="/grupos",
    tags=["Grupos"]
)

api_router.include_router(
    horarios.router,
    prefix="/horarios",
    tags=["Horarios"]
)

api_router.include_router(
    inscripciones.router,
    prefix="/inscripciones",
    tags=["Inscripciones"]
)


api_router.include_router(
    actividades_evaluativas.router,
    prefix="/actividades-evaluativas",
    tags=["Actividades Evaluativas"]
)

api_router.include_router(
    entregas.router,
    prefix="/entregas",
    tags=["Entregas"]
)

api_router.include_router(
    calificaciones.router,
    prefix="/calificaciones",
    tags=["Calificaciones"]
)

api_router.include_router(
    asistencias.router,
    prefix="/asistencias",
    tags=["Asistencias"]
)
