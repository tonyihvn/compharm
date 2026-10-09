# React Backend - JSON Form Management Integration Guide

## Overview
This guide provides instructions for setting up the React backend server to properly manage JSON forms and sync them with the Python pharmacy application.

---

## 1. Form Upload and Management

### Current Status
- ✅ Upload endpoint exists: `POST /api/forms/upload`
- ✅ Database models configured
- ✅ Authentication required (admin only)
- ⚠️ Need to verify file upload handling

### Form Structure
The backend expects JSON forms in this structure:

```json
{
  "id": "unique-form-id",
  "uuid": "optional-uuid",
  "name": "Form Display Name",
  "description": "Optional description",
  "pages": [
    {
      "sections": [
        {
          "name": "section-name",
          "questions": [
            {
              "id": "field-id",
              "type": "text|select|radio|checkbox|date",
              "label": "Field Label",
              "required": true,
              "options": ["option1", "option2"],
              "validation": "regex-pattern"
            }
          ]
        }
      ]
    }
  ]
}
```

### Required API Endpoints (Already in forms.js)

#### 1. Upload/Create Form
**Endpoint**: `POST /api/forms/upload`
**Auth**: Required (Admin only)
**Body**: JSON form data (as shown above)
**Response**:
```json
{
  "message": "Form created successfully",
  "data": {
    "id": "form-id",
    "form_name": "Form Name",
    "form_uuid": "unique-uuid",
    "form_data": {...},
    "version": 1,
    "created_by": "user-id",
    "is_active": true
  }
}
```

#### 2. List Forms
**Endpoint**: `GET /api/forms`
**Auth**: Required
**Query Params**: `page`, `limit`, `active`
**Response**:
```json
{
  "message": "Forms retrieved successfully",
  "data": [...],
  "total": 10,
  "page": 1,
  "pages": 1
}
```

#### 3. Get Form Details
**Endpoint**: `GET /api/forms/{formId}`
**Auth**: Required
**Response**:
```json
{
  "message": "Form retrieved successfully",
  "data": {
    "id": "form-id",
    "form_name": "Form Name",
    "form_data": {...},
    "version": 2
  }
}
```

#### 4. Update Form
**Endpoint**: `PUT /api/forms/{formId}`
**Auth**: Required (Admin only)
**Body**: Updated JSON form data
**Response**: Updated form object with incremented version

#### 5. Delete Form
**Endpoint**: `DELETE /api/forms/{formId}`
**Auth**: Required (Admin only)
**Response**:
```json
{
  "message": "Form deleted successfully"
}
```

---

## 2. Form Synchronization with Python App

### Sync Flow

```
Python App Start
    ↓
→ GET /api/forms (fetch available forms)
    ↓
→ Store forms locally (cached)
    ↓
→ Display in Admin Panel → Forms Management
    ↓
User selects form to preview/edit
    ↓
→ GET /api/forms/{formId} (fetch full form data)
    ↓
→ Render form in preview/editor
```

### Current Implementation in Python App

The Python app expects forms to be returned with this structure in the list view:
```python
# In load_forms_list():
item_data = {
    'id': form['id'],
    'form_data': form['form_data'],  # Full JSON
    'is_local': False,
    'is_remote': True
}
```

### Verification Needed
1. Ensure `/api/forms` returns forms with complete `form_data` field
2. Ensure `/api/forms/{formId}` response wraps data in `data` key:
   ```json
   { "data": { "form_data": {...} } }
   ```

---

## 3. Form Response/Submission Handling

### Python App → Backend Submission Flow

```
Python App (Clients Management)
    ↓
→ User selects client
→ Click "Fill Form" button
    ↓
→ Render form with client data
    ↓
→ User fills form
→ Click "Submit"
    ↓
→ POST /api/submissions (send filled form data)
    ↓
Backend stores submission
    ↓
Python App stores locally & marks as synced
```

### Required Endpoint (Check if implemented)

**Endpoint**: `POST /api/submissions`
**Auth**: Required
**Body**:
```json
{
  "form_id": "form-id",
  "client_id": "client-pepfar-id",
  "filled_by_user_id": "user-id",
  "form_data": {
    "field-id-1": "value-1",
    "field-id-2": "value-2"
  },
  "status": "submitted",
  "filled_at": "2026-10-09T12:00:00Z"
}
```

**Response**:
```json
{
  "message": "Submission created successfully",
  "data": {
    "id": "submission-id",
    "form_id": "form-id",
    "client_id": "client-id",
    "form_data": {...},
    "status": "submitted",
    "server_submission_id": "server-id"
  }
}
```

### GET Submissions (Already exists)

**Endpoint**: `GET /api/forms/{formId}/submissions`
**Auth**: Required
**Query Params**: `page`, `limit`, `status`

---

## 4. Admin Panel Form Upload Feature

### User Flow (Python App)

1. Admin goes to: Admin Panel → Forms Management → "Upload Form"
2. Selects JSON file from computer
3. Python app sends: `POST /api/forms/upload`
4. Backend validates and stores
5. Form appears in Forms Management list

### Testing

Create a sample JSON form file and test:
```bash
curl -X POST http://localhost:5000/api/forms/upload \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d @form.json
```

---

## 5. Critical Fixes Needed in React Backend

### Issue 1: Authorization Header Validation
**Status**: Check
**Action**: Ensure all endpoints properly validate Bearer token
```javascript
// In auth middleware
if (!req.headers.authorization || !req.headers.authorization.startsWith('Bearer ')) {
    return res.status(401).json({ message: 'Missing or invalid authorization' });
}
```

### Issue 2: Response Consistency
**Status**: Check
**Action**: Ensure all form endpoints wrap responses in `data` key
```javascript
// Ensure this pattern
res.json({
    message: "...",
    data: form  // <-- Wrapped in 'data'
});
```

