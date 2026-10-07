# User Management & Role-Based Access Control Implementation

## Overview
Enhanced the React backend server with comprehensive user management and role-based access control. Users can now be created with specific roles (Pharmacy Staff, Facility Manager, Admin) and each role has appropriate access to manage clients based on their assigned facility or pharmacy.

---

## Key Features Implemented

### 1. Enhanced User Creation Form
**File:** `react-backend-server/public/index.html`

**Features:**
- Role-dependent field visibility
  - **Pharmacy Staff**: Must have a Pharmacy ID (e.g., PHARM-IKOYI-001)
  - **Facility Manager**: Must have a Facility ID (e.g., FAC-LAGOS-001)
  - **Admin**: No facility/pharmacy restriction
- All required fields are marked with red asterisk
- Form validation ensures appropriate fields are filled based on selected role

**How It Works:**
```javascript
// When user selects a role, appropriate fields appear
- Role: "pharmacy_staff" → Shows Pharmacy ID field
- Role: "facility_manager" → Shows Facility ID field
- Role: "admin" → Shows both fields (optional)
```

### 2. Role-Based Client Filtering
**File:** `react-backend-server/public/index.html` + `src/routes/clients.js`

**Features:**
- Users only see clients assigned to their facility or pharmacy
- Pharmacy Staff sees only clients in their pharmacy
- Facility Managers see only clients in their facility
- Admins see all clients
- Filtering happens automatically when loading the clients list

**Implementation:**
```javascript
// Frontend filters based on user role
if (user.role === 'pharmacy_staff' && user.pharmacyId) {
    url += `?pharmacyCode=${user.pharmacyId}`;
} else if (user.role === 'facility_manager' && user.facilityId) {
    url += `?facilityId=${user.facilityId}`;
}
```

### 3. Client Management (Edit/Delete)
**Files:** 
- `react-backend-server/public/index.html`
- `react-backend-server/src/routes/clients.js`

**Features:**
- Each client displays Edit and Delete buttons
- Edit opens a modal dialog with all client fields
- Users can only edit/delete clients in their own facility/pharmacy
- Admin users can manage all clients
- Delete action requires confirmation

**Edit Modal Form:**
- Client Name (required)
- PEPFAR ID (required)
- Facility ID (required)
- Pharmacy ID (required)
- Age
- Gender
- Phone Number
- Email
- Address

**Authorization Checks:**
```javascript
// Backend verifies user has permission to edit
if (user.role === 'pharmacy_staff' && client.pharmacyCode !== user.pharmacyId) {
    return res.status(403).json({ message: 'You can only edit clients in your pharmacy' });
}
```

### 4. API Endpoints (Updated/Enhanced)

#### POST /api/auth/signup
**Enhanced to include:**
- `pharmacy_id` for pharmacy staff users
- `facility_id` for facility managers
- Validation that required field is provided based on role

**Example Request:**
```json
{
    "username": "pharmastaff01",
    "email": "pharmastaff01@compharm.org",
    "password": "TestPass123!",
    "full_name": "John Pharmacy",
    "role": "pharmacy_staff",
    "pharmacy_id": "PHARM-IKOYI-001"
}
```

#### POST /api/auth/login
**Response now includes:**
- `pharmacyId`: User's assigned pharmacy (if pharmacy_staff)
- `facilityId`: User's assigned facility (if facility_manager)

**Example Response:**
```json
{
    "message": "Login successful",
    "token": "eyJhbGc...",
    "user": {
        "id": "uuid",
        "email": "pharmastaff01@compharm.org",
        "role": "pharmacy_staff",
        "pharmacyId": "PHARM-IKOYI-001",
        "facilityId": null
    }
}
```

#### GET /api/clients
**Enhanced query parameters:**
- `?pharmacyCode=PHARM-IKOYI-001` - Get clients for a pharmacy
- `?facilityId=uuid` - Get clients for a facility

**Authorization:** Authentication required, filtered by user role

#### GET /api/clients/:clientId
**Enhanced Response Format:**
```json
{
    "message": "Client retrieved successfully",
    "client": {
        "id": "uuid",
        "name": "Mary Johnson",
        "pepfarId": "PEPFAR-2024-001",
        "facilityCode": "FAC-LAGOS-001",
        "pharmacyCode": "PHARM-IKOYI-001",
        "age": 35,
        "gender": "F",
        "phone": "+234-XXX-XXXX",
        "email": "mary@example.com",
        "address": "Lagos, Nigeria"
    }
}
```

#### PUT /api/clients/:clientId
**Updates client information with:**
- Automatic field mapping (name → full_name, phone → phone_number, etc.)
- Support for creating new facility/pharmacy records if needed
- Authorization checks per user role
- Returns properly formatted response

