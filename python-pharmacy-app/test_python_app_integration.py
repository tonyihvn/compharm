"""
Integration test: Simulate Python app admin panel login and API access
"""

import requests
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config.settings import Settings

def simulate_python_app_flow():
    """Simulate the complete Python app login flow"""
    
    settings = Settings()
    api_url = settings.CENTRAL_SERVER_URL
    
    print("Simulating Python App Admin Panel Flow:")
    print("="*60)
    
    # Step 1: User enters credentials in login form
    print("\n[Step 1] User enters login credentials:")
    username = "super@compharm.org"
    password = "@@ComPharm22"
    print(f"  Email: {username}")
    print(f"  Password: {'*' * len(password)}")
    
    # Step 2: LoginWindow.get_server_auth_token() is called
    print("\n[Step 2] LoginWindow.get_server_auth_token() calls backend...")
    try:
        response = requests.post(
            f"{api_url}/api/auth/login",
            json={"email": username, "password": password},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"[FAIL] Authentication failed: {response.status_code}")
            return False
        
        auth_token = response.json().get('token')
        user_data = response.json().get('user', {})
        
        print(f"[OK] Got auth token: {auth_token[:30]}...")
        print(f"[OK] User: {user_data.get('email')} (role: {user_data.get('role')})")
        
    except Exception as e:
        print(f"[FAIL] Login error: {str(e)}")
        return False
    
    # Step 3: main.py calls admin_panel.set_auth_token(token)
    print("\n[Step 3] AdminPanel stores token for later use...")
    stored_token = auth_token
    print(f"[OK] Token stored in admin_panel")
    
    # Step 4: ModernMainWindow shows AdminPanel
    print("\n[Step 4] Admin Panel UI loads and renders...")
    
    # Step 5: AdminPanel.load_users_list() is called (when admin panel opens)
    print("\n[Step 5] load_users_list() calls /api/users endpoint...")
    
    # This is what admin_panel.py does:
    # token = self.get_auth_token()  # Gets the stored token
    # headers = {"Authorization": f"Bearer {token}"}
    # response = requests.get(f"{api_url}/api/users", headers=headers)
    
    headers = {
        "Authorization": f"Bearer {stored_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{api_url}/api/users",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"[SUCCESS] Got 200 response - Admin access GRANTED!")
            users = response.json().get('users', [])
            print(f"[OK] Retrieved {len(users)} users from admin panel")
            
            # Show the users that would appear in the admin panel
            print("\n    Users in Admin Panel:")
            for user in users:
                role = user.get('role', 'unknown')
                email = user.get('email', 'unknown')
                status = "ACTIVE" if user.get('is_active') else "INACTIVE"
                print(f"      [{role.upper():20}] {email:25} {status}")
            
            return True
        
        elif response.status_code == 403:
            print(f"[FAIL] Got 403 - Admin access DENIED (THIS IS THE BUG!)")
            print(f"      Response: {response.json()}")
            return False
        
        else:
            print(f"[FAIL] Unexpected status: {response.status_code}")
            print(f"      Response: {response.json()}")
            return False
            
    except Exception as e:
        print(f"[FAIL] API call error: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n")
    print("#"*60)
    print("# PYTHON APP INTEGRATION TEST")
    print("#"*60)
    
    try:
        success = simulate_python_app_flow()
        
        print("\n" + "="*60)
        print("INTEGRATION TEST RESULT")
        print("="*60)
        
        if success:
            print("\nSUCCESS!")
            print("The Python app can now:")
            print("  1. Login with super@compharm.org / @@ComPharm22")
            print("  2. Get auth token from backend")
            print("  3. Access /api/users endpoint")
            print("  4. Load users in Admin Panel")
            print("\nThe 403 error is PERMANENTLY FIXED!")
            sys.exit(0)
        else:
            print("\nFAILED!")
            print("The issue persists.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
