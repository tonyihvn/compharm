# Sync Functionality Implementation Guide

## Overview

The pharmacy app now includes comprehensive synchronization functionality that allows:
- **Manual Sync**: Users can trigger immediate synchronization via the "Sync Now" button
- **Auto-Sync**: Background synchronization runs automatically at configured intervals
- **Sync Status Indicator**: Real-time display of sync status in the sidebar
- **Progress Tracking**: Visual feedback during sync operations
- **Error Handling**: Graceful error handling with detailed logging

## Features Implemented

### 1. Enhanced SyncWorker (`ui/widgets/sync_worker.py`)

**Key Features:**
- Background thread-based synchronization
- Manual sync triggering with `trigger_sync()` method
- Configurable auto-sync intervals
- Real-time progress reporting via signals
- Graceful error handling and recovery
- Detailed logging of all sync operations

**Signals:**
- `sync_started`: Emitted when sync begins
- `sync_progress`: Emitted with progress messages (e.g., "Fetching clients...")
- `sync_completed`: Emitted when sync completes successfully
- `sync_error`: Emitted when sync fails

**Methods:**
- `perform_sync()`: Executes the actual sync operations
- `trigger_sync()`: Requests an immediate manual sync
- `update_sync_interval(interval_minutes)`: Changes auto-sync interval
- `get_sync_status()`: Returns current sync status
- `stop()`: Gracefully stops the sync worker

### 2. Sync Status Indicator Widget (`ui/widgets/sync_status_widget.py`)

**SyncStatusIndicator:**
- Displays current sync status in the sidebar
- Shows last sync time and client count
- Color-coded status indicators:
  - Gray dot: Idle
  - Orange dot: Syncing in progress
  - Green checkmark: Sync successful
  - Red X: Sync failed

**SyncProgressDialog:**
- Modal dialog showing sync progress
- Real-time progress messages
- Displays sync results (clients, forms, submissions)
- Error messages on failure
- Indeterminate progress bar during sync

### 3. Database Sync Methods (`database/db_manager.py`)

Added methods:
- `add_or_update_client(client_data)`: Saves/updates clients locally
- `add_or_update_form(form_data)`: Saves/updates forms locally
- `get_pending_submissions()`: Retrieves unsynced form submissions
- `mark_submission_synced(submission_id)`: Marks submissions as synced

### 4. Updated Main Window (`ui/modern_main_window.py`)

**Changes:**
- Added sync status indicator to sidebar
- Integrated "Sync Now" button for manual sync
- Connected sync signals to UI handlers
- Auto-initialization of sync worker after login
- Proper cleanup on logout

**Sync Handler Methods:**
- `setup_sync_worker()`: Initializes sync background thread
- `sync_data()`: Manual sync trigger with progress dialog
- `on_sync_started()`: Handles sync start
- `on_sync_completed()`: Handles successful sync
- `on_sync_error()`: Handles sync errors

### 5. System Settings (`ui/system_settings.py`)

**Existing Sync Settings:**
- Auto-sync interval (minutes): Default 5 minutes
- Batch size for sync: Default 100 items
- Configurable via System Settings dialog

**Settings saved to `.env` file:**
```
SYNC_INTERVAL=5          # minutes
SYNC_BATCH_SIZE=100      # items per sync
AUTO_SYNC_ENABLED=True   # enable/disable auto-sync
```

## Usage

### Manual Sync

Users can trigger an immediate sync by:
1. Clicking the "⚡ Sync Now" button in the sidebar
2. A progress dialog appears showing:
   - Real-time progress messages
   - Number of clients/forms processed
   - Sync results upon completion
   - Any error messages if sync fails

### Auto-Sync Configuration

To configure auto-sync:
1. Open Admin Panel → System Settings
2. Set "Auto Sync Interval (minutes)" to desired value (1-1440 minutes)
3. Click "Save Settings"
4. Changes take effect after app restart

### Monitoring Sync Status

The sync status indicator in the sidebar shows:
- **Idle** (gray): No sync in progress
- **Syncing...** (orange): Sync operation running
- **Synced Successfully** (green): Last sync completed successfully
- **Sync Failed** (red): Last sync encountered an error

The indicator also displays:
- Last sync time
- Number of clients synced
- Error message if sync failed