**Example Request:**
```json
{
    "name": "Mary Johnson Updated",
    "pepfar_id": "PEPFAR-2024-001",
    "facility_id": "FAC-LAGOS-001",
    "pharmacy_id": "PHARM-IKOYI-001",
    "age": 36,
    "gender": "F",
    "phone": "+234-123-4567",
    "email": "mary.updated@example.com",
    "address": "New Address, Lagos"
}
```

#### DELETE /api/clients/:clientId
**Authorization:**
- Pharmacy Staff can delete clients in their pharmacy
- Facility Manager can delete clients in their facility
- Admin can delete any client
- Returns 403 if user not authorized

---

## User Roles & Permissions

### Admin
- ✅ Create/Read/Update/Delete all users
- ✅ Create/Read/Update/Delete all clients
- ✅ View all facilities and pharmacies
- ✅ Access all forms and submissions

### Facility Manager
- ✅ Create/Read/Update/Delete clients in their facility
- ✅ View only clients in their facility
- ❌ Cannot create users
- ❌ Cannot access other facilities' data

### Pharmacy Staff
- ✅ Create/Read/Update/Delete clients in their pharmacy
- ✅ View only clients in their pharmacy
- ✅ Submit forms for clients
- ❌ Cannot create users
- ❌ Cannot access other pharmacies' data

---

## Frontend UI Changes

### Dashboard User Info Display
```html
<div class="user-info">
    <p><strong>User:</strong> <span id="currentUser"></span></p>
    <p><strong>Role:</strong> <span id="currentRole"></span></p>
</div>
```

### Create User Tab
Enhanced form with:
- Username (required)
- Email (required)
- Password (required)
- Full Name (required)
- Role dropdown (required)
- Pharmacy ID field (conditional, required for pharmacy_staff)
- Facility ID field (conditional, required for facility_manager)

### Clients List Tab
Enhanced with:
- Refresh button
- Status filter dropdown
- Grid layout for client cards
- Each client card shows all relevant information
- Edit button (opens modal)
- Delete button (with confirmation)

### Edit Client Modal
Professional modal dialog featuring:
- Modal header with close button
- Organized form fields in a grid
- All client details editable
- Cancel and Save buttons
- Form validation

---

## CSS Styling

### New Classes Added
```css
.client-actions { }          /* Container for edit/delete buttons */
.btn-edit { }                /* Green edit button */
.btn-delete { }              /* Red delete button */
.modal { }                   /* Modal overlay */
.modal.active { }            /* Show modal */
.modal-content { }           /* Modal dialog box */
.modal-header { }            /* Modal header section */
.modal-close { }             /* Close button styling */
```

### Responsive Design
- Modal works on all screen sizes
- Client list cards stack responsively
- Form grid adapts to smaller screens
- Touch-friendly buttons (44px+ minimum height)

---

## JavaScript Functions

### New Functions Added

#### updateRoleDependentFields()
Shows/hides Pharmacy/Facility ID fields based on selected role
```javascript
function updateRoleDependentFields() {
    const role = document.getElementById('userRole').value;
    // Show/hide fields and set required attributes
}
```

#### openEditModal(clientId)
Fetches client data and opens edit modal
```javascript
function openEditModal(clientId) {
    // Fetch client data and populate form
}
```

#### closeEditModal()
Closes the edit modal
```javascript
function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
}
```

#### saveClientChanges(event)
Sends PUT request to update client
```javascript
async function saveClientChanges(event) {
    // Validate form and send update
}
```

#### deleteClient(clientId, clientName)
Requests confirmation and deletes client via DELETE endpoint
```javascript
async function deleteClient(clientId, clientName) {
    // Request confirmation and delete
}
```

---

## Backend Changes Summary

### Updated Files

#### 1. auth.js
- Enhanced signup endpoint to accept and validate pharmacy_id/facility_id
- Updated login response to include pharmacyId and facilityId

#### 2. clients.js
- **GET /:clientId**: Returns formatted client object with proper field mapping
- **PUT /:clientId**: 
  - Handles field name mapping (name → full_name, etc.)
  - Supports facility/pharmacy record creation
  - Implements authorization checks
  - Returns formatted response
- **DELETE /:clientId**: 
  - Added authorization checks for pharmacy_staff and facility_manager
  - Allows deletion of own clients only (unless admin)

#### 3. middleware/auth.js
- Existing authorization middleware remains functional
- New authorization checks added to client routes

---

## Data Flow Diagram

### User Creation Flow
```
User fills Create User form
    ↓
Role selected (pharmacy_staff/facility_manager/admin)
    ↓
Pharmacy/Facility ID fields shown/required
    ↓
POST /api/auth/signup
    ↓
Backend creates User with pharmacy_id/facility_id
    ↓
User can now login
```

