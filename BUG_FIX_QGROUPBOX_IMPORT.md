# Bug Fix: Missing QGroupBox Import

## Issue
When logging in to the Python Pharmacy App, an error occurred:
```
NameError: name 'QGroupBox' is not defined
```

This happened in `ui/admin_panel.py` line 223 when trying to create the System Settings tab.

## Root Cause
The `QGroupBox` widget was used in the `create_system_settings_tab()` method but was not imported in the module's import statements.

## Solution
Added `QGroupBox` to the imports in `ui/admin_panel.py`:

**Before:**
```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QTabWidget, QListWidget, QListWidgetItem,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QTextEdit
)
```

**After:**
```python
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QTabWidget, QListWidget, QListWidgetItem,
    QLineEdit, QComboBox, QCheckBox, QSpinBox, QTextEdit, QGroupBox
)
```

## Status
✅ Fixed - App now launches successfully after login

## Testing
1. Login to the app with valid credentials
2. MainWindow initializes without errors
3. Admin Panel opens with System Settings tab visible
4. QGroupBox containers display correctly

## Files Modified
- `python-pharmacy-app/ui/admin_panel.py` (line 5-8)

## Related Changes
This fix was necessary due to the new System Settings tab implementation that uses `QGroupBox` widgets for grouping settings sections:
- Backend Server Configuration section
- Pharmacy Configuration section
- Advanced Settings button section

All other functionality remains unchanged.
