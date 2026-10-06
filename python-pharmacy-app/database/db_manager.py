"""Database manager for SQLite operations."""

import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .models import Base
from config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self, database_url: str = None):
        """Initialize database manager."""
        self.database_url = database_url or settings.DATABASE_URL
        
        # SQLite configuration
        connect_args = {"check_same_thread": False} if "sqlite" in self.database_url else {}
        poolclass = StaticPool if "sqlite" in self.database_url else None
        
        self.engine = create_engine(
            self.database_url,
            connect_args=connect_args,
            poolclass=poolclass,
            echo=settings.DEBUG
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Database initialized: {self.database_url}")

    def init_db(self):
        """Create all tables in the database."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def close(self):
        """Close database connection."""
        self.engine.dispose()
        logger.info("Database connection closed")

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()

    def reset_db(self):
        """Drop all tables and recreate them (for testing)."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.warning("All database tables dropped")
            self.init_db()
            logger.info("Database reset completed")
        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            raise


# Global database manager instance
db_manager = DatabaseManager()
