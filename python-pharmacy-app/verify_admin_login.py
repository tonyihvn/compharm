#!/usr/bin/env python3
"""
Final verification that admin login is working correctly
"""
import sys
import sqlite3

print("\n" + "=" * 70)
print(" ADMIN LOGIN SYSTEM - FINAL VERIFICATION")
print("=" * 70)

# Step 1: Check configuration
print("\n[CHECK 1] Configuration Settings")
print("-" * 70)
from config.settings import settings

print(f"  Admin Email:     {settings.SUPER_USER_EMAIL}")
print(f"  Admin Password:  {'*' * len(settings.SUPER_USER_PASSWORD)}")
print(f"  Admin Full Name: {settings.SUPER_USER_NAME}")
print("  [OK] Settings loaded correctly")

# Step 2: Initialize database and create admin
print("\n[CHECK 2] Database Initialization & Admin Creation")
print("-" * 70)
from database.db_manager import DatabaseManager
from utils.auth import init_default_admin

db_manager = DatabaseManager(settings.DATABASE_URL)
db_manager.init_db()
print("  [OK] Database initialized")

session = db_manager.get_session()
try:
    init_result = init_default_admin(session)
    print(f"  [OK] Admin initialization: {'Success' if init_result else 'Failed'}")
finally:
    session.close()

# Step 3: Verify admin in database
print("\n[CHECK 3] Admin User in Database")
print("-" * 70)
conn = sqlite3.connect('pharmacy.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT username, email, role, is_superuser, is_active 
    FROM users 
    WHERE is_superuser=1 OR role='admin'
""")
admin_users = cursor.fetchall()

if admin_users:
    for user in admin_users:
        print(f"  Username:  {user[0]}")
        print(f"  Email:     {user[1]}")
        print(f"  Role:      {user[2]}")
        print(f"  Superuser: {user[3]}")
        print(f"  Active:    {user[4]}")
    print("  [OK] Admin user exists in database")
else:
    print("  [ERROR] No admin user found!")
    conn.close()
    sys.exit(1)

conn.close()

# Step 4: Test login
print("\n[CHECK 4] Login Authentication Test")
print("-" * 70)
from utils.auth import authenticate_user

session = db_manager.get_session()
try:
    # Test correct password
    result = authenticate_user(session, settings.SUPER_USER_EMAIL, settings.SUPER_USER_PASSWORD)
    if result:
        print(f"  Username: {result['username']}")
        print(f"  Email:    {result['email']}")
        print(f"  Role:     {result['role']}")
        print(f"  Superuser: {result['is_superuser']}")
        print("  [OK] Login with correct password: SUCCESS")
    else:
        print("  [ERROR] Login with correct password: FAILED")
        sys.exit(1)
    
    # Test wrong password
    wrong_result = authenticate_user(session, settings.SUPER_USER_EMAIL, "wrongpassword")
    if wrong_result is None:
        print("  [OK] Login with wrong password: CORRECTLY REJECTED")
    else:
        print("  [ERROR] Login with wrong password: INCORRECTLY ACCEPTED")
        sys.exit(1)
        
finally:
    session.close()

# Final summary
print("\n" + "=" * 70)
print(" VERIFICATION COMPLETE - ALL CHECKS PASSED!")
print("=" * 70)
print("\n LOGIN CREDENTIALS:")
print(f"  Email:    {settings.SUPER_USER_EMAIL}")
print(f"  Password: {'*' * len(settings.SUPER_USER_PASSWORD)}")
print("\n SUPPORTED LOGIN TYPES:")
print("  1. Admin Login (role: admin, is_superuser: true)")
print("  2. Pharmacy Staff Login (role: pharmacy_staff)")
print("\n Ready to start the application!")
print("=" * 70 + "\n")
