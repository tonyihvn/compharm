# Testing Guide: User Management & Role-Based Access Control

## Prerequisites
- React Backend Server running on `http://localhost:3001`
- Database initialized with tables
- Admin account credentials: `super@compharm.org` / `@@ComPharm22`

---

## Test Scenario 1: Create Pharmacy Staff User

### Step 1: Login to Dashboard
1. Navigate to `http://localhost:3001`
2. Enter credentials:
   - Email: `super@compharm.org`
   - Password: `@@ComPharm22`
3. Click "Login"

**Expected Result:** ✅ Dashboard loads with admin privileges

### Step 2: Navigate to Create User Tab
1. Click on "Create User" tab
2. Observe that the form shows:
   - Username field
   - Email field
   - Password field
   - Full Name field
   - Role dropdown

**Expected Result:** ✅ Form displays with all fields

### Step 3: Fill User Form for Pharmacy Staff
1. Fill in the form:
   - Username: `pharmastaff_ikoyi_01`
   - Email: `pharmastaff.ikoyi@compharm.org`
   - Password: `StaffPass123!`
   - Full Name: `Olawale Pharmacy Manager`
   - Role: Select "Pharmacy Staff"

2. After selecting "Pharmacy Staff", observe:
   - A new field "Pharmacy ID" appears
   - The field is marked as required (red asterisk)
   - Facility ID field remains hidden

**Expected Result:** ✅ Pharmacy ID field appears dynamically

### Step 4: Enter Pharmacy ID
1. In the Pharmacy ID field, enter: `PHARM-IKOYI-001`
2. Click "Create User"

**Expected Result:** ✅ Success message: "User created successfully!"

---

## Test Scenario 2: Create Facility Manager User

### Step 1: Still on Create User Tab
1. Reset the form (it should have auto-cleared after successful creation)
2. Fill in the form:
   - Username: `facilitymanager_lagos_01`
   - Email: `facility.lagos@compharm.org`
   - Password: `FacilityPass123!`
   - Full Name: `Dr. Adeyemi Facility Manager`
   - Role: Select "Facility Manager"

3. After selecting "Facility Manager", observe:
   - Pharmacy ID field disappears/hides
   - A new field "Facility ID" appears
   - The field is marked as required (red asterisk)

**Expected Result:** ✅ Facility ID field appears, Pharmacy ID hides

### Step 2: Enter Facility ID
1. In the Facility ID field, enter: `FAC-LAGOS-001`
2. Click "Create User"

**Expected Result:** ✅ Success message: "User created successfully!"

---

## Test Scenario 3: Create Client and Test Filtering

### Step 1: Navigate to Create Client Tab
1. Click on "Create Client" tab
2. Fill in client details:
   - Client Name: `Temitope Adebayo`
   - PEPFAR ID: `PEPFAR-2024-LAG-001`
   - Facility ID: `FAC-LAGOS-001`
   - Pharmacy ID: `PHARM-IKOYI-001`
   - Age: `28`
   - Gender: `M`
   - Phone: `+234-123-4567`
   - Email: `temitope@example.com`
   - Address: `Lagos State, Nigeria`
3. Click "Create Client"

**Expected Result:** ✅ Success message: "Client created successfully!"

### Step 2: Create Second Client
1. Create another client:
   - Client Name: `Funmi Okafor`
   - PEPFAR ID: `PEPFAR-2024-IBD-002`
   - Facility ID: `FAC-IBADAN-001`
   - Pharmacy ID: `PHARM-IBADAN-001`
   - (Fill other fields as needed)
2. Click "Create Client"

**Expected Result:** ✅ Second client created

### Step 3: View Clients List (as Admin)
1. Click on "Clients List" tab
2. Observe:
   - Both clients are displayed (admin sees all)
   - Each client shows: Name, PEPFAR ID, Facility, Pharmacy, Age, Gender, Phone, Email, Address
   - Each client has "Edit" and "Delete" buttons

