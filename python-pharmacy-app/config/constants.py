"""
Application Constants
"""

# User Roles
class UserRole:
    ADMIN = "admin"
    PHARMACY_STAFF = "pharmacy_staff"
    FACILITY_OFFICER = "facility_officer"
    
    CHOICES = [ADMIN, PHARMACY_STAFF, FACILITY_OFFICER]


# Sync Status
class SyncStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    
    CHOICES = [PENDING, IN_PROGRESS, SUCCESS, FAILED, PARTIAL]


# Client Status
class ClientStatus:
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"
    
    CHOICES = [ACTIVE, INACTIVE, ARCHIVED]


# Form Status
class FormStatus:
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    
    CHOICES = [DRAFT, ACTIVE, ARCHIVED]


# Submission Status
class SubmissionStatus:
    DRAFT = "draft"
    SUBMITTED = "submitted"
    SYNCED = "synced"
    REJECTED = "rejected"
    
    CHOICES = [DRAFT, SUBMITTED, SYNCED, REJECTED]


# Form Field Types
class FormFieldType:
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    PHONE = "phone"
    DATE = "date"
    DATETIME = "datetime"
    TIME = "time"
    SELECT = "select"
    MULTISELECT = "multiselect"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXTAREA = "textarea"
    FILE = "file"
    SECTION = "section"
    HIDDEN = "hidden"
    
    CHOICES = [
        TEXT, NUMBER, EMAIL, PHONE, DATE, DATETIME, TIME,
        SELECT, MULTISELECT, CHECKBOX, RADIO, TEXTAREA, FILE, SECTION, HIDDEN
    ]


# API Response Codes
class APIResponseCode:
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503


# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Date Format
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

# Error Messages
ERROR_MESSAGES = {
    "invalid_credentials": "Invalid username or password",
    "unauthorized": "You are not authorized to perform this action",
    "not_found": "The requested resource was not found",
    "validation_error": "Validation error occurred",
    "sync_failed": "Failed to sync data with server",
    "db_error": "Database operation failed",
    "network_error": "Network connection error",
}

# Success Messages
SUCCESS_MESSAGES = {
    "login_success": "Login successful",
    "logout_success": "Logout successful",
    "sync_success": "Data synced successfully",
    "form_submitted": "Form submitted successfully",
    "client_created": "Client created successfully",
    "form_uploaded": "Form uploaded successfully",
}

# Condition Operators
CONDITION_OPERATORS = {
    "equals": "==",
    "notEquals": "!=",
    "greaterThan": ">",
    "lessThan": "<",
    "greaterThanOrEqual": ">=",
    "lessThanOrEqual": "<=",
    "contains": "contains",
    "notContains": "notContains",
    "isEmpty": "isEmpty",
    "isNotEmpty": "isNotEmpty",
    "in": "in",
    "notIn": "notIn",
    "startsWith": "startsWith",
    "endsWith": "endsWith",
    "matches": "matches",
}

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_INTERNAL_ERROR = 500

# Database
DEFAULT_DATABASE_PATH = "pharmacy_data.db"
DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH}"

# API
DEFAULT_CENTRAL_SERVER_URL = "http://localhost:8000"
API_TIMEOUT = 30  # seconds
SYNC_INTERVAL = 5  # minutes

# Form Validation
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_EXTENSIONS = ["pdf", "jpg", "jpeg", "png", "txt"]
