# Community Pharmacy App - Python Desktop

A professional desktop application for community pharmacies to manage drug dispensing using OpenMRS-compliant JSON forms.

## Architecture

- **UI Framework**: PyQt6 (Desktop)
- **Database**: SQLite (local)
- **Backend Integration**: REST API (connects to React Central Server)
- **Form Engine**: Custom JSON form renderer with conditional logic and validation

## Features

- Role-based access (Admin, Pharmacy Staff, Facility)
- Upload and manage OpenMRS JSON forms
- Download and manage client data from central server
- Display and fill dynamic forms
- Sync data with central server
- Offline-first architecture with automatic sync

## Directory Structure

```
python-pharmacy-app/
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── constants.py
├── database/
│   ├── __init__.py
│   ├── models.py
│   ├── db_manager.py
│   └── migrations/
├── api/
│   ├── __init__.py
│   ├── client.py
│   └── sync_manager.py
├── forms/
│   ├── __init__.py
│   ├── form_engine.py
│   ├── validators.py
│   ├── condition_evaluator.py
│   └── widgets/
│       ├── __init__.py
│       ├── base_widget.py
│       ├── text_widget.py
│       ├── select_widget.py
│       ├── date_widget.py
│       ├── checkbox_widget.py
│       └── file_widget.py
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── login_window.py
│   ├── clients_view.py
│   ├── client_details_view.py
│   ├── form_view.py
│   ├── admin_panel.py
│   ├── styles.py
│   └── dialogs/
│       ├── __init__.py
│       ├── form_upload_dialog.py
│       ├── client_sync_dialog.py
│       └── sync_status_dialog.py
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── validators.py
│   └── helpers.py
├── resources/
│   ├── icons/
│   └── styles/
└── main.py
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Configuration

See `config/settings.py` for environment variables:
- `CENTRAL_SERVER_URL`: API endpoint for central server
- `SYNC_INTERVAL`: Auto-sync interval in minutes
- `DATABASE_PATH`: SQLite database location

## API Integration

The app communicates with a React backend server. See API documentation for:
- `/api/clients/download` - Pull client data
- `/api/forms/submit` - Submit form data
- `/api/auth/login` - Authentication

## Database Schema

- **Users**: Admin, Pharmacy Staff, Facility users
- **Clients**: Patient data from facilities
- **Forms**: Uploaded JSON form definitions
- **FormSubmissions**: Completed form data
- **SyncLog**: Sync history and status
