"""
API Router v1

Agrupa todos los routers de endpoints de la API v1.
Organiza las rutas por dominio de negocio.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

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

@api_router.get(
    "/",
    tags=["API Info"],
    summary="Información de la API v1",
    response_description="Listado completo de endpoints disponibles"
)
async def api_v1_info():
    """
    Endpoint raíz de la API v1.
    
    Proporciona información general sobre la API y un listado completo
    de todos los endpoints disponibles organizados por categoría.
    
    **Incluye:**
    - Información general de la API
    - Enlaces a documentación
    - Guía de autenticación
    - Listado completo de endpoints por categoría
    - Descripción de cada endpoint
    
    **No requiere autenticación**
    """
    return JSONResponse({
        "message": "Planner Universitario API v1",
        "version": "1.0.0",
        "status": "active",
        "description": "Sistema de gestión académica universitaria",
        
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        
        "authentication": {
            "type": "JWT Bearer Token",
            "login_endpoint": "/api/v1/auth/login",
            "token_expiration": "24 hours",
            "steps": [
                "1. POST /api/v1/auth/login with {email, password}",
                "2. Copy the 'access_token' from response",
                "3. Use 'Authorization: Bearer <token>' header in protected requests",
                "4. Token expires in 24 hours, login again if needed"
            ]
        },
        
        "roles": {
            "Superadmin": "Full access to all endpoints and system administration",
            "Profesor": "Manage groups, grades, attendance, and academic activities",
            "Estudiante": "View own data, submit assignments, and enroll in courses"
        },
        
        "endpoints": {
            "authentication": {
                "base": "/api/v1/auth",
                "endpoints": [
                    {"method": "POST", "path": "/api/v1/auth/login", "description": "Login and get JWT token", "auth": "Public"},
                    {"method": "GET", "path": "/api/v1/auth/me", "description": "Get current user info", "auth": "Required"},
                    {"method": "POST", "path": "/api/v1/auth/change-password", "description": "Change user password", "auth": "Required"},
                    {"method": "POST", "path": "/api/v1/auth/verify-token", "description": "Verify token validity", "auth": "Required"},
                    {"method": "POST", "path": "/api/v1/auth/logout", "description": "Logout (invalidate token)", "auth": "Required"},
                    {"method": "GET", "path": "/api/v1/auth/check-permissions", "description": "Check user permissions", "auth": "Required"},
                    {"method": "GET", "path": "/api/v1/auth/session-info", "description": "Get session information", "auth": "Required"}
                ]
            },
            
            "usuarios": {
                "base": "/api/v1/usuarios",
                "description": "User management (CRUD operations)",
                "total_endpoints": 22,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/usuarios", "description": "List all users", "auth": "Superadmin"},
                    {"method": "POST", "path": "/api/v1/usuarios", "description": "Create new user", "auth": "Superadmin"},
                    {"method": "GET", "path": "/api/v1/usuarios/{id}", "description": "Get user by ID", "auth": "Required"},
                    {"method": "PUT", "path": "/api/v1/usuarios/{id}", "description": "Update user", "auth": "Superadmin"},
                    {"method": "DELETE", "path": "/api/v1/usuarios/{id}", "description": "Delete user", "auth": "Superadmin"}
                ]
            },
            
            "roles": {
                "base": "/api/v1/roles",
                "description": "Role management",
                "total_endpoints": 10,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/roles", "description": "List all roles", "auth": "Required"},
                    {"method": "POST", "path": "/api/v1/roles", "description": "Create role", "auth": "Superadmin"},
                    {"method": "GET", "path": "/api/v1/roles/{id}", "description": "Get role by ID", "auth": "Required"},
                    {"method": "DELETE", "path": "/api/v1/roles/{id}", "description": "Delete role", "auth": "Superadmin"}
                ]
            },
            
            "facultades": {
                "base": "/api/v1/facultades",
                "description": "Faculty management",
                "total_endpoints": 11,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/facultades", "description": "List all faculties", "auth": "Public"},
                    {"method": "POST", "path": "/api/v1/facultades", "description": "Create faculty", "auth": "Superadmin"},
                    {"method": "GET", "path": "/api/v1/facultades/{id}", "description": "Get faculty by ID", "auth": "Public"},
                    {"method": "PUT", "path": "/api/v1/facultades/{id}", "description": "Update faculty", "auth": "Superadmin"}
                ]
            },
            
            "programas_academicos": {
                "base": "/api/v1/programas-academicos",
                "description": "Academic program management",
                "total_endpoints": 14,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/programas-academicos", "description": "List all programs", "auth": "Public"},
                    {"method": "POST", "path": "/api/v1/programas-academicos", "description": "Create program", "auth": "Superadmin"},
                    {"method": "GET", "path": "/api/v1/programas-academicos/{id}", "description": "Get program by ID", "auth": "Public"},
                    {"method": "DELETE", "path": "/api/v1/programas-academicos/{id}", "description": "Delete program", "auth": "Superadmin"}
                ]
            },
            
            "cursos": {
                "base": "/api/v1/cursos",
                "description": "Course catalog management",
                "total_endpoints": 11,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/cursos", "description": "List all courses", "auth": "Public"},
                    {"method": "POST", "path": "/api/v1/cursos", "description": "Create course", "auth": "Superadmin"},
                    {"method": "GET", "path": "/api/v1/cursos/{id}", "description": "Get course by ID", "auth": "Public"},
                    {"method": "PUT", "path": "/api/v1/cursos/{id}", "description": "Update course", "auth": "Superadmin"}
                ]
            },
            
            "profesores": {
                "base": "/api/v1/profesores",
                "description": "Professor profile management",
                "total_endpoints": 14,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/profesores", "description": "List all professors", "auth": "Required"},
                    {"method": "POST", "path": "/api/v1/profesores", "description": "Create professor profile", "auth": "Superadmin"},
                    {"method": "GET", "path": "/api/v1/profesores/{id}", "description": "Get professor by ID", "auth": "Required"},
                    {"method": "DELETE", "path": "/api/v1/profesores/{id}", "description": "Delete professor", "auth": "Superadmin"}
                ]
            },
            
            "estudiantes": {
                "base": "/api/v1/estudiantes",
                "description": "Student profile management",
                "total_endpoints": 15,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/estudiantes", "description": "List all students", "auth": "Required"},
                    {"method": "POST", "path": "/api/v1/estudiantes", "description": "Create student profile", "auth": "Superadmin"},
                    {"method": "GET", "path": "/api/v1/estudiantes/{id}", "description": "Get student by ID", "auth": "Required"},
                    {"method": "DELETE", "path": "/api/v1/estudiantes/{id}", "description": "Delete student", "auth": "Superadmin"}
                ]
            },
            
            "grupos": {
                "base": "/api/v1/grupos",
                "description": "Course group (section) management",
                "total_endpoints": 13,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/grupos", "description": "List all groups", "auth": "Public"},
                    {"method": "POST", "path": "/api/v1/grupos", "description": "Create group", "auth": "Superadmin/Profesor"},
                    {"method": "GET", "path": "/api/v1/grupos/{id}", "description": "Get group by ID", "auth": "Public"},
                    {"method": "PUT", "path": "/api/v1/grupos/{id}", "description": "Update group", "auth": "Superadmin/Profesor"}
                ]
            },
            
            "horarios": {
                "base": "/api/v1/horarios",
                "description": "Class schedule management",
                "total_endpoints": 13,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/horarios/grupo/{grupo_id}", "description": "Get group schedules", "auth": "Public"},
                    {"method": "POST", "path": "/api/v1/horarios", "description": "Create schedule", "auth": "Superadmin/Profesor"},
                    {"method": "PUT", "path": "/api/v1/horarios/{id}", "description": "Update schedule", "auth": "Superadmin/Profesor"},
                    {"method": "DELETE", "path": "/api/v1/horarios/{id}", "description": "Delete schedule", "auth": "Superadmin"}
                ]
            },
            
            "inscripciones": {
                "base": "/api/v1/inscripciones",
                "description": "Student enrollment management",
                "total_endpoints": 17,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/inscripciones", "description": "List all enrollments", "auth": "Required"},
                    {"method": "POST", "path": "/api/v1/inscripciones", "description": "Enroll student", "auth": "Required"},
                    {"method": "GET", "path": "/api/v1/inscripciones/{id}", "description": "Get enrollment by ID", "auth": "Required"},
                    {"method": "PATCH", "path": "/api/v1/inscripciones/{id}/retirar", "description": "Withdraw student", "auth": "Required"}
                ]
            },
            
            "actividades_evaluativas": {
                "base": "/api/v1/actividades-evaluativas",
                "description": "Academic activity management (assignments, exams, quizzes)",
                "total_endpoints": 9,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/actividades-evaluativas", "description": "List all activities", "auth": "Public"},
                    {"method": "POST", "path": "/api/v1/actividades-evaluativas", "description": "Create activity", "auth": "Superadmin/Profesor"},
                    {"method": "PUT", "path": "/api/v1/actividades-evaluativas/{id}", "description": "Update activity", "auth": "Superadmin/Profesor"},
                    {"method": "DELETE", "path": "/api/v1/actividades-evaluativas/{id}", "description": "Delete activity", "auth": "Superadmin"}
                ]
            },
            
            "entregas": {
                "base": "/api/v1/entregas",
                "description": "Assignment submission management",
                "total_endpoints": 10,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/entregas/actividad/{actividad_id}", "description": "Get activity submissions", "auth": "Required"},
                    {"method": "POST", "path": "/api/v1/entregas", "description": "Submit assignment", "auth": "Required"},
                    {"method": "PUT", "path": "/api/v1/entregas/{id}", "description": "Update submission", "auth": "Required"},
                    {"method": "DELETE", "path": "/api/v1/entregas/{id}", "description": "Delete submission", "auth": "Required"}
                ]
            },
            
            "calificaciones": {
                "base": "/api/v1/calificaciones",
                "description": "Grade management",
                "total_endpoints": 11,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/calificaciones", "description": "List all grades", "auth": "Required"},
                    {"method": "POST", "path": "/api/v1/calificaciones", "description": "Grade submission", "auth": "Superadmin/Profesor"},
                    {"method": "POST", "path": "/api/v1/calificaciones/bulk", "description": "Grade multiple submissions", "auth": "Superadmin/Profesor"},
                    {"method": "PUT", "path": "/api/v1/calificaciones/{id}", "description": "Update grade", "auth": "Superadmin/Profesor"}
                ]
            },
            
            "asistencias": {
                "base": "/api/v1/asistencias",
                "description": "Attendance tracking",
                "total_endpoints": 12,
                "main_endpoints": [
                    {"method": "GET", "path": "/api/v1/asistencias/grupo/{grupo_id}", "description": "Get group attendance", "auth": "Required"},
                    {"method": "POST", "path": "/api/v1/asistencias", "description": "Record attendance", "auth": "Superadmin/Profesor"},
                    {"method": "POST", "path": "/api/v1/asistencias/bulk", "description": "Record bulk attendance", "auth": "Superadmin/Profesor"},
                    {"method": "PATCH", "path": "/api/v1/asistencias/{id}", "description": "Update attendance", "auth": "Superadmin/Profesor"}
                ]
            }
        },
        
        "statistics": {
            "total_endpoints": 179,
            "public_endpoints": "~30 (documentation, course catalogs, faculties)",
            "protected_endpoints": "~149 (require authentication)",
            "categories": 15
        },
        
        "support": {
            "need_help": "Visit /docs for interactive API documentation",
            "authentication_guide": "See 'authentication' section above",
            "health_check": "GET /health"
        }
    })


api_router.include_router(auth.router)


api_router.include_router(usuarios.router)

api_router.include_router(roles.router)


api_router.include_router(
    facultades.router,
    prefix="/facultades",
    tags=["Facultades"]
)

api_router.include_router(programas_academicos.router)

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
