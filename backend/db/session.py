"""
Configuración de la sesión de base de datos SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
import logging

from backend.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  
    poolclass=NullPool,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Generador de dependencia para FastAPI.
    
    Proporciona una sesión de base de datos que se cierra automáticamente
    después de cada request.
    
    Uso en FastAPI:
    ```python
    @app.get("/items")
    def read_items(db: Session = Depends(get_db)):
        items = db.query(Item).all()
        return items
    ```
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error en la sesión de base de datos: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos.
    
    Esta función puede ser usada para:
    - Crear tablas (en desarrollo)
    - Ejecutar migraciones
    - Cargar datos iniciales
    """
    from backend.db.base import Base
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        raise


__all__ = ["engine", "SessionLocal", "get_db", "init_db"]
