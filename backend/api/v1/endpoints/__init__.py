"""
Endpoints package

Este paquete contiene todos los endpoints de la API v1,
organizados por dominio de negocio.
"""

from . import (
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

__all__ = [
    "auth",
    "usuarios",
    "roles",
    "facultades",
    "programas_academicos",
    "cursos",
    "profesores",
    "estudiantes",
    "grupos",
    "horarios",
    "inscripciones",
    "actividades_evaluativas",
    "entregas",
    "calificaciones",
    "asistencias"
]
