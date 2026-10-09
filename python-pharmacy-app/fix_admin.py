#!/usr/bin/env python3
"""
Fix admin user login issue by reinitializing the admin with correct credentials
"""
import sys
import sqlite3
from pathlib import Path

# Check if database exists
db_path = Path("pharmacy.db")
if not db_path.exists():
    print("Database does not exist. It will be created on next app start.")
    sys.exit(0)

try:
    # Connect to database
    conn = sqlite3.connect("pharmacy.db")
    cursor = conn.cursor()
    
    # Check if user table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user';")
    if not cursor.fetchone():
        print("User table does not exist in database")
        sys.exit(0)
    
    # Check existing admin users
    cursor.execute("SELECT id, username, email, role, is_superuser FROM user WHERE is_superuser=1 OR role='admin';")
    admin_users = cursor.fetchall()
    
    if admin_users:
        print(f"Found {len(admin_users)} admin user(s):")
        for admin in admin_users:
            print(f"  ID: {admin[0]}, Username: {admin[1]}, Email: {admin[2]}, Role: {admin[3]}, Superuser: {admin[4]}")
        
        # Delete existing admin users to allow reinitialization
        print("\nDeleting existing admin users to allow reinitialization...")
        cursor.execute("DELETE FROM user WHERE is_superuser=1 OR role='admin';")
        conn.commit()
        print("✓ Admin users deleted. App will create new admin on next start.")
    else:
        print("No admin users found in database")
    
    # List all users
    cursor.execute("SELECT id, username, email, role, is_superuser, is_active FROM user;")
    all_users = cursor.fetchall()
    print(f"\nAll users in database ({len(all_users)} total):")
    for user in all_users:
        print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}, Superuser: {user[4]}, Active: {user[5]}")
    
    conn.close()
    print("\n✓ Database fix completed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