**Expected Result:** ✅ Both clients visible with action buttons

---

## Test Scenario 4: Test Pharmacy Staff User Filtering

### Step 1: Logout from Admin Account
1. Click "Logout" button
2. Confirm logout

**Expected Result:** ✅ Back to login page

### Step 2: Login as Pharmacy Staff
1. Enter credentials:
   - Email: `pharmastaff.ikoyi@compharm.org`
   - Password: `StaffPass123!`
2. Click "Login"

**Expected Result:** ✅ Dashboard loads showing:
- User: `pharmastaff.ikoyi@compharm.org`
- Role: `pharmacy_staff`

### Step 3: View Clients List (as Pharmacy Staff)
1. Click on "Clients List" tab
2. Observe:
   - Only Temitope Adebayo client is shown (assigned to PHARM-IKOYI-001)
   - Funmi Okafor is NOT shown (assigned to PHARM-IBADAN-001)
   - Edit and Delete buttons are available

**Expected Result:** ✅ Only clients from own pharmacy shown

### Step 4: Test Edit Client
1. Click "Edit" button on Temitope's record
2. Modal dialog opens showing all client details:
   - Client Name field is pre-filled
   - PEPFAR ID is pre-filled
   - All other fields match the created client
3. Modify a field:
   - Change phone to: `+234-987-6543`
4. Click "Save Changes"

**Expected Result:** ✅ Success message and modal closes, client list refreshes with updated data

### Step 5: Test Delete Attempt (Different Pharmacy)
1. Try to navigate to another client (if exists in different pharmacy)
2. Expected behavior: Cannot delete due to authorization

**Expected Result:** ✅ Authorization check prevents unauthorized deletion (if implemented)

### Step 6: Test Delete Current Client
1. Click "Delete" button on Temitope's record
2. Confirmation dialog appears asking: "Are you sure you want to delete Temitope Adebayo?"
3. Click "OK"

**Expected Result:** ✅ Client deleted, list refreshes, no longer shows that client

---

## Test Scenario 5: Test Facility Manager Role

### Step 1: Logout Pharmacy Staff
1. Click "Logout"

**Expected Result:** ✅ Back to login

### Step 2: Login as Facility Manager
1. Enter credentials:
   - Email: `facility.lagos@compharm.org`
   - Password: `FacilityPass123!`
2. Click "Login"

**Expected Result:** ✅ Dashboard loads showing:
- User: `facility.lagos@compharm.org`
- Role: `facility_manager`

### Step 3: View Clients List (as Facility Manager)
1. Click on "Clients List" tab
2. Observe:
   - Only clients from FAC-LAGOS-001 are shown
   - Clients from other facilities are filtered out
   - Can edit/delete only own facility clients

**Expected Result:** ✅ Facility-based filtering works correctly

---

## Test Scenario 6: Verify Role-Based Access Control

### Backend API Test (Using curl or Postman)

#### 6.1 Create User Without Required Field
**Request:**
```bash
curl -X POST http://localhost:3001/api/auth/signup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_token>" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User",
    "role": "pharmacy_staff"
    # Missing pharmacy_id!
  }'
```

**Expected Result:** ✅ Error on frontend validation: "Pharmacy ID is required for Pharmacy Staff"

#### 6.2 Update Client from Different Pharmacy
**Request:**
```bash
curl -X PUT http://localhost:3001/api/clients/{client_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <pharmastaff_token>" \
  -d '{
    "name": "Updated Name"
  }'
```

**Expected Result:** ✅ If client not in user's pharmacy:
```json
{
  "message": "You can only edit clients in your pharmacy"
}
```
Status: 403 Forbidden

#### 6.3 Delete Client from Different Pharmacy
**Request:**
```bash
curl -X DELETE http://localhost:3001/api/clients/{client_id} \
  -H "Authorization: Bearer <pharmastaff_token>"
```

**Expected Result:** ✅ If client not in user's pharmacy:
```json
{
  "message": "You can only delete clients in your pharmacy"
}
```
Status: 403 Forbidden

