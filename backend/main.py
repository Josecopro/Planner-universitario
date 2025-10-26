"""
Main application file - Planner Universitario API

Este es el punto de entrada de la aplicación FastAPI.
Configura la aplicación, middleware, CORS, y monta todos los routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from core import config
from db.session import engine
from db.base import Base
from api.v1.api import api_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    
    Startup: Verifica la conexión a la base de datos
    Shutdown: Cierra conexiones y limpia recursos
    """
    logger.info("La API...")
    
    try:
        with engine.connect() as conn:
            logger.info("Conexión a la base de datos establecida")
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        raise
    
    logger.info(f"API iniciada correctamente en modo: {config.settings.PROJECT_NAME}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando Planner Universitario API...")
    engine.dispose()
    logger.info("Recursos liberados correctamente")


app = FastAPI(
    title=config.settings.PROJECT_NAME,
    version=config.settings.VERSION,
    description="""
    **Planner Universitario API** - Sistema de gestión académica universitaria.
    
    ## Características principales:
    
    * **Autenticación y Autorización** - Sistema JWT con roles (Superadmin, Profesor, Estudiante)
    * **Gestión Académica** - Facultades, Programas, Cursos, Grupos
    * **Gestión de Personas** - Profesores, Estudiantes, Usuarios
    * **Evaluación** - Actividades, Entregas, Calificaciones
    * **Asistencia** - Registro y seguimiento de asistencia
    * **Inscripciones** - Matrícula y gestión de inscripciones
    * **Horarios** - Programación de horarios de clases
    
    ## Seguridad:
    
    * Autenticación mediante JWT (JSON Web Tokens)
    * Control de acceso basado en roles (RBAC)
    * Rate limiting en endpoints de autenticación
    * Bloqueo de cuentas tras intentos fallidos
    * Validación exhaustiva de datos
    
    ## Estructura de URLs:
    
    Todos los endpoints están bajo el prefijo `/api/v1/`
    """,
    openapi_tags=[
        {"name": "Autenticación", "description": "Endpoints de login, logout y gestión de tokens"},
        {"name": "Usuarios", "description": "Gestión de usuarios del sistema"},
        {"name": "Roles", "description": "Gestión de roles y permisos"},
        {"name": "Facultades", "description": "Gestión de facultades"},
        {"name": "Programas Académicos", "description": "Gestión de programas académicos"},
        {"name": "Cursos", "description": "Catálogo de cursos"},
        {"name": "Profesores", "description": "Gestión de perfiles de profesores"},
        {"name": "Estudiantes", "description": "Gestión de perfiles de estudiantes"},
        {"name": "Grupos", "description": "Gestión de grupos (secciones) de cursos"},
        {"name": "Horarios", "description": "Programación de horarios de clases"},
        {"name": "Inscripciones", "description": "Matrícula y gestión de inscripciones"},
        {"name": "Actividades Evaluativas", "description": "Tareas, exámenes, quizzes, etc."},
        {"name": "Entregas", "description": "Entregas de actividades por estudiantes"},
        {"name": "Calificaciones", "description": "Calificaciones de entregas"},
        {"name": "Asistencias", "description": "Registro de asistencia a clases"},
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # (React/Vite)
        "http://localhost:5173",      # Vite dev server
        "http://localhost:8000",      # Backend local
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


app.include_router(
    api_router,
    prefix=config.settings.API_V1_STR
)


@app.get(
    "/",
    tags=["Root"],
    summary="Endpoint raíz",
    response_description="Información básica de la API"
)
async def root():
    """
    Endpoint raíz que proporciona información básica de la API.
    
    Returns:
        dict: Información de la API incluyendo nombre, versión y enlaces útiles
    """
    return {
        "message": "Bienvenido a Planner Universitario API",
        "version": config.settings.VERSION,
        "project": config.settings.PROJECT_NAME,
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": config.settings.API_V1_STR,
        "status": "online"
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    response_description="Estado de salud de la API"
)
async def health_check():
    """
    Endpoint de health check para monitoreo.
    
    Verifica que la API esté respondiendo correctamente.
    Útil para:
    - Monitoreo de servicios
    - Load balancers
    - Orquestadores (Kubernetes, Docker Swarm)
    
    Returns:
        dict: Estado de salud de la API y sus componentes
    """
    try:
        # Verificar conexión a la base de datos
        with engine.connect() as conn:
            db_status = "healthy"
    except Exception as e:
        logger.error(f"Health check failed - Database error: {e}")
        db_status = "unhealthy"
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": db_status,
                "error": str(e)
            }
        )
    
    return {
        "status": "healthy",
        "database": db_status,
        "version": config.settings.VERSION,
        "api_v1": config.settings.API_V1_STR
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Manejador personalizado para errores 404"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Recurso no encontrado",
            "path": str(request.url),
            "method": request.method
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Manejador personalizado para errores 500"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "message": "Ha ocurrido un error inesperado. Por favor, contacte al administrador."
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