### Client Management Flow
```
User logs in
    ↓
Auth token obtained with pharmacyId/facilityId
    ↓
Load Clients List
    ↓
Frontend filters: GET /api/clients?pharmacyCode=XXX
    ↓
Backend applies authorization
    ↓
Display only user's clients
    ↓
User clicks Edit on a client
    ↓
Modal opens, client data loaded
    ↓
User updates fields
    ↓
PUT /api/clients/:clientId
    ↓
Backend authorizes and updates
    ↓
Client list refreshes
```

---

## Testing Checklist

- [ ] Login with admin account
- [ ] Create new pharmacy_staff user with Pharmacy ID
- [ ] Create new facility_manager user with Facility ID
- [ ] Try to create pharmacy_staff without Pharmacy ID (should fail)
- [ ] Try to create facility_manager without Facility ID (should fail)
- [ ] Login as pharmacy_staff user
- [ ] View clients list (should only see own pharmacy's clients)
- [ ] Edit a client (should succeed)
- [ ] Try to delete client (should work with confirmation)
- [ ] Login as facility_manager user
- [ ] View clients list (should only see own facility's clients)
- [ ] Edit a client (should succeed)
- [ ] Try to edit client from different facility (should fail)
- [ ] Login as admin user
- [ ] View all clients regardless of facility/pharmacy
- [ ] Edit any client (should succeed)

---

## Security Notes

⚠️ **Important Security Considerations:**

1. **Pharmacy/Facility ID Validation**: Current implementation trusts the entered IDs. Consider:
   - Pre-populated dropdown of existing facilities/pharmacies
   - Validation against a master list
   - Role-based restrictions on which facilities/pharmacies can be selected

2. **Token Security**: JWTs are stored in localStorage
   - Consider upgrading to secure HttpOnly cookies
   - Add token refresh mechanism
   - Implement token revocation on logout

3. **Authorization Checks**: Always verify on the backend
   - Current implementation checks user role and facility/pharmacy
   - Consider additional checks for sensitive operations
   - Add audit logging for client modifications

4. **CORS & CSP**: Check your Content Security Policy headers
   - Ensure API calls are properly authenticated
   - Validate request origins

---

## Future Enhancements

1. **Multi-facility/Pharmacy Users**: Allow one user to manage multiple facilities/pharmacies
2. **Permission Management**: Fine-grained permissions (read-only, modify forms, etc.)
3. **User Audit Trail**: Log all user actions for compliance
4. **Batch Operations**: Edit multiple clients at once
5. **Client Export**: Export client list to CSV/Excel
6. **Client Search/Filter**: Advanced search by name, PEPFAR ID, phone, etc.
7. **Assigned Facilities/Pharmacies Management**: UI for assigning clients to facilities/pharmacies
8. **User Management Interface**: CRUD for users in the web UI
9. **Two-Factor Authentication**: For enhanced security
10. **Activity Dashboard**: Show recent activities and statistics

---

## Troubleshooting

### Issue: "You can only edit clients in your pharmacy" error
**Solution**: Ensure you're logged in as the correct user and the client belongs to your pharmacy/facility

### Issue: Modal doesn't open when clicking Edit
**Solution**: Check browser console for JavaScript errors. Ensure client ID is being passed correctly

### Issue: Delete button doesn't work
**Solution**: 
- Verify user has permission (admin, or owns the client's pharmacy/facility)
- Check network tab in developer tools for API error response
- Clear browser cache and reload

### Issue: Clients list is empty for pharmacy_staff user
**Solution**:
- Verify the pharmacy_id matches exactly (case-sensitive)
- Check that clients are actually assigned to that pharmacy
- Verify the user was created with the correct pharmacy_id

---

## API Documentation Reference

All endpoints require authentication via JWT token in Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Base URL
```
http://localhost:3001/api
```

### Authentication Endpoints
- POST `/auth/login` - Login and get token
- POST `/auth/signup` - Create new user (admin only)
- POST `/auth/verify` - Verify token validity

### Client Endpoints
- GET `/clients` - List clients (filtered by user role)
- GET `/clients/:clientId` - Get single client
- POST `/clients` - Create client
- PUT `/clients/:clientId` - Update client
- DELETE `/clients/:clientId` - Delete client
- GET `/clients?pharmacyCode=X` - Filter by pharmacy
- GET `/clients?facilityId=X` - Filter by facility

---

## Deployment Notes

1. Ensure `.env` file has JWT_SECRET set to a strong value
2. Update CORS settings if deploying to production
3. Consider using HTTPS instead of HTTP
4. Set up proper database backups
5. Configure proper logging for audit trails
6. Test all role-based access controls before going live
7. Notify users about new password requirements during signup

