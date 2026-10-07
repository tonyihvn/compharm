# ComPharm Complete System Implementation Guide

## Overview
ComPharm is a comprehensive pharmacy management system enabling:
- **Admin Dashboard** - Professional UI with statistics and charts
- **Client Management** - Full CRUD operations with customizable fields
- **User Management** - Role-based access control (Admin, Pharmacy Staff, Facility Manager)
- **API Integration** - OpenMRS, Python Pharmacy App, and backend server integration
- **Field Configuration** - Admin-customizable client form fields

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Backend Server                      │
│              (http://localhost:3001)                          │
├──────────────────┬──────────────────┬──────────────────────┤
│   Web UI         │   REST APIs      │   Database           │
│  (Dashboard)     │  (for clients)   │  (SQLite/MySQL)      │
├──────────────────┴──────────────────┴──────────────────────┤
│                                                              │
│  ┌─────────────────────┐  ┌─────────────────────┐         │
│  │   OpenMRS App       │  │  Python App         │         │
│  │   (Facility)        │  │  (Pharmacy)         │         │
│  └─────────────────────┘  └─────────────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints Reference

### Authentication
```
POST /api/auth/login
  Request: { email, password }
  Response: { token, user: { id, email, role, pharmacyId, facilityId } }

POST /api/auth/signup (Admin only)
  Request: { username, email, password, full_name, role, pharmacy_id?, facility_id? }
  Response: { message, userId }
```

### Clients
```
GET /api/clients
  Query: ?pharmacyCode=X or ?facilityId=Y or ?page=1&limit=20
  Response: { clients: [...], total, page, pages }
  Auth: Required (auto-filtered by role)

GET /api/clients/:clientId
  Response: { client: {...} }
  Auth: Required

POST /api/clients
  Request: { name, pepfar_id, facility_id, pharmacy_id, phone?, email?, address?, age?, gender? }
  Response: { message, clients: [...] }
  Auth: Required

PUT /api/clients/:clientId
  Request: { name?, pepfar_id?, facility_id?, pharmacy_id?, ... }
  Response: { message, client: {...} }
  Auth: Required

DELETE /api/clients/:clientId
  Response: { message }
  Auth: Required
```

### Client Fields
```
GET /api/fields
  Response: { fields: [...] }
  Auth: Required

POST /api/fields (Admin only)
  Request: { name, field_name, field_type, required?, order_index? }
  Response: { message, field: {...} }
  Auth: Required, Admin

PUT /api/fields/:fieldId (Admin only)
  Request: { name?, field_type?, required?, order_index? }
  Response: { message, field: {...} }
  Auth: Required, Admin

DELETE /api/fields/:fieldId (Admin only)
  Response: { message }
  Auth: Required, Admin

POST /api/fields/reset/defaults (Admin only)
  Response: { message, fields: [...] }
  Auth: Required, Admin
```

### Forms
```
POST /api/forms/upload
  Request: FormData { form_file, name, description }
  Response: { message, form: {...} }
  Auth: Required

GET /api/forms
  Response: { forms: [...] }
  Auth: Required

PUT /api/forms/:formId
  Request: { name, description, definition }
  Response: { message, form: {...} }
  Auth: Required

DELETE /api/forms/:formId
  Response: { message }
  Auth: Required
```

### Submissions
```
POST /api/submissions
  Request: { form_id, client_id, pepfar_id, pharmacy_client_id, form_data, status }
  Response: { message, submission: {...} }
  Auth: Required

GET /api/submissions
  Query: ?form_id=X&client_id=Y&page=1&limit=20
  Response: { submissions: [...], total, page, pages }
  Auth: Required

GET /api/submissions/:submissionId
  Response: { submission: {...} }
  Auth: Required
```

---

## Using the System

### 1. Web Dashboard (Admin)

**Login:**
- URL: http://localhost:3001
- Email: super@compharm.org
- Password: @@ComPharm22

**Features:**
- 📊 Dashboard - View statistics and charts
- 👥 Clients - List, view, edit, delete clients
- ➕ New Client - Create new clients
- 👤 Users - Manage system users
- 👤➕ New User - Create users with roles
- 📋 Fields - Configure client form fields
- ⚙️ Settings - System configuration

### 2. Managing Client Fields

**Default Fields:**
- Full Name (required)
- PEPFAR ID (required)
- Date of Birth
- Gender
- Phone Number
- Email
- Address

**Customize:**
1. Go to "Fields" tab
2. Click "Add Field"
3. Enter field details:
   - Field Name: Display name
   - Field Type: text, email, tel, number, date, select
   - Required: Yes/No
4. Click "Save"

**API Example:**
```bash
curl -X POST http://localhost:3001/api/fields \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Marital Status",
    "field_name": "marital_status",
    "field_type": "select",
    "required": false,
    "order_index": 8
  }'
```

---

## OpenMRS Integration

### Create Client via API

**Endpoint:** `POST /api/clients`

**Example Request:**
```bash
curl -X POST http://localhost:3001/api/clients \
  -H "Authorization: Bearer <openmrs_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "pepfar_id": "PEPFAR-2024-LAG-001",
    "facility_id": "FAC-LAGOS-001",
    "pharmacy_id": "PHARM-IKOYI-001",
    "phone": "+234-123-4567",
    "email": "john@example.com",
    "gender": "M"
  }'
```

**Response:**
```json
{
    "message": "Client created successfully",
    "clients": [
        {
            "id": "uuid-123",
            "name": "John Doe",
            "pepfarId": "PEPFAR-2024-LAG-001",
            "pharmacyCode": "PHARM-IKOYI-001",
            "facilityCode": "FAC-LAGOS-001"
        }
    ]
}
```

### Fetch Clients via API

**Endpoint:** `GET /api/clients`

**Example Request:**
```bash
curl -X GET "http://localhost:3001/api/clients?page=1&limit=50" \
  -H "Authorization: Bearer <openmrs_token>"
```

**Response:**
```json
{
    "message": "Clients retrieved successfully",
    "clients": [...],
    "total": 100,
    "page": 1,
    "pages": 2
}
```

---

## Python App Integration

### 1. System Settings - Backend Credentials

**Location:** Python App → Admin Panel → System Settings

**Fields:**
- Backend Server URL: http://localhost:3001
- Username: Your backend username
- Password: Your backend password

**Storage:** These credentials are stored in the app database (not recommended for production)

### 2. Download Clients

**Python App Code:**
```python
def download_clients():
    # Get credentials from settings
    username = settings.BACKEND_USERNAME
    password = settings.BACKEND_PASSWORD
    pharmacy_code = settings.PHARMACY_ID
    
    # Authenticate
    auth_response = requests.post(
        f"{settings.BACKEND_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    token = auth_response.json()['token']
    
    # Download clients
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f"{settings.BACKEND_URL}/api/clients?pharmacyCode={pharmacy_code}",
        headers=headers
    )
    
    clients = response.json()['clients']
    # Save to local database
```

### 3. Upload Form Submissions

**Python App Code:**
```python
def submit_form():
    # Get credentials from settings
    username = settings.BACKEND_USERNAME
    password = settings.BACKEND_PASSWORD
    
    # Authenticate
    auth_response = requests.post(
        f"{settings.BACKEND_URL}/api/auth/login",
        json={"username": username, "password": password}
    )
    token = auth_response.json()['token']
    
    # Submit form
    headers = {'Authorization': f'Bearer {token}'}
    submission_data = {
        "form_id": form_id,
        "client_id": client_id,
        "pepfar_id": client_pepfar_id,
        "pharmacy_client_id": pharmacy_client_id,
        "form_data": {...},
        "status": "submitted"
    }
    
    response = requests.post(
        f"{settings.BACKEND_URL}/api/submissions",
        json=submission_data,
        headers=headers
    )
```

---

## Testing All APIs

### Test 1: Login

```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "super@compharm.org",
    "password": "@@ComPharm22"
  }'
```

**Expected Response:** `{ "token": "eyJ...", "user": {...} }`

### Test 2: Create Client

```bash
# Replace <token> with the token from login
curl -X POST http://localhost:3001/api/clients \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Patient",
    "pepfar_id": "PEPFAR-TEST-001",
    "facility_id": "FAC-TEST-001",
    "pharmacy_id": "PHARM-TEST-001",
    "phone": "+234-123-4567"
  }'
```

### Test 3: Get Clients

```bash
curl -X GET "http://localhost:3001/api/clients?page=1&limit=10" \
  -H "Authorization: Bearer <token>"
```

### Test 4: Add Custom Field

```bash
curl -X POST http://localhost:3001/api/fields \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Occupation",
    "field_name": "occupation",
    "field_type": "text",
    "required": false,
    "order_index": 8
  }'
```

### Test 5: Update Client

```bash
curl -X PUT "http://localhost:3001/api/clients/<clientId>" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "phone": "+234-987-6543"
  }'
```

### Test 6: Delete Client

```bash
curl -X DELETE "http://localhost:3001/api/clients/<clientId>" \
  -H "Authorization: Bearer <token>"
```

---

## User Roles & Permissions

| Operation | Admin | Pharmacy | Facility | Note |
|-----------|-------|----------|----------|------|
| View Dashboard | ✅ | ✅ | ✅ | Own data only for non-admin |
| Create Client | ✅ | ✅ | ✅ | Own pharmacy/facility only |
| View Clients | ✅ | ✅ | ✅ | Auto-filtered by role |
| Edit Client | ✅ | ✅ | ✅ | Own pharmacy/facility only |
| Delete Client | ✅ | ✅ | ✅ | Own pharmacy/facility only |
| Create User | ✅ | ❌ | ❌ | Admin only |
| Manage Fields | ✅ | ❌ | ❌ | Admin only |
| View All Data | ✅ | ❌ | ❌ | Admin only |

---

## System Architecture Details

### Database Models

**User**
- id (UUID)
- username, email
- password_hash
- full_name
- role (admin, pharmacy_staff, facility_manager)
- pharmacy_id (FK, for pharmacy staff)
- facility_id (FK, for facility managers)
- is_active, last_login

**Client**
- id (UUID)
- full_name, pepfar_id
- gender, phone_number, email, address
- date_of_birth
- facility_id (FK)
- pharmacy_id (FK)
- is_active

**ClientField**
- id (UUID)
- name (display name)
- field_name (database column)
- field_type (text, email, tel, number, date, select)
- required (boolean)
- order_index (display order)

**Pharmacy**
- id (UUID)
- pharmacy_code (unique)
- pharmacy_name
- api_key
- is_active

**Facility**
- id (UUID)
- facility_code (unique)
- facility_name
- is_active

**Form**
- id (UUID)
- name
- description
- definition (JSON)
- created_by_id (FK to User)
- is_active

**FormSubmission**
- id (UUID)
- form_id (FK)
- client_id (FK)
- pepfar_id
- pharmacy_client_id
- form_data (JSON)
- status (drafted, submitted, synced)
- created_at, updated_at

---

## Configuration

### Environment Variables (.env)

```env
NODE_ENV=development
PORT=3001
DB_TYPE=sqlite
JWT_SECRET=your-secret-key-here
CORS_ORIGIN=http://localhost:3000
```

### Database

- **SQLite** (default) - `pharmacy_sync_backend.db`
- **MySQL** (optional) - Configure DB_TYPE=mysql and connection details

---

## Security Best Practices

1. **Authentication:** Use JWT tokens with 24-hour expiration
2. **Authorization:** Role-based access control on all endpoints
3. **Data Isolation:** Users see only their organization's data
4. **Passwords:** Hashed with bcrypt (salt rounds: 10)
5. **HTTPS:** Use in production (not just HTTP)
6. **CORS:** Configured to allow specific origins
7. **Input Validation:** All inputs validated server-side

---

## Troubleshooting

### "Invalid credentials" on login
- Verify email and password
- Check user exists in database
- Ensure password is correctly hashed

### "You can only edit clients in your pharmacy" error
- Verify user's pharmacy_id matches client's pharmacy
- Check user role and permissions
- Ensure proper authorization token

### Client fields not showing
- Verify fields exist in database
- Check field type is supported
- Verify order_index is set correctly

### Forms upload failing
- Check file format is valid JSON
- Verify file size < 5MB
- Check form has required fields

---

## Performance Optimization

- Database indexing on frequently queried fields
- Pagination support (default 20 items per page)
- Efficient relationship loading (eager loading)
- Caching for client lists (consider Redis)
- Query optimization for large datasets

---

## API Rate Limiting (Future)

Recommended implementation:
- 100 requests/minute for authenticated users
- 10 requests/minute for public endpoints
- Exponential backoff on repeated failures

---

## Deployment Checklist

- [ ] Change JWT_SECRET to strong random value
- [ ] Set NODE_ENV=production
- [ ] Configure MySQL database
- [ ] Enable HTTPS/TLS
- [ ] Set up proper CORS origins
- [ ] Configure email notifications (optional)
- [ ] Set up log aggregation
- [ ] Configure database backups
- [ ] Test all APIs thoroughly
- [ ] Train end users
- [ ] Have rollback plan ready

---

## Support & Documentation

- **Frontend:** Responsive web UI with professional dashboard
- **Backend:** RESTful APIs with comprehensive error handling
- **Database:** Automatic schema migration and seeding
- **Testing:** Manual and API testing guides provided
- **Logging:** Comprehensive logging for debugging

---

## Version Information

- **Version:** 1.0.0
- **Last Updated:** 2026-10-07
- **Status:** Production Ready

---

## Future Enhancements

1. Advanced reporting and analytics
2. Export to Excel/CSV
3. Two-factor authentication
4. Audit logging
5. Workflow automation
6. Mobile app
7. Real-time sync
8. Offline mode with conflict resolution
9. Data encryption at rest
10. Multi-language support