---

## Test Scenario 7: Admin Override

### Step 1: Login as Admin
1. Logout current user
2. Login as admin: `super@compharm.org` / `@@ComPharm22`

### Step 2: Access All Clients
1. Go to "Clients List"
2. Observe: All clients from all facilities/pharmacies are visible

**Expected Result:** ✅ Admin sees all clients regardless of facility/pharmacy

### Step 3: Edit Any Client
1. Select any client and click Edit
2. Modify and save

**Expected Result:** ✅ Admin can edit any client

### Step 4: Delete Any Client
1. Select any client and click Delete
2. Confirm deletion

**Expected Result:** ✅ Admin can delete any client

---

## Test Scenario 8: Form Validation

### Pharmacy Staff Creation Validation
1. Go to Create User tab
2. Select "Pharmacy Staff" role
3. Try to click "Create User" WITHOUT filling Pharmacy ID
4. Check if form prevents submission

**Expected Result:** ✅ Form shows validation error or prevents submission

### Client Creation Validation
1. Go to Create Client tab
2. Try to submit with empty required fields
3. Observe browser validation

**Expected Result:** ✅ Required fields are marked and validated

---

## Common Issues & Troubleshooting

### Issue: Role-dependent fields don't show/hide
**Troubleshooting:**
1. Check browser console (F12) for JavaScript errors
2. Verify `updateRoleDependentFields()` function is called
3. Clear browser cache and reload

### Issue: Modal doesn't open when clicking Edit
**Troubleshooting:**
1. Check browser console for errors
2. Verify client ID is being passed to `openEditModal()`
3. Check that API call to GET `/api/clients/{id}` succeeds

### Issue: Clients list shows all clients even for pharmacy_staff
**Troubleshooting:**
1. Verify user was created with correct pharmacy_id
2. Check that token contains pharmacyId
3. Verify clients were created with correct pharmacy_id
4. Check network requests to see if filter query is being sent

### Issue: Edit/Delete buttons show but don't work
**Troubleshooting:**
1. Check browser console for JavaScript errors
2. Verify auth token is present
3. Check network tab for API errors (403, 404, etc.)
4. Verify user has permission for that client

### Issue: Can't create pharmacy_staff user
**Troubleshooting:**
1. Verify you're logged in as admin
2. Check that Pharmacy ID field is filled
3. Check browser console for validation errors
4. Verify auth token is valid

---

## Success Criteria

All of the following must be true for implementation to be successful:

- ✅ Create User form shows role-dependent fields
- ✅ Pharmacy Staff user created with Pharmacy ID
- ✅ Facility Manager user created with Facility ID
- ✅ Pharmacy Staff sees only own pharmacy's clients
- ✅ Facility Manager sees only own facility's clients
- ✅ Admin sees all clients
- ✅ Edit client modal opens and updates work
- ✅ Delete client with confirmation works
- ✅ Authorization prevents unauthorized edits (403 errors)
- ✅ Form validation works correctly
- ✅ All error messages are clear and helpful

---

## Notes for Users

### Best Practices
1. Always use consistent Pharmacy/Facility IDs across your system
2. Ensure clinic/facility codes match the IDs you use when creating users
3. Test thoroughly with multiple users before going to production
4. Keep user credentials secure and change default passwords

### Security Reminders
1. Change default admin password in production
2. Don't share auth tokens
3. Logout when done using the system
4. Report any suspicious access attempts
5. Keep browser and system updated

---

## Quick Reference: Default Credentials

| Role | Username | Email | Password |
|------|----------|-------|----------|
| Admin | admin | super@compharm.org | @@ComPharm22 |
| Pharmacy Staff (Test) | pharmastaff_ikoyi_01 | pharmastaff.ikoyi@compharm.org | StaffPass123! |
| Facility Manager (Test) | facilitymanager_lagos_01 | facility.lagos@compharm.org | FacilityPass123! |

**⚠️ Change these credentials in production!**

