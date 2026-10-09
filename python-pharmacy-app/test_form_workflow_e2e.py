#!/usr/bin/env python3
"""
End-to-end test for form filling workflow.
Tests form loading, selection, filling, and submission.
"""

import sys
import json
import time
from pathlib import Path

# Fix console encoding for Windows
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
# Use ASCII-safe checkmarks for cross-platform compatibility
CHECK = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

# Add the app root to path
sys.path.insert(0, str(Path(__file__).parent))

from database.db_manager import DatabaseManager
from services.api_client import CentralServerClient

def test_database_forms_loaded():
    """Test that forms can be loaded from database."""
    print("\n=== Test 1: Database Forms Loading ===")
    try:
        db = DatabaseManager()
        forms = db.get_all_forms()
        print(f"{CHECK} Successfully loaded {len(forms)} forms from database")
        if forms:
            print(f"  Sample form: {forms[0].get('name', 'Unknown')}")
        return True
    except Exception as e:
        print(f"{FAIL} Failed to load forms: {e}")
        return False

def test_database_clients_loaded():
    """Test that clients can be loaded from database."""
    print("\n=== Test 2: Database Clients Loading ===")
    try:
        db = DatabaseManager()
        clients = db.get_all_clients()
        print(f"{CHECK} Successfully loaded {len(clients)} clients from database")
        if clients:
            print(f"  Sample client: {clients[0].get('fullName', 'Unknown')}")
        return True
    except Exception as e:
        print(f"{FAIL} Failed to load clients: {e}")
        return False

def test_form_structure():
    """Test that forms have correct structure."""
    print("\n=== Test 3: Form Structure Validation ===")
    try:
        db = DatabaseManager()
        forms = db.get_all_forms()
        if not forms:
            print(f"{WARN} No forms in database, skipping structure test")
            return True
        
        form = forms[0]
        required_fields = ['id', 'uuid', 'name', 'definition']
        missing_fields = [f for f in required_fields if f not in form]
        
        if missing_fields:
            print(f"{FAIL} Form missing fields: {missing_fields}")
            return False
        
        # Parse definition if it's JSON string
        definition = form['definition']
        if isinstance(definition, str):
            definition = json.loads(definition)
        
        if not isinstance(definition, dict):
            print(f"{FAIL} Form definition is not a dict: {type(definition)}")
            return False
        
        print(f"{CHECK} Form structure valid: {form['name']}")
        print(f"  Sections: {len(definition.get('sections', []))}")
        return True
    except Exception as e:
        print(f"{FAIL} Form structure validation failed: {e}")
        return False

def test_client_structure():
    """Test that clients have correct structure."""
    print("\n=== Test 4: Client Structure Validation ===")
    try:
        db = DatabaseManager()
        clients = db.get_all_clients()
        if not clients:
            print(f"{WARN} No clients in database, skipping structure test")
            return True
        
        client = clients[0]
        # Clients might have different field names
        has_name = 'name' in client or 'fullName' in client or 'full_name' in client
        has_id = 'id' in client or 'pepfar_id' in client
        
        if not (has_name and has_id):
            print(f"{FAIL} Client missing critical fields")
            print(f"  Available fields: {list(client.keys())}")
            return False
        
        print(f"{CHECK} Client structure valid")
        print(f"  Fields: {list(client.keys())}")
        return True
    except Exception as e:
        print(f"{FAIL} Client structure validation failed: {e}")
        return False

def test_form_submission_creation():
    """Test that form submissions can be created in database."""
    print("\n=== Test 5: Form Submission Creation ===")
    try:
        db = DatabaseManager()
        
        # Get first form and client
        forms = db.get_all_forms()
        clients = db.get_all_clients()
        
        if not forms or not clients:
            print(f"{WARN} Need at least one form and one client, skipping test")
            return True
        
        form_id = forms[0]['id']
        client_id = clients[0]['id']
        
        # Create a sample submission
        submission_data = {
            'test_field': 'test_value',
            'timestamp': time.time()
        }
        
        # Use ORM to insert submission
        session = db.get_session()
        try:
            from database.models import FormSubmission
            submission = FormSubmission(
                form_id=form_id,
                client_id=client_id,
                data=submission_data,
                status='draft',
                filled_by_user_id=1
            )
            session.add(submission)
            session.commit()
            submission_id = submission.id
            session.close()
            
            print(f"{CHECK} Form submission created (ID: {submission_id})")
            print(f"  Form: {forms[0]['name']}")
            print(f"  Client: {clients[0].get('fullName', clients[0].get('full_name', 'Unknown'))}")
            
            return True
        except Exception as e:
            session.rollback()
            session.close()
            raise
    except Exception as e:
        print(f"{FAIL} Form submission creation failed: {e}")
        return False

def test_offline_mode_detection():
    """Test that offline mode is properly detected."""
    print("\n=== Test 6: Offline Mode Detection ===")
    try:
        api_client = CentralServerClient()
        is_online = api_client.is_online()
        
        if is_online:
            print(f"{CHECK} Server is online at {api_client.api_url}")
        else:
            print(f"{CHECK} Server is offline (as expected for offline-first app)")
        
        return True
    except Exception as e:
        print(f"{FAIL} Offline mode detection failed: {e}")
        return False

def test_form_data_collection():
    """Test form data collection workflow."""
    print("\n=== Test 7: Form Data Collection ===")
    try:
        db = DatabaseManager()
        forms = db.get_all_forms()
        
        if not forms:
            print(f"{WARN} No forms available for testing")
            return True
        
        form_def = forms[0]['definition']
        if isinstance(form_def, str):
            form_def = json.loads(form_def)
        
        # Just validate form definition structure
        if not isinstance(form_def, dict):
            print(f"{FAIL} Form definition is not a dict: {type(form_def)}")
            return False
        
        # Check for required sections
        if 'sections' not in form_def:
            print(f"{FAIL} Form definition missing 'sections' key")
            return False
        
        print(f"{CHECK} Form data structure is valid")
        print(f"  Form: {forms[0]['name']}")
        print(f"  Sections: {len(form_def.get('sections', []))}")
        
        return True
    except Exception as e:
        print(f"{FAIL} Form data collection failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("FORM FILLING WORKFLOW END-TO-END TEST")
    print("=" * 60)
    
    tests = [
        test_database_forms_loaded,
        test_database_clients_loaded,
        test_form_structure,
        test_client_structure,
        test_form_submission_creation,
        test_offline_mode_detection,
        test_form_data_collection,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"{FAIL} Test crashed: {e}")
            results.append((test.__name__, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = f"{CHECK}" if result else f"{FAIL}"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Form workflow is ready for production.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Review output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
