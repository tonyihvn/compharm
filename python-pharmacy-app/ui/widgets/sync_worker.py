"""Sync worker for background synchronization."""

import logging
import time
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from config.settings import settings

logger = logging.getLogger(__name__)


class SyncWorker(QThread):
    """Worker thread for synchronizing data with central server."""
    
    sync_started = pyqtSignal()
    sync_progress = pyqtSignal(str)  # Progress message
    sync_completed = pyqtSignal(dict)  # Results dictionary
    sync_error = pyqtSignal(str)  # Error message
    
    def __init__(self, api_client, db_manager, sync_interval=300):
        """Initialize sync worker.
        
        Args:
            api_client: CentralServerClient instance
            db_manager: DatabaseManager instance
            sync_interval: Sync interval in seconds (default: 300 = 5 minutes)
        """
        super().__init__()
        self.api_client = api_client
        self.db_manager = db_manager
        self.sync_interval = sync_interval
        self.running = False
        self.manual_sync_requested = False
        self.is_syncing = False
        self.last_sync_time = None
        self.last_sync_result = None
    
    def run(self):
        """Run the sync worker in background loop."""
        self.running = True
        next_sync = 0
        
        while self.running:
            current_time = time.time()
            
            # Check if manual sync requested or if interval elapsed
            if self.manual_sync_requested or (current_time >= next_sync and self.running):
                self.manual_sync_requested = False
                try:
                    self.is_syncing = True
                    self.sync_started.emit()
                    logger.info("Sync started")
                    
                    # Perform sync operations
                    sync_result = self.perform_sync()
                    
                    self.is_syncing = False
                    self.last_sync_time = datetime.now()
                    self.last_sync_result = sync_result
                    
                    self.sync_completed.emit(sync_result)
                    logger.info(f"Sync completed successfully: {sync_result}")
                    
                    # Schedule next auto sync
                    next_sync = current_time + self.sync_interval
                    
                except Exception as e:
                    self.is_syncing = False
                    error_msg = f"Sync error: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    self.sync_error.emit(error_msg)
                    
                    # Retry after shorter interval on error
                    next_sync = current_time + min(60, self.sync_interval)
            
            # Sleep in small intervals to allow responsiveness
            time.sleep(1)
    
    def perform_sync(self) -> dict:
        """Perform actual sync operations.
        
        Returns:
            Dictionary with sync results
        """
        results = {
            'clients_synced': 0,
            'forms_synced': 0,
            'submissions_sent': 0,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }
        
        try:
            # Sync clients from central server
            self.sync_progress.emit("Fetching clients from server...")
            logger.info("Fetching clients from central server")
            
            clients = self.api_client.get_clients()
            if clients:
                self.sync_progress.emit(f"Saving {len(clients)} clients to database...")
                logger.info(f"Received {len(clients)} clients from server")
                
                for i, client in enumerate(clients):
                    try:
                        self.db_manager.add_or_update_client(client)
                        if (i + 1) % 10 == 0:
                            self.sync_progress.emit(f"Saved {i + 1}/{len(clients)} clients")
                    except Exception as e:
                        logger.warning(f"Failed to sync client {client.get('id', 'unknown')}: {str(e)}")
                
                results['clients_synced'] = len(clients)
                logger.info(f"Successfully synced {len(clients)} clients")
            
            # Sync forms from central server
            self.sync_progress.emit("Fetching forms from server...")
            logger.info("Fetching forms from central server")
            
            forms_response = self.api_client.get_forms()
            forms = forms_response.get('data', []) if forms_response and isinstance(forms_response, dict) else []
            
            if forms:
                self.sync_progress.emit(f"Downloading and saving {len(forms)} forms...")
                logger.info(f"Received {len(forms)} forms from server")
                
                for i, form in enumerate(forms):
                    try:
                        form_id = form.get('id') or form.get('form_uuid')
                        form_name = form.get('form_name') or form.get('name', 'Unknown')
                        
                        # Get full form data (definition/form_data)
                        full_form_data = form.get('form_data') or form.get('definition') or form
                        
                        # Store form in local database
                        success = self.db_manager.store_form(
                            form_id=form_id,
                            form_name=form_name,
                            form_definition=full_form_data,
                            version=form.get('version', '1.0'),
                            description=form.get('description', '')
                        )
                        
                        if success:
                            logger.debug(f"Stored form {form_id} in local database")
                        else:
                            logger.warning(f"Failed to store form {form_id}")
                        
                        if (i + 1) % 5 == 0:
                            self.sync_progress.emit(f"Downloaded {i + 1}/{len(forms)} forms")
                    
                    except Exception as e:
                        logger.warning(f"Failed to sync form {form.get('id', 'unknown')}: {str(e)}")
                
                results['forms_synced'] = len(forms)
                logger.info(f"Successfully synced {len(forms)} forms")
            
            # Push pending submissions to central server
            self.sync_progress.emit("Checking for pending submissions...")
            logger.info("Fetching pending submissions")
            
            submissions = self.db_manager.get_pending_submissions()
            if submissions:
                self.sync_progress.emit(f"Sending {len(submissions)} submissions to server...")
                logger.info(f"Found {len(submissions)} pending submissions")
                
                for i, submission in enumerate(submissions):
                    try:
                        self.api_client.submit_form(submission)
                        self.db_manager.mark_submission_synced(submission['id'])
                        if (i + 1) % 5 == 0:
                            self.sync_progress.emit(f"Sent {i + 1}/{len(submissions)} submissions")
                    except Exception as e:
                        logger.warning(f"Failed to submit form {submission.get('id', 'unknown')}: {str(e)}")
                
                results['submissions_sent'] = len(submissions)
                logger.info(f"Successfully sent {len(submissions)} submissions")
            
            self.sync_progress.emit("Sync completed successfully")
            
        except Exception as e:
            logger.error(f"Error during sync: {str(e)}", exc_info=True)
            results['status'] = 'error'
            results['error'] = str(e)
            raise
        
        return results
    
    def trigger_sync(self):
        """Trigger an immediate manual sync."""
        logger.info("Manual sync triggered")
        self.manual_sync_requested = True
    
    def update_sync_interval(self, interval_minutes: int):
        """Update the sync interval.
        
        Args:
            interval_minutes: New sync interval in minutes
        """
        self.sync_interval = max(1, interval_minutes) * 60  # Convert to seconds
        logger.info(f"Sync interval updated to {interval_minutes} minutes")
    
    def get_sync_status(self) -> dict:
        """Get current sync status."""
        return {
            'is_syncing': self.is_syncing,
            'last_sync_time': self.last_sync_time,
            'last_sync_result': self.last_sync_result
        }
    
    def stop(self):
        """Stop the sync worker."""
        logger.info("Stopping sync worker")
        self.running = False
        self.wait()
