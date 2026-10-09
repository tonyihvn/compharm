"""
Test script to verify the 403 Admin access fix
Tests the complete flow: login -> get token -> call /api/users
"""

import requests
import json
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from api.backend_client import BackendAPIClient
from config.settings import Settings

def test_backend_login():
    """Test login to backend and verify token"""
    print("\n" + "="*60)
    print("TEST 1: Backend Login & Token Generation")
    print("="*60)
    
    settings = Settings()
    api_url = settings.CENTRAL_SERVER_URL
    
    try:
        response = requests.post(
            f"{api_url}/api/auth/login",
            json={
                "email": "super@compharm.org",
                "password": "@@ComPharm22"
            },
            timeout=10
        )
        
        print(f"Login response status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print("[PASS] Login successful")
            token = data.get('token')
            user_info = data.get('user', {})
            
            print(f"[OK] Token received: {token[:20]}...")
            print(f"[OK] User: {user_info.get('email')} ({user_info.get('role')})")
            
            return token
        else:
            print(f"[FAIL] Login failed: {data}")
            return None
            
    except Exception as e:
        print(f"[ERROR] Login error: {str(e)}")
        return None


def test_api_users_endpoint(token):
    """Test /api/users endpoint with Bearer token"""
    print("\n" + "="*60)
    print("TEST 2: Call /api/users Endpoint")
    print("="*60)
    
    settings = Settings()
    api_url = settings.CENTRAL_SERVER_URL
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{api_url}/api/users",
            headers=headers,
            timeout=10
        )
        
        print(f"API response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"[PASS] Retrieved {len(users)} users")
            
            for user in users:
                print(f"  - {user.get('email')} ({user.get('role')})")
            
            return True
        elif response.status_code == 403:
            print("[FAIL] Got 403 Forbidden error")
            print(f"Response: {response.json()}")
            return False
        else:
            print(f"[FAIL] Unexpected status code: {response.status_code}")
            print(f"Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"[ERROR] API call error: {str(e)}")
        return False


def test_backend_api_client():
    """Test using the BackendAPIClient class"""
    print("\n" + "="*60)
    print("TEST 3: BackendAPIClient Login & Auth")
    print("="*60)
    
    try:
        api_client = BackendAPIClient()
        
        # Test authentication
        print("Attempting authentication...")
        if api_client.authenticate():
            print("[PASS] Authentication successful")
            print(f"[OK] Token set: {api_client.auth_token[:20] if api_client.auth_token else 'None'}...")
            
            # Test calling the users endpoint
            print("\nCalling /api/users...")
            users = api_client.get('/api/users')
            
            if users:
                print("[PASS] Retrieved users successfully")
                if 'users' in users:
                    print(f"  Total users: {len(users['users'])}")
                return True
            else:
                print("[FAIL] Failed to retrieve users")
                return False
        else:
            print("[FAIL] Authentication failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] BackendAPIClient error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("TESTING 403 ADMIN ACCESS FIX")
    print("="*60)
    
    results = []
    
    # Test 1: Direct backend login
    token = test_backend_login()
    results.append(("Backend Login", token is not None))
    
    if token:
        # Test 2: Call API with token
        api_success = test_api_users_endpoint(token)
        results.append(("API /users Call", api_success))
    
    # Test 3: BackendAPIClient
    client_success = test_backend_api_client()
    results.append(("BackendAPIClient", client_success))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n✓ ALL TESTS PASSED - 403 ERROR IS FIXED!")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED - ISSUE PERSISTS")
        return 1


if __name__ == "__main__":
    sys.exit(main())
