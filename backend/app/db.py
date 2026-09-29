import logging
from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.exc import OperationalError

from app.config import settings

logger = logging.getLogger("dealdna.db")


class Base(DeclarativeBase):
    pass


def create_resilient_engine():
    target_url = settings.database_url
    try:
        if target_url.startswith("postgresql"):
            # Test quick connection with small timeout
            test_engine = create_engine(
                target_url,
                connect_args={"connect_timeout": 3},
                pool_pre_ping=True
            )
            with test_engine.connect():
                logger.info("Connected successfully to PostgreSQL.")
                return test_engine
    except Exception as exc:
        logger.warning(
            "PostgreSQL unavailable (%s). Falling back to local SQLite database for development.",
            exc
        )
    
    # Fallback SQLite engine
    sqlite_url = "sqlite:///./dealdna.db"
    return create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True
    )


engine = create_resilient_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
