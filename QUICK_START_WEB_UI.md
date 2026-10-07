# Quick Start - Access ComPharm Web UI

## ✅ Current Status

The backend server is **running and fully operational** on port 3001 with MySQL database.

## 🚀 How to Access the Web Interface

### Step 1: Open Your Browser

Open any modern web browser (Chrome, Firefox, Safari, Edge) and navigate to:

```
http://localhost:3001
```

### Step 2: Login

Use these credentials:

| Field | Value |
|-------|-------|
| **Email** | `super@compharm.org` |
| **Password** | `@@ComPharm22` |

⚠️ **Important:** Note the double `@@` symbols in the password

### Step 3: Explore the Dashboard

After login, you'll see:

- **Dashboard** - Overview with statistics
- **Clients** - Manage patient records
- **Users** - Manage system users
- **Fields** - Configure form fields

## 📋 What You Can Do

### Create a Client

1. Navigate to **Clients** tab
2. Click **Add Client** button
3. Fill in the form:
   - **PEPFAR ID** (e.g., EP001)
   - **Full Name**
   - **Date of Birth**
   - **Gender**
   - **Facility ID** (must exist)
   - **Pharmacy ID** (e.g., P1)
   - Other optional fields

4. Click **Save**

### Create a Pharmacy

1. Navigate to **Pharmacies** (if available)
2. Click **Add Pharmacy**
3. Fill in:
   - **Pharmacy Code** (e.g., P1)
   - **Pharmacy Name**
   - **Address**
   - **Phone**
   - **Email**

4. Click **Save**

### Create a Facility

1. Navigate to **Facilities** (if available)
2. Click **Add Facility**
3. Fill in:
   - **Facility Code**
   - **Facility Name**
   - **System Type** (e.g., openmrs)
   - **Address**

4. Click **Save**

## 🔌 Test API Directly

You can also test the API using curl or Postman:

### Login via API

```bash
curl -X POST http://localhost:3001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"super@compharm.org","password":"@@ComPharm22"}'
```

### Response (with token):

```json
{
  "message": "Login successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "39870782-dbc6-48c1-92a9-f55d398ae222",
    "username": "superadmin",
    "email": "super@compharm.org",
    "role": "admin"
  }
}
```

### Get Clients

```bash
curl -X GET http://localhost:3001/api/clients \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Create Client via API

```bash
curl -X POST http://localhost:3001/api/clients \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "pepfarId": "EP001",
    "fullName": "John Doe",
    "facilityId": "FAC001",
    "pharmacyId": "P1",
    "gender": "M",
    "dateOfBirth": "1990-01-15"
  }'
```

## 📊 Verify Backend Connectivity

### Check Server Health

```bash
curl http://localhost:3001/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-10-07T10:15:00.000Z",
  "version": "1.0.0"
}
```

### Check Database Connection

The server will log database connection on startup:
```
Database connection established
Database models synchronized
Server is running on port 3001
```

## 🔗 Integration with Python App

Once you've created clients in the web UI:

1. **Set Pharmacy ID** in Python App (System Settings)
2. **Click "Sync Now"** in Admin Panel
3. **View synced clients** in the Clients View
4. **Forms** can be uploaded and filled by clients

## 🛠️ Troubleshooting

### Can't access http://localhost:3001

**Possible causes:**
- Backend server not running
- Port 3001 already in use
- Firewall blocking connection

**Solution:**
1. Check if server is running: `npm start` in react-backend-server/
2. Check port: `netstat -an | findstr 3001`
3. Try http://127.0.0.1:3001 instead

### Login shows error

**Possible causes:**
- Wrong password (check double @@)
- Database not initialized
- User not created

**Solution:**
1. Verify password is exactly: `@@ComPharm22`
2. Check server logs for errors
3. Restart server with clean database

### Clients not showing after creation

**Possible causes:**
- Facility or Pharmacy doesn't exist
- Browser cache issue
- API error

**Solution:**
1. Create Facility and Pharmacy first
2. Hard refresh browser (Ctrl+F5 or Cmd+Shift+R)
3. Check browser console for errors
4. Test API directly with curl

## 📱 Mobile Access

You can access the web UI from other devices:

Replace `localhost` with your computer's IP address:

```
http://YOUR_IP:3001
```

Example: `http://192.168.1.100:3001`

## 🔒 Security Notes

⚠️ **For Development Only**

The default credentials and configuration are for development/testing:
- Default password is simple and should be changed
- CORS is enabled for all origins
- Database password is in plain text
- No HTTPS configured

Before production deployment:
1. Change default admin password
2. Set strict CORS policies
3. Use environment variables for secrets
4. Enable HTTPS
5. Set up proper backups
6. Review security headers

## 📞 API Documentation

### Headers Required

Most API endpoints require authentication:

```
Authorization: Bearer <token>
X-Pharmacy-ID: <pharmacy_id>
X-Facility-ID: <facility_id>
```

### Response Format

All API responses follow this format:

```json
{
  "message": "Success description",
  "data": {},
  "error": null,
  "timestamp": "2026-10-07T10:15:00.000Z"
}
```

## ✨ Next Steps

1. ✅ Access http://localhost:3001 in your browser
2. ✅ Login with super@compharm.org / @@ComPharm22
3. ✅ Create test Facilities and Pharmacies
4. ✅ Create test Clients
5. ✅ Configure Python App with PharmacyID
6. ✅ Test sync functionality

**Happy using ComPharm! 🎉**

---

**Backend Server Status:** ✅ Running on http://localhost:3001
**Database:** ✅ MySQL connected (pharmacy_sync)
**API:** ✅ All endpoints operational
**Auth:** ✅ Working correctly
