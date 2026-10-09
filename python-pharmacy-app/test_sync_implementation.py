#!/usr/bin/env python3
"""
Test script to verify sync functionality implementation
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_sync_worker():
    """Test SyncWorker implementation"""
    logger.info("=" * 60)
    logger.info("Testing SyncWorker Implementation")
    logger.info("=" * 60)
    
    try:
        from ui.widgets.sync_worker import SyncWorker
        from services.api_client import CentralServerClient
        from database.db_manager import DatabaseManager
        from config.settings import settings
        
        logger.info("✓ Imported SyncWorker successfully")
        
        # Create mock instances
        api_client = CentralServerClient()
        db_manager = DatabaseManager()
        
        # Create sync worker
        sync_worker = SyncWorker(api_client, db_manager, sync_interval=300)
        logger.info("✓ SyncWorker created successfully")
        
        # Check methods exist
        assert hasattr(sync_worker, 'perform_sync'), "Missing perform_sync method"
        assert hasattr(sync_worker, 'trigger_sync'), "Missing trigger_sync method"
        assert hasattr(sync_worker, 'get_sync_status'), "Missing get_sync_status method"
        assert hasattr(sync_worker, 'update_sync_interval'), "Missing update_sync_interval method"
        logger.info("✓ All required methods exist")
        
        # Check signals
        assert hasattr(sync_worker, 'sync_started'), "Missing sync_started signal"
        assert hasattr(sync_worker, 'sync_progress'), "Missing sync_progress signal"
        assert hasattr(sync_worker, 'sync_completed'), "Missing sync_completed signal"
        assert hasattr(sync_worker, 'sync_error'), "Missing sync_error signal"
        logger.info("✓ All required signals exist")
        
        # Test sync status
        status = sync_worker.get_sync_status()
        assert 'is_syncing' in status, "Missing is_syncing in status"
        assert 'last_sync_time' in status, "Missing last_sync_time in status"
        assert 'last_sync_result' in status, "Missing last_sync_result in status"
        logger.info(f"✓ Sync status check: {status}")
        
        # Test update interval
        sync_worker.update_sync_interval(10)
        assert sync_worker.sync_interval == 600, "Sync interval not updated correctly"
        logger.info("✓ Sync interval updated successfully")
        
        logger.info("\n✓ SyncWorker tests PASSED\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ SyncWorker test FAILED: {str(e)}", exc_info=True)
        return False


def test_sync_status_indicator():
    """Test SyncStatusIndicator widget"""
    logger.info("=" * 60)
    logger.info("Testing SyncStatusIndicator Widget")
    logger.info("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.widgets.sync_status_widget import SyncStatusIndicator
        
        app = QApplication.instance() or QApplication([])
        
        # Create indicator
        indicator = SyncStatusIndicator()
        logger.info("✓ SyncStatusIndicator created successfully")
        
        # Test state changes
        indicator.set_idle()
        logger.info("✓ Set idle state")
        
        indicator.set_syncing()
        logger.info("✓ Set syncing state")
        
        result = {
            'last_sync_time': None,
            'last_sync_result': {
                'clients_synced': 10,
                'forms_synced': 5
            }
        }
        indicator.set_success(result)
        logger.info("✓ Set success state")
        
        indicator.set_error("Test error message")
        logger.info("✓ Set error state")
        
        logger.info("\n✓ SyncStatusIndicator tests PASSED\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ SyncStatusIndicator test FAILED: {str(e)}", exc_info=True)
        return False


def test_sync_progress_dialog():
    """Test SyncProgressDialog widget"""
    logger.info("=" * 60)
    logger.info("Testing SyncProgressDialog Widget")
    logger.info("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.widgets.sync_status_widget import SyncProgressDialog
        
        app = QApplication.instance() or QApplication([])
        
        # Create dialog
        dialog = SyncProgressDialog()
        logger.info("✓ SyncProgressDialog created successfully")
        
        # Test progress update
        dialog.update_progress("Fetching clients...")
        logger.info("✓ Progress message updated")
        
        # Test completion
        result = {
            'status': 'success',
            'clients_synced': 15,
            'forms_synced': 8,
            'submissions_sent': 3
        }
        dialog.sync_completed(result)
        logger.info("✓ Sync completion handled")
        
        # Test error
        dialog.sync_error("Test error")
        logger.info("✓ Sync error handled")
        
        logger.info("\n✓ SyncProgressDialog tests PASSED\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ SyncProgressDialog test FAILED: {str(e)}", exc_info=True)
        return False


def test_database_sync_methods():
    """Test database sync methods"""
    logger.info("=" * 60)
    logger.info("Testing Database Sync Methods")
    logger.info("=" * 60)
    
    try:
        from database.db_manager import DatabaseManager
        
        db_manager = DatabaseManager()
        
        # Check methods exist
        assert hasattr(db_manager, 'add_or_update_client'), "Missing add_or_update_client method"
        assert hasattr(db_manager, 'add_or_update_form'), "Missing add_or_update_form method"
        assert hasattr(db_manager, 'get_pending_submissions'), "Missing get_pending_submissions method"
        assert hasattr(db_manager, 'mark_submission_synced'), "Missing mark_submission_synced method"
        logger.info("✓ All required database methods exist")
        
        # Test getting pending submissions
        submissions = db_manager.get_pending_submissions()
        assert isinstance(submissions, list), "get_pending_submissions should return a list"
        logger.info(f"✓ get_pending_submissions works: {len(submissions)} pending submissions")
        
        logger.info("\n✓ Database sync methods tests PASSED\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ Database sync methods test FAILED: {str(e)}", exc_info=True)
        return False


def test_settings_configuration():
    """Test settings configuration"""
    logger.info("=" * 60)
    logger.info("Testing Settings Configuration")
    logger.info("=" * 60)
    
    try:
        from config.settings import settings
        
        # Check sync-related settings
        assert hasattr(settings, 'AUTO_SYNC_ENABLED'), "Missing AUTO_SYNC_ENABLED setting"
        assert hasattr(settings, 'SYNC_INTERVAL'), "Missing SYNC_INTERVAL setting"
        assert hasattr(settings, 'SYNC_BATCH_SIZE'), "Missing SYNC_BATCH_SIZE setting"
        logger.info("✓ All required settings exist")
        
        logger.info(f"  AUTO_SYNC_ENABLED: {settings.AUTO_SYNC_ENABLED}")
        logger.info(f"  SYNC_INTERVAL: {settings.SYNC_INTERVAL} minutes")
        logger.info(f"  SYNC_BATCH_SIZE: {settings.SYNC_BATCH_SIZE}")
        
        logger.info("\n✓ Settings configuration tests PASSED\n")
        return True
        
    except Exception as e:
        logger.error(f"✗ Settings configuration test FAILED: {str(e)}", exc_info=True)
        return False


def main():
    """Run all tests"""
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 10 + "SYNC FUNCTIONALITY TEST SUITE" + " " * 20 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    logger.info("\n")
    
    results = {
        "Settings Configuration": test_settings_configuration(),
        "Database Sync Methods": test_database_sync_methods(),
        "SyncWorker": test_sync_worker(),
        "SyncStatusIndicator": test_sync_status_indicator(),
        "SyncProgressDialog": test_sync_progress_dialog(),
    }
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        logger.info(f"{test_name:<40} {status}")
    
    logger.info("=" * 60)
    logger.info(f"Total: {passed}/{total} tests passed")
    logger.info("=" * 60 + "\n")
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
