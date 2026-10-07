# Backend Database Information

## React Backend Server Database Configuration

### Active Database: MySQL
Located at: `/react-backend-server/.env`

```
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=pharmacy_sync
DB_USER=root
DB_PASSWORD=root
```

### What the Backend Uses
The React backend server uses **MySQL** (not SQLite), specifically configured with:
- Dialect: MySQL
- Host: localhost
- Port: 3306
- Database: `pharmacy_sync`

### User Management
**Default Admin User:**
- Username: `superadmin`
- Email: `super@compharm.org`
- Password: `@@ComPharm22`
- Role: `admin`

**Pharmacy Staff User (for Python App):**
- Username: `jlambu`
- Email: `p1@compharm.org`
- Password: `please22` (newly updated)
- Role: `pharmacy_staff`
- Pharmacy ID: `p1`

### Database Tables
- `users` - Application users
- `pharmacies` - Pharmacy records
- `facilities` - Facility records
- `clients` - Client/patient records
- `pharmacy_forms` - Form templates
- `form_submissions` - Form submission data
- And other sync/audit tables

## Important Note
⚠️ **Do NOT use the SQLite database file (`pharmacy_sync_backend.db`) for user management!**
The SQLite file is likely a legacy/backup file. All active data is stored in MySQL.

### User Updates
When updating user credentials, passwords, or roles:
1. Connect to MySQL directly OR
2. Use the API endpoints (POST /api/users, PUT /api/users/:userId)
3. Do NOT manually edit the SQLite database

## Verification Commands
To verify your setup is correct:

```bash
# Check MySQL is running
netstat -ano | findstr 3306

# View database
mysql -h localhost -u root -p root pharmacy_sync

# Check user
SELECT username, email, role FROM users WHERE username='jlambu';
```
