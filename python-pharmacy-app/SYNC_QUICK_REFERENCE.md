# Sync Feature - Quick Reference Guide

## 🎯 What's New

The pharmacy app now has powerful sync capabilities that keep your local database synchronized with the central server automatically and on-demand.

## 📊 Sync Status Indicator

Located in the sidebar, the sync status indicator shows:

```
● Idle              Gray dot - No sync in progress
● Syncing...        Orange dot - Sync operation running
✓ Synced            Green checkmark - Last sync successful
✗ Sync Failed       Red X - Last sync had errors
```

Shows:
- Current status with visual indicator
- Last sync time (e.g., "Last sync: 14:30:45")
- Statistics (e.g., "Clients: 25, Forms: 8")

## ⚡ Manual Sync ("Sync Now" Button)

### How to Use:
1. Click the **"⚡ Sync Now"** button in the sidebar
2. A progress dialog appears showing:
   - Real-time progress messages
   - What's being synced (clients, forms, submissions)
   - Number of items processed
3. Wait for sync to complete
4. View results:
   - Number of clients synced
   - Number of forms synced
   - Number of submissions sent
   - Any errors that occurred

### When to Use:
- Before closing the app to ensure latest data is synced
- When you've made changes that need immediate sync
- When the auto-sync interval has been increased
- After adding new clients or forms manually

## 🔄 Auto-Sync (Background Sync)

The app automatically synchronizes data in the background at regular intervals.

### Configuration:
1. Click **"⚙️ Admin Panel"** in sidebar
2. Select **"System Settings"**
3. Find the **"Synchronization Settings"** section
4. Set **"Auto Sync Interval (minutes)"**
   - Default: 5 minutes
   - Min: 1 minute
   - Max: 1440 minutes (24 hours)
5. Click **"Save Settings"**
6. Restart the app for changes to take effect

### What Gets Synced Automatically:
- **Downloaded from Server:** Clients, Forms
- **Uploaded to Server:** Pending form submissions
- **Saved Locally:** All downloaded data stored in database

## 📋 Data Synced

### Download (Pull from Backend)
- **Clients**: All clients assigned to your pharmacy
- **Forms**: All available medical/pharmacy forms

### Upload (Push to Backend)
- **Form Submissions**: Any forms filled out locally
- After upload, marked as "synced" in the database

## 🛠️ Troubleshooting

### Sync Not Starting
**Problem:** No sync activity, status shows "Idle"

**Solutions:**
1. Check internet connection
2. Verify backend server URL in System Settings
3. Check that backend server is running
4. Try clicking "Sync Now" manually
5. Restart the application

### Sync Shows Error
**Problem:** Status shows "Sync Failed" with error message

**Solutions:**
1. Check internet connection
2. Verify backend server is accessible
3. Check credentials in System Settings
4. Restart the application
5. Check logs: `logs/pharmacy_app.log`

### Sync Too Slow
**Problem:** Sync operations take too long

**Solutions:**
1. Increase **Auto Sync Interval** in System Settings
   - If not urgent, reduce frequency
2. Reduce **Sync Batch Size** in System Settings
   - Smaller batches = more frequent but shorter syncs
3. Check server performance
4. Check network bandwidth

### Sync Not Completing
**Problem:** Sync gets stuck or never finishes

**Solutions:**
1. Wait at least 5 minutes (default sync interval)
2. Check internet connection stability
3. Try manual "Sync Now" instead
4. Restart application
5. Check logs for specific errors

## 📝 Logs

All sync activity is logged in: `logs/pharmacy_app.log`

Log entries include:
- Sync start/stop times
- Items synced
- Errors encountered
- Processing time

To view logs:
```
Windows: logs\pharmacy_app.log
Linux/Mac: logs/pharmacy_app.log
```

## ⚙️ Settings Reference

### System Settings → Synchronization Settings

| Setting | Default | Range | Impact |
|---------|---------|-------|--------|
| Auto Sync Interval | 5 min | 1-1440 min | How often background sync runs |
| Sync Batch Size | 100 | 10-1000 | Items per sync operation |

### Environment Variables (.env)

```
SYNC_INTERVAL=5              # Auto-sync interval (minutes)
SYNC_BATCH_SIZE=100          # Items per sync batch
AUTO_SYNC_ENABLED=True       # Enable/disable auto-sync
CENTRAL_SERVER_URL=http://...  # Backend server address
```

## 🔒 Security Notes

- Sync credentials come from System Settings
- Backend credentials should never be shared
- Sync data is transmitted over HTTPS (if configured)
- Local database is protected on your device

## 📞 Need Help?

1. **Check Status Indicator**: Look at the sync status in sidebar
2. **Review Logs**: Check `logs/pharmacy_app.log` for details
3. **Manual Sync**: Click "Sync Now" to test connectivity
4. **System Settings**: Verify backend URL and credentials
5. **Contact Admin**: Report persistent sync issues

## 💡 Tips & Best Practices

✅ **Do:**
- Keep auto-sync interval reasonable (5-30 minutes)
- Click "Sync Now" before closing the app
- Check sync status indicator regularly
- Monitor logs for errors
- Restart app after changing sync settings

❌ **Don't:**
- Set sync interval to less than 1 minute
- Disable auto-sync unless necessary
- Close app during active sync (let it complete)
- Change settings while sync is running
- Ignore persistent sync errors

## 🎓 Understanding Sync Status

### Idle (Gray Dot)
- No sync operation in progress
- Ready for manual sync
- Auto-sync will run at scheduled time
- **Normal state** between syncs

### Syncing (Orange Dot)
- Sync operation currently running
- Don't close the application
- Wait for completion
- **Temporary state** during sync

### Synced (Green Checkmark)
- Last sync completed successfully
- All data is up-to-date
- Statistics show items synced
- **Good state** - everything is working

### Failed (Red X)
- Last sync encountered an error
- Check logs for error details
- Try "Sync Now" again
- Verify backend connectivity
- **Action needed** - investigate error

## 📊 Example Sync Cycle

```
14:25:00 - Auto-sync starts (interval elapsed)
14:25:05 - Fetching clients from server...
14:25:10 - Saved 25 clients to database
14:25:15 - Fetching forms from server...
14:25:20 - Saved 8 forms to database
14:25:25 - Checking for pending submissions...
14:25:30 - Sent 3 form submissions
14:25:35 - Sync completed successfully
          Status: Synced ✓
          Clients: 25, Forms: 8, Submissions: 3
```

## 🚀 Getting Started

1. **First Time Setup:**
   - Go to Admin Panel → System Settings
   - Configure backend server URL
   - Set auto-sync interval
   - Click "Test Connection"
   - Save settings and restart app

2. **First Sync:**
   - Click "⚡ Sync Now"
   - Wait for progress dialog to show results
   - Confirm clients/forms are downloaded
   - Check sync status indicator

3. **Ongoing Use:**
   - Monitor sync status in sidebar
   - Let auto-sync run in background
   - Click "Sync Now" when needed
   - Check logs if issues occur

---

**Version**: 1.0 | **Last Updated**: October 2024
