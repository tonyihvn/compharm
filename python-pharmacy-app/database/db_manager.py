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

    # Sync-related methods
    def add_or_update_client(self, client_data: dict) -> Client:
        """Add or update a client in the database.
        
        Args:
            client_data: Dictionary containing client information
            
        Returns:
            The created or updated Client object
        """
        session = self.get_session()
        try:
            client_id = client_data.get('id')
            
            # Find existing client
            existing = session.query(Client).filter_by(id=client_id).first()
            
            if existing:
                # Update existing client
                for key, value in client_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                logger.debug(f"Updated client {client_id}")
            else:
                # Create new client
                existing = Client(**client_data)
                session.add(existing)
                logger.debug(f"Created new client {client_id}")
            
            session.commit()
            return existing
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding/updating client: {str(e)}")
            raise
        finally:
            session.close()

    def get_all_clients(self) -> list:
        """Get all clients from local database.
        
        Returns:
            List of client dictionaries
        """
        session = self.get_session()
        try:
            clients = session.query(Client).all()
            
            result = []
            for client in clients:
                result.append({
                    'id': client.id,
                    'pepfar_id': client.pepfar_id,
                    'fullName': client.full_name,
                    'full_name': client.full_name,
                    'dateOfBirth': client.date_of_birth,
                    'gender': client.gender,
                    'phone': client.phone_number,
                    'email': client.email,
                    'national_id': client.national_id,
                    'address': client.address,
                    'facility_id': client.facility_id,
                    'pharmacy_id': client.pharmacy_id,
                })
            
            logger.info(f"Loaded {len(result)} clients from database")
            return result
        except Exception as e:
            logger.error(f"Error loading clients: {str(e)}")
            return []
        finally:
            session.close()

    def add_or_update_form(self, form_data: dict):
        """Add or update a form in the database.
        
        Args:
            form_data: Dictionary containing form information
        """
        session = self.get_session()
        try:
            # Import here to avoid circular imports
            from .models import Form
            
            form_id = form_data.get('id')
            
            # Find existing form
            existing = session.query(Form).filter_by(id=form_id).first()
            
            if existing:
                # Update existing form
                for key, value in form_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                logger.debug(f"Updated form {form_id}")
            else:
                # Create new form
                existing = Form(**form_data)
                session.add(existing)
                logger.debug(f"Created new form {form_id}")
            
            session.commit()
            return existing
        except Exception as e:
            session.rollback()
            logger.warning(f"Error adding/updating form: {str(e)}")
            # Don't raise to allow sync to continue with other items
            return None
        finally:
            session.close()

    def get_pending_submissions(self) -> list:
        """Get all pending form submissions.
        
        Returns:
            List of pending submissions
        """
        session = self.get_session()
        try:
            # Import here to avoid circular imports
            from .models import FormSubmission
            
            pending = session.query(FormSubmission).filter_by(
                is_synced_to_server=False
            ).all()
            
            # Convert to dictionaries
            result = []
            for submission in pending:
                result.append({
                    'id': submission.id,
                    'form_id': submission.form_id,
                    'client_id': submission.client_id,
                    'data': submission.data,
                    'created_at': submission.created_at
                })
            
            logger.debug(f"Found {len(result)} pending submissions")
            return result
        except Exception as e:
            logger.warning(f"Error getting pending submissions: {str(e)}")
            return []
        finally:
            session.close()

    def mark_submission_synced(self, submission_id: int) -> bool:
        """Mark a submission as synced.
        
        Args:
            submission_id: ID of the submission to mark as synced
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        try:
            # Import here to avoid circular imports
            from .models import FormSubmission
            from datetime import datetime
            
            submission = session.query(FormSubmission).filter_by(
                id=submission_id
            ).first()
            
            if submission:
                submission.is_synced_to_server = True
                submission.synced_at = datetime.utcnow()
                submission.status = 'synced'
                session.commit()
                logger.debug(f"Marked submission {submission_id} as synced")
                return True
            else:
                logger.warning(f"Submission {submission_id} not found")
                return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error marking submission as synced: {str(e)}")
            return False
        finally:
            session.close()

    def store_form(self, form_id: str, form_name: str, form_definition: dict, version: str = '1.0', description: str = '') -> bool:
        """Store a downloaded form in the local database.
        
        Args:
            form_id: Unique form identifier
            form_name: Display name of the form
            form_definition: OpenMRS JSON form definition
            version: Form version
            description: Form description
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        try:
            from .models import Form
            from datetime import datetime
            
            # Check if form already exists
            existing = session.query(Form).filter_by(uuid=str(form_id)).first()
            
            if existing:
                # Update existing form
                existing.definition = form_definition
                existing.version = version
                existing.description = description
                existing.updated_at = datetime.utcnow()
                logger.debug(f"Updated form {form_id} in database")
            else:
                # Create new form
                form = Form(
                    name=form_name,
                    uuid=str(form_id),
                    version=version,
                    definition=form_definition,
                    description=description,
                    is_published=True,
                    uploaded_at=datetime.utcnow()
                )
                session.add(form)
                logger.debug(f"Stored new form {form_id} in database")
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing form: {str(e)}")
            return False
        finally:
            session.close()

    def save_form(self, form_data: dict) -> bool:
        """Save a form from API response to the local database.
        
        Handles React backend API response format with fields like:
        - id or form_id: Form identifier
        - form_name or name: Display name
        - form_data: Form definition (JSON)
        - version: Form version
        - description: Form description
        
        Args:
            form_data: Form dictionary from API response
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract fields with fallbacks for different API formats
            form_id = form_data.get('id') or form_data.get('form_id') or form_data.get('uuid')
            form_name = form_data.get('form_name') or form_data.get('name', 'Unnamed Form')
            form_definition = form_data.get('form_data') or form_data.get('definition') or {}
            version = str(form_data.get('version', '1.0'))
            description = form_data.get('description', '')
            
            if not form_id:
                logger.error(f"Cannot save form without ID: {form_data}")
                return False
            
            return self.store_form(
                form_id=str(form_id),
                form_name=form_name,
                form_definition=form_definition,
                version=version,
                description=description
            )
        except Exception as e:
            logger.error(f"Error saving form from API response: {str(e)}")
            return False


    def get_all_forms(self) -> list:
        """Get all stored forms from local database.
        
        Returns:
            List of form dictionaries
        """
        session = self.get_session()
        try:
            from .models import Form
            
            forms = session.query(Form).filter_by(is_retired=False).all()
            
            result = []
            for form in forms:
                result.append({
                    'id': form.id,
                    'uuid': form.uuid,
                    'name': form.name,
                    'version': form.version,
                    'description': form.description,
                    'definition': form.definition,
                    'is_published': form.is_published,
                    'uploaded_at': form.uploaded_at.isoformat() if form.uploaded_at else None
                })
            
            logger.debug(f"Retrieved {len(result)} forms from database")
            return result
        except Exception as e:
            logger.warning(f"Error getting forms: {str(e)}")
            return []
        finally:
            session.close()

    def get_form_by_uuid(self, form_uuid: str) -> dict:
        """Get a specific form by UUID.
        
        Args:
            form_uuid: Form UUID
            
        Returns:
            Form dictionary or None if not found
        """
        session = self.get_session()
        try:
            from .models import Form
            
            form = session.query(Form).filter_by(uuid=str(form_uuid)).first()
            
            if form:
                return {
                    'id': form.id,
                    'uuid': form.uuid,
                    'name': form.name,
                    'version': form.version,
                    'description': form.description,
                    'definition': form.definition,
                    'is_published': form.is_published,
                    'uploaded_at': form.uploaded_at.isoformat() if form.uploaded_at else None
                }
            else:
                logger.debug(f"Form {form_uuid} not found in database")
                return None
        except Exception as e:
            logger.warning(f"Error getting form: {str(e)}")
            return None
        finally:
            session.close()

    def delete_form(self, form_uuid: str) -> bool:
        """Delete a form from the local database.
        
        Args:
            form_uuid: Form UUID
            
        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        try:
            from .models import Form
            
            form = session.query(Form).filter_by(uuid=str(form_uuid)).first()
            
            if form:
                # Soft delete by marking as retired
                form.is_retired = True
                session.commit()
                logger.debug(f"Deleted form {form_uuid}")
                return True
            else:
                logger.warning(f"Form {form_uuid} not found")
                return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting form: {str(e)}")
            return False
        finally:
            session.close()

    def add_form_submission(self, form_uuid: str, client_id: int, submission_data: dict, user_id: int = None) -> int:
        """Add a form submission to the database.
        
        Args:
            form_uuid: Form UUID
            client_id: Client ID
            submission_data: Filled form data
            user_id: User who filled the form
            
        Returns:
            Submission ID or None if failed
        """
        session = self.get_session()
        try:
            from .models import Form, FormSubmission
            from datetime import datetime
            
            # Get form by UUID
            form = session.query(Form).filter_by(uuid=str(form_uuid)).first()
            if not form:
                logger.warning(f"Form {form_uuid} not found")
                return None
            
            # Create submission
            submission = FormSubmission(
                form_id=form.id,
                client_id=client_id,
                filled_by_user_id=user_id,
                data=submission_data,
                status='draft',
                is_synced_to_server=False
            )
            session.add(submission)
            session.commit()
            
            logger.debug(f"Created form submission {submission.id}")
            return submission.id
        except Exception as e:
            session.rollback()
            logger.error(f"Error adding form submission: {str(e)}")
            return None
        finally:
            session.close()


# Global database manager instance
db_manager = DatabaseManager()
