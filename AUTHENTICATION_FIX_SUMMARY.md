# Authentication Fix Summary

## Issue
The Python app was failing to authenticate with the React backend server with the error:
```
Failed to authenticate with backend server: Invalid credentials
```

Even with the correct credentials (`jlambu` / `please22`) in the `.env` file.

## Root Cause
**The backend server was using MySQL, not SQLite**, but the password hash was being stored/updated in the SQLite database (`pharmacy_sync_backend.db`).

### Database Configuration
- **React Backend Server**: Uses **MySQL** (configured in `.env` with `DB_TYPE=mysql`)
  - Host: localhost
  - Port: 3306
  - Database: `pharmacy_sync`
  - User: root
  - Password: root

### What Was Happening
1. The Python app attempted to login with credentials `jlambu` / `please22`
2. The backend server looked up the user in MySQL and found them
3. The password stored in MySQL was hashed with a different hash than "please22"
4. bcrypt comparison failed: ❌ `false`
5. Authentication failed

## Solution
Generated a new bcrypt hash for the password "please22" and updated it in the **MySQL** database:

```sql
UPDATE users SET password_hash = '$2a$10$mQEwBPNsk7zXmEz.czzkNO6TURHXeFWP7GT44/GDQUjVHfV7B72k2' 
WHERE username = 'jlambu';
```

## Verification
After the fix, the authentication now works correctly:
- bcrypt comparison result: ✅ `true`
- User logged in successfully
- JWT token generated

## Configuration for Python App
Your `.env` file is correctly configured:
```
CENTRAL_SERVER_URL=http://localhost:3001
BACKEND_USERNAME=jlambu
BACKEND_PASSWORD=please22
PHARMACY_ID=p1
```

## Important Notes
1. **Make sure MySQL is running** - The backend server requires MySQL on localhost:3306
2. **Use `pharmacy_code` for PHARMACY_ID** - Not the UUID `id` field. In your case, "p1" is correct.
3. **Update credentials are now synchronized**:
   - Username: `jlambu`
   - Password: `please22`
   - Role: `pharmacy_staff`
   - Pharmacy ID: `p1`

## Testing
You can now run your Python app and it should successfully authenticate with the React backend server without the "Invalid credentials" error.
