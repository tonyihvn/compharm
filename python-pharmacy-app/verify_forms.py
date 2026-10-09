#!/usr/bin/env python
"""
Quick Test Script for Forms Functionality
Run this to verify forms are working correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_basic_workflow():
    """Test the basic workflow of forms functionality"""
    print("\n" + "="*70)
    print("FORMS FUNCTIONALITY - QUICK TEST")
    print("="*70)
    
    # Test 1: Import all necessary modules
    print("\n[TEST 1] Importing modules...")
    try:
        from ui.form_editor import FormEditorDialog
        from ui.form_view import FormView
        from ui.widgets.forms_list_view import FormsListView
        from ui.modern_main_window import ModernMainWindow
        from services.api_client import CentralServerClient
        print("[PASS] All imports successful")
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False
    
    # Test 2: Check API client
    print("\n[TEST 2] Checking API client...")
    try:
        client = CentralServerClient()
        
        # Check for required methods
        required_methods = [
            'fetch_available_forms',
            'get_forms',
            'fetch_clients',
            'submit_form',
            'get_client_details'
        ]
        
        for method in required_methods:
            if not hasattr(client, method):
                print(f"[FAIL] Missing method: {method}")
                return False
        
        print("[PASS] API client has all required methods")
    except Exception as e:
        print(f"[FAIL] Error checking API client: {e}")
        return False
    
    # Test 3: Check FormView enhancements
    print("\n[TEST 3] Checking FormView enhancements...")
    try:
        # Check for new methods
        if not hasattr(FormView, 'load_form'):
            print("[FAIL] load_form method not found")
            return False
        
        if not hasattr(FormView, 'refresh_form_ui'):
            print("[FAIL] refresh_form_ui method not found")
            return False
        
        # Check method signatures
        import inspect
        
        load_form_sig = inspect.signature(FormView.load_form)
        if 'form_id' not in str(load_form_sig) or 'client_id' not in str(load_form_sig):
            print("[FAIL] load_form has incorrect signature")
            return False
        
        print("[PASS] FormView enhancements verified")
    except Exception as e:
        print(f"[FAIL] Error checking FormView: {e}")
        return False
    
    # Test 4: Check FormsListView
    print("\n[TEST 4] Checking FormsListView...")
    try:
        required_methods = [
            'load_data',
            'refresh_forms_list',
            'refresh_clients_list',
            'on_form_selected',
            'on_client_selected',
            'fill_selected_form',
            'load_submissions'
        ]
        
        for method in required_methods:
            if not hasattr(FormsListView, method):
                print(f"[FAIL] Missing method: {method}")
                return False
        
        # Check for signals
        import inspect
        source = inspect.getsource(FormsListView)
        
        if 'form_selected = pyqtSignal' not in source:
            print("[FAIL] form_selected signal not found")
            return False
        
        print("[PASS] FormsListView verified")
    except Exception as e:
        print(f"[FAIL] Error checking FormsListView: {e}")
        return False
    
    # Test 5: Check ModernMainWindow integration
    print("\n[TEST 5] Checking ModernMainWindow integration...")
    try:
        # Read with UTF-8 encoding to handle special characters
        with open('ui/modern_main_window.py', 'r', encoding='utf-8') as f:
            source = f.read()
        
        checks = [
            ('FormsListView import', 'from ui.widgets.forms_list_view import FormsListView'),
            ('FormsListView initialization', 'self.forms_list_view = FormsListView('),
            ('show_forms_list method', 'def show_forms_list(self):'),
            ('Signal connection', 'self.forms_list_view.form_selected.connect'),
            ('Form handler', 'def on_forms_list_form_selected(self, form_data: dict, client_data: dict):'),
            ('Stack widget index', 'self.stacked_widget.addWidget(self.forms_list_view)'),
        ]
        
        for check_name, check_str in checks:
            if check_str not in source:
                print(f"[FAIL] {check_name} not found")
                return False
        
        print("[PASS] ModernMainWindow integration verified")
    except Exception as e:
        print(f"[FAIL] Error checking ModernMainWindow: {e}")
        return False
    
    # Test 6: Syntax validation
    print("\n[TEST 6] Validating Python syntax...")
    try:
        import py_compile
        
        files_to_check = [
            'ui/form_editor.py',
            'ui/form_view.py',
            'ui/widgets/forms_list_view.py',
            'ui/modern_main_window.py',
            'services/api_client.py'
        ]
        
        for file in files_to_check:
            if not os.path.exists(file):
                print(f"[FAIL] File not found: {file}")
                return False
            
            try:
                py_compile.compile(file, doraise=True)
            except py_compile.PyCompileError as e:
                print(f"[FAIL] Syntax error in {file}: {e}")
                return False
        
        print("[PASS] All files have valid Python syntax")
    except Exception as e:
        print(f"[FAIL] Error validating syntax: {e}")
        return False
    
    return True


def print_workflow_summary():
    """Print the workflow summary"""
    print("\n" + "="*70)
    print("FORMS WORKFLOW")
    print("="*70)
    
    workflow = """
    1. User clicks "Forms" button
       --> ModernMainWindow.show_forms_list()
           --> Sets stacked widget to index 3 (FormsListView)
           
    2. FormsListView loads
       --> Fetches forms via API: /api/forms
       --> Fetches clients via API: /api/clients
       --> Displays both in lists
       
    3. User selects form and client
       --> on_form_selected() captures form
       --> on_client_selected() captures client
       --> fill_selected_form() emits signal
       
    4. Signal emitted
       --> on_forms_list_form_selected() handler called
           --> Loads form details via API
           --> Sets stacked widget to index 2 (FormViewer)
           
    5. FormViewer displays form
       --> load_form() fetches form definition
       --> refresh_form_ui() renders form fields
       --> User fills out form
       
    6. User submits form
       --> submit_form() collects data
       --> POST to /api/submissions
       --> Success message displayed
       
    7. Return to client list or form list
       --> show_client_detail() or show_forms_list()
    """
    
    print(workflow)


def print_api_endpoints():
    """Print required API endpoints"""
    print("\n" + "="*70)
    print("REQUIRED API ENDPOINTS")
    print("="*70)
    
    endpoints = """
    GET /api/forms
    --> Returns: {"forms": [...]}
        Response: List of available forms
        
    GET /api/forms/{formId}
    --> Returns: {"data": {...}}
        Response: Form definition with sections and fields
        
    GET /api/clients
    --> Returns: {"clients": [...]}
        Response: List of clients
        
    GET /api/clients/{clientId}
    --> Returns: {"data": {...}}
        Response: Client details
        
    GET /api/submissions
    --> Returns: {"submissions": [...]}
        Response: List of recent form submissions
        
    POST /api/submissions
    --> Body: {"formId": "...", "clientId": "...", "fields": {...}}
        Response: {"message": "...", "submissionId": "..."}
    """
    
    print(endpoints)


def main():
    """Run all tests and print results"""
    
    # Run tests
    success = test_basic_workflow()
    
    if success:
        print("\n" + "="*70)
        print("ALL TESTS PASSED!")
        print("="*70)
        print("\nForms functionality is ready to use.\n")
        
        # Print additional info
        print_workflow_summary()
        print_api_endpoints()
        
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("""
1. Ensure backend server is running
2. Launch the Python Pharmacy App
3. Login with valid credentials
4. Click "Forms" button to test
5. Select form and client
6. Fill and submit form
7. Check "Form Submissions" tab to verify

For issues, check logs in: logs/pharmacy_app.log
        """)
        return 0
    else:
        print("\n" + "="*70)
        print("TESTS FAILED")
        print("="*70)
        print("\nPlease review the errors above and fix any issues.\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
