"""Sync worker for background synchronization."""

import logging
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)


class SyncWorker(QThread):
    """Worker thread for synchronizing data with central server."""
    
    sync_started = pyqtSignal()
    sync_completed = pyqtSignal(dict)
    sync_error = pyqtSignal(str)
    
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
    
    def run(self):
        """Run the sync worker."""
        import time
        self.running = True
        
        while self.running:
            try:
                self.sync_started.emit()
                
                # Perform sync operations
                sync_result = self.perform_sync()
                
                self.sync_completed.emit(sync_result)
                logger.info(f"Sync completed successfully: {sync_result}")
                
            except Exception as e:
                error_msg = f"Sync error: {str(e)}"
                logger.error(error_msg)
                self.sync_error.emit(error_msg)
            
            # Wait for next sync interval
            if self.running:
                time.sleep(self.sync_interval)
    
    def perform_sync(self) -> dict:
        """Perform actual sync operations.
        
        Returns:
            Dictionary with sync results
        """
        results = {
            'clients_synced': 0,
            'forms_synced': 0,
            'submissions_sent': 0,
            'timestamp': None
        }
        
        try:
            # Sync clients from central server
            clients = self.api_client.get_clients()
            if clients:
                for client in clients:
                    self.db_manager.add_or_update_client(client)
                results['clients_synced'] = len(clients)
                logger.info(f"Synced {len(clients)} clients")
            
            # Sync forms from central server
            forms = self.api_client.get_forms()
            if forms:
                for form in forms:
                    self.db_manager.add_or_update_form(form)
                results['forms_synced'] = len(forms)
                logger.info(f"Synced {len(forms)} forms")
            
            # Push submissions to central server
            submissions = self.db_manager.get_pending_submissions()
            if submissions:
                for submission in submissions:
                    self.api_client.submit_form(submission)
                    self.db_manager.mark_submission_synced(submission['id'])
                results['submissions_sent'] = len(submissions)
                logger.info(f"Sent {len(submissions)} submissions")
            
            from datetime import datetime
            results['timestamp'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error during sync: {str(e)}")
            raise
        
        return results
    
    def stop(self):
        """Stop the sync worker."""
        self.running = False
        self.wait()