### Issue 3: Connection Reset Errors
**Status**: Investigate
**Action**: 
- Check if forms are too large (> 1MB)
- Increase request timeout on server
- Add better error logging

**Solution in server.js**:
```javascript
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));
```

### Issue 4: CORS Headers (if needed)
**Status**: Verify
**Action**: Ensure CORS is properly configured for Python app requests
```javascript
import cors from 'cors';

app.use(cors({
    origin: '*',  // Or specify Python app URL
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    allowedHeaders: ['Content-Type', 'Authorization']
}));
```

---

## 6. Testing Checklist

### Admin Panel Form Management

- [ ] **Upload Form**
  - [ ] Admin clicks "Upload Form" button
  - [ ] Selects a valid JSON form file
  - [ ] Backend receives upload and stores successfully
  - [ ] Form appears in Forms Management list
  - [ ] Error message shown if JSON invalid

- [ ] **List Forms**
  - [ ] Admin Panel shows all uploaded forms
  - [ ] Forms show name, version, upload date
  - [ ] Forms can be paginated

- [ ] **Preview Form**
  - [ ] Admin selects form and clicks "Preview"
  - [ ] Form displays correctly (no rendering errors)
  - [ ] Form is read-only (cannot submit)
  - [ ] Connection errors handled gracefully

- [ ] **Edit Form**
  - [ ] Admin selects form and clicks "Edit"
  - [ ] Form editor opens with JSON preview
  - [ ] Can make changes and save
  - [ ] Form version incremented
  - [ ] Cached form data used if server unreachable

- [ ] **Delete Form**
  - [ ] Admin can delete form with confirmation
  - [ ] Form removed from list
  - [ ] Proper error handling if form not found

### Form Synchronization

- [ ] Python app fetches forms on startup
- [ ] Forms cached locally
- [ ] Forms available even offline
- [ ] Form list refreshes when "Sync Now" clicked
- [ ] New forms appear after sync

### Submission Handling

- [ ] Client opens form for filling
- [ ] Form renders with client details pre-filled
- [ ] Client can fill all field types correctly
- [ ] Form submission sends data to backend
- [ ] Submission appears in Forms → Submissions list
- [ ] Submissions can be reviewed and exported

---

## 7. Database Schema Verification

### PharmacyForm Table
```sql
CREATE TABLE pharmacy_forms (
  id UUID PRIMARY KEY,
  form_uuid VARCHAR UNIQUE,
  form_name VARCHAR NOT NULL,
  description TEXT,
  form_data JSON NOT NULL,  -- Full form definition
  version INTEGER DEFAULT 1,
  is_active BOOLEAN DEFAULT true,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### FormSubmission Table
```sql
CREATE TABLE form_submissions (
  id UUID PRIMARY KEY,
  form_id UUID REFERENCES pharmacy_forms(id),
  client_id VARCHAR,  -- PEPFAR ID
  filled_by_user_id UUID REFERENCES users(id),
  form_data JSON NOT NULL,  -- Filled form data
  status VARCHAR DEFAULT 'draft',  -- draft, submitted, synced
  filled_at TIMESTAMP,
  is_synced_to_server BOOLEAN DEFAULT false,
  synced_at TIMESTAMP,
  server_submission_id VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 8. Troubleshooting

### Forms not showing in Python App
1. Check: GET /api/forms returns 200 status
2. Check: Response includes `data` array with forms
3. Check: Each form has `id`, `form_name`, `form_data` fields
4. Check: Python app has valid auth token

### Form preview shows error
1. Check: GET /api/forms/{formId} returns 200 status
2. Check: Response wraps form in `data` key
3. Check: `form_data` field contains valid JSON
4. Check: Form JSON has required `name` and at least one section

### Connection reset when editing forms
1. Check: Server logs for specific errors
2. Check: Form size (too large may exceed timeout)
3Check: Network timeout settings (increase to 30s)
4. Check: Server memory/CPU usage during form operations

### Submissions not syncing
1. Check: POST /api/submissions endpoint returns 201 status
2. Check: Response includes `server_submission_id`
3. Check: Python app receives and stores submission ID
4. Check: Submissions marked as `is_synced_to_server = true`

---

## 9. Configuration

### Environment Variables (.env)

```
# Backend Server
BACKEND_PORT=5000
BACKEND_HOST=0.0.0.0
NODE_ENV=production

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pharmacy_sync
DB_USER=postgres
DB_PASSWORD=password

# Form upload limits
MAX_FORM_SIZE=52428800  # 50MB
REQUEST_TIMEOUT=30000   # 30 seconds

# CORS
CORS_ORIGIN=*
```

### Python App Config (.env)

```
BACKEND_URL=http://localhost:5000
BACKEND_TIMEOUT=30
FORM_CACHE_DIR=./forms_cache
```

---

## 10. Next Steps

1. **Verify existing endpoints** are working as expected
2. **Test form upload** from Python app
3. **Test form sync** on startup
4. **Implement form rendering** in Python app (convert JSON to PyQt6 widgets)
5. **Test form submission** flow end-to-end
6. **Monitor performance** with large forms
7. **Add form versioning** UI to track changes

---

## Important Notes

- ✅ Authentication middleware is working
- ✅ Form CRUD endpoints are implemented
- ⚠️ Form rendering in Python app needs implementation
- ⚠️ Form submission flow needs testing
- ⚠️ Connection resilience needs improvement
- 🔄 Sync scheduling is implemented but needs verification

---

## Support

For issues with form synchronization:
1. Check Python app logs: `logs/` directory
2. Check React server logs: `logs/` directory
3. Verify network connectivity between Python and React
4. Test endpoints manually with curl or Postman
5. Review database for stored forms and submissions
