"""
Simple verification that the 403 fix works
"""

import requests
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import Settings

def verify_403_fix():
    """Verify that the 403 Admin access error is fixed"""
    
    settings = Settings()
    api_url = settings.CENTRAL_SERVER_URL
    
    print("="*60)
    print("VERIFYING 403 ADMIN ACCESS FIX")
    print("="*60)
    
    # Step 1: Login
    print("\n[1] Logging in as super@compharm.org...")
    response = requests.post(
        f"{api_url}/api/auth/login",
        json={
            "email": "super@compharm.org",
            "password": "@@ComPharm22"
        },
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"[FAIL] Login failed: {response.status_code}")
        return False
    
    data = response.json()
    token = data.get('token')
    print(f"[PASS] Login successful. Token obtained.")
    
    # Step 2: Call /api/users with token
    print("\n[2] Calling /api/users endpoint...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{api_url}/api/users",
        headers=headers,
        timeout=10
    )
    
    print(f"    Response status: {response.status_code}")
    
    if response.status_code == 200:
        users = response.json().get('users', [])
        print(f"[PASS] Successfully retrieved {len(users)} users!")
        print("\n    Users:")
        for user in users:
            print(f"      - {user['email']} ({user['role']})")
        return True
    elif response.status_code == 403:
        print(f"[FAIL] Got 403 Forbidden - Admin access fix did NOT work")
        print(f"    Response: {response.json()}")
        return False
    else:
        print(f"[FAIL] Unexpected status code: {response.status_code}")
        print(f"    Response: {response.json()}")
        return False


if __name__ == "__main__":
    try:
        success = verify_403_fix()
        
        print("\n" + "="*60)
        if success:
            print("SUCCESS! The 403 Admin access error is FIXED!")
            print("The super admin can now access the /api/users endpoint.")
            print("="*60)
            sys.exit(0)
        else:
            print("FAILURE! The issue persists.")
            print("="*60)
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