## Data Synced

During each sync cycle, the following data is synchronized:

### Download (Pull from Server)
1. **Clients**: Fetches all clients assigned to this pharmacy
2. **Forms**: Fetches all available forms from the server
3. Saved to local SQLite database

### Upload (Push to Server)
1. **Form Submissions**: Sends any pending form submissions
2. Marks submissions as synced in local database

## Technical Architecture

### Thread Safety
- Sync worker runs in a separate thread to keep UI responsive
- All database operations are session-based
- Signal/slot communication for thread-safe UI updates

### Error Handling
- Connection errors: Retries after shorter interval
- Invalid data: Logs warning and continues
- Partial failures: Processes remaining items
- Database errors: Logged and reported to user

### Logging
All sync operations are logged to `logs/pharmacy_app.log`:
- Sync start/completion times
- Number of items synced
- Error details and stack traces
- Performance metrics

## Configuration

### Environment Variables
```bash
# Sync settings (in .env file)
SYNC_INTERVAL=5              # minutes between auto-syncs
SYNC_BATCH_SIZE=100          # items per sync operation
AUTO_SYNC_ENABLED=True       # enable/disable auto-sync
CENTRAL_SERVER_URL=http://localhost:3001  # backend server
```

### Runtime Configuration
Modify sync interval at runtime:
```python
sync_worker.update_sync_interval(10)  # 10 minutes
```

## API Endpoints Used

The sync worker communicates with the backend server using:
- `GET /api/clients`: Fetch all clients (params: pharmacy_id, skip, limit)
- `GET /api/forms`: Fetch all available forms
- `POST /api/forms/submit`: Submit form responses
- `GET /api/clients/{id}`: Fetch single client details (if needed)

## Error Recovery

The sync system includes smart error recovery:
1. **Connection Errors**: Retries after 60 seconds
2. **Server Errors (5xx)**: Automatic retry with backoff
3. **Invalid Data**: Logs warning and continues with next item
4. **Partial Failures**: Completes as much as possible, reports status

## Performance Considerations

- Auto-sync interval: Minimum 1 minute, maximum 24 hours
- Batch size: Configurable (default 100 items)
- Progress updates every 10 clients
- Database transactions are atomic
- No blocking of UI during sync

## Troubleshooting

### Sync Not Starting
1. Check if backend server is running
2. Verify CENTRAL_SERVER_URL setting
3. Check logs in `logs/pharmacy_app.log`
4. Restart application

### Sync Showing Errors
1. Check network connectivity
2. Verify backend credentials in System Settings
3. Ensure backend server is accessible
4. Check server logs for issues

### Sync Too Slow
1. Reduce SYNC_BATCH_SIZE in settings
2. Increase SYNC_INTERVAL if not critical
3. Check server performance
4. Verify network bandwidth

## Testing

Run the test suite to verify sync functionality:
```bash
python test_sync_implementation.py
```

Expected output:
```
✓ Settings Configuration tests PASSED
✓ Database Sync Methods tests PASSED
✓ SyncWorker tests PASSED
✓ SyncStatusIndicator tests PASSED
✓ SyncProgressDialog tests PASSED
Total: 5/5 tests passed
```

## Future Enhancements

Potential improvements:
- Selective sync (sync only specific data types)
- Sync scheduling (specify days/times)
- Bandwidth throttling
- Offline mode with periodic sync
- Sync history/audit trail
- Conflict resolution for duplicates
- Incremental sync (only changed data)

## Files Modified/Created

### New Files:
- `ui/widgets/sync_status_widget.py`: Sync indicators and progress dialog
- `test_sync_implementation.py`: Test suite for sync functionality

### Modified Files:
- `ui/widgets/sync_worker.py`: Enhanced with manual sync, progress, and better error handling
- `ui/modern_main_window.py`: Integrated sync UI, buttons, and status indicator
- `database/db_manager.py`: Added sync-related database methods
- `ui/system_settings.py`: Already had sync interval configuration

## Support

For issues or questions about the sync functionality:
1. Check logs in `logs/pharmacy_app.log`
2. Verify backend server connectivity
3. Review System Settings configuration
4. Run test suite: `python test_sync_implementation.py`
5. Contact system administrator

