"""Database manager for SQLite operations."""

import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from .models import Base, Client
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

    def ensure_client_schema(self):
        """Add missing client columns for older databases."""
        try:
            inspector = inspect(self.engine)
            if not inspector.has_table('clients'):
                return

            existing_columns = {col['name'] for col in inspector.get_columns('clients')}
            required_columns = {
                'address', 'weight', 'height', 'bmi', 'last_visit_date',
                'hiv_status', 'art_status', 'current_cd4', 'current_viral_load'
            }

            for column_name in sorted(required_columns - existing_columns):
                column = Client.__table__.columns[column_name]
                column_type = column.type.compile(dialect=self.engine.dialect)
                sql = f'ALTER TABLE clients ADD COLUMN {column_name} {column_type};'
                with self.engine.begin() as conn:
                    conn.execute(text(sql))
                logger.info(f"Added missing column to clients table: {column_name}")
        except Exception as e:
            logger.warning(f"Unable to migrate clients table schema: {e}")

    def init_db(self):
        """Create all tables in the database."""
        try:
            Base.metadata.create_all(bind=self.engine)
            self.ensure_client_schema()
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
