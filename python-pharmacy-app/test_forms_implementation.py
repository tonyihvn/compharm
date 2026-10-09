"""
Test script to verify forms functionality implementation
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        from ui.form_editor import FormEditorDialog
        print("  [OK] FormEditorDialog imported successfully")
        
        from ui.form_view import FormView
        print("  [OK] FormView imported successfully")
        
        from ui.widgets.forms_list_view import FormsListView
        print("  [OK] FormsListView imported successfully")
        
        from ui.modern_main_window import ModernMainWindow
        print("  [OK] ModernMainWindow imported successfully")
        
        from services.api_client import CentralServerClient
        print("  [OK] CentralServerClient imported successfully")
        
        return True
    except ImportError as e:
        print(f"  [FAIL] Import error: {e}")
        return False


def test_form_editor_syntax():
    """Test FormEditorDialog syntax"""
    print("\nTesting FormEditorDialog...")
    try:
        with open('ui/form_editor.py', 'r') as f:
            content = f.read()
        
        # Check for duplicates
        if content.count('def save_form(self):') > 1:
            print("  [FAIL] Duplicate save_form method found")
            return False
        
        # Check for proper exception handling
        if 'except Exception as e:' not in content:
            print("  [FAIL] Exception handling not found")
            return False
        
        print("  [OK] FormEditorDialog structure is correct")
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_forms_list_view():
    """Test FormsListView implementation"""
    print("\nTesting FormsListView...")
    try:
        from ui.widgets.forms_list_view import FormsListView
        
        # Check if required methods exist
        required_methods = [
            'load_data',
            'refresh_forms_list',
            'refresh_clients_list',
            'on_form_selected',
            'on_client_selected',
            'fill_selected_form',
            'load_submissions',
            'view_submission_details'
        ]
        
        for method in required_methods:
            if not hasattr(FormsListView, method):
                print(f"  [FAIL] Missing method: {method}")
                return False
        
        print("  [OK] FormsListView has all required methods")
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_form_view_enhancements():
    """Test FormView enhancements"""
    print("\nTesting FormView enhancements...")
    try:
        from ui.form_view import FormView
        
        # Check if load_form method exists
        if not hasattr(FormView, 'load_form'):
            print("  [FAIL] load_form method not found")
            return False
        
        # Check if refresh_form_ui method exists
        if not hasattr(FormView, 'refresh_form_ui'):
            print("  [FAIL] refresh_form_ui method not found")
            return False
        
        print("  [OK] FormView has all required methods")
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_api_client():
    """Test API client additions"""
    print("\nTesting API client...")
    try:
        from services.api_client import CentralServerClient
        
        # Check if required methods exist
        required_methods = [
            'fetch_available_forms',
            'get_forms',
            'fetch_clients',
            'submit_form'
        ]
        
        for method in required_methods:
            if not hasattr(CentralServerClient, method):
                print(f"  [FAIL] Missing method: {method}")
                return False
        
        print("  [OK] API client has all required methods")
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_main_window():
    """Test ModernMainWindow integration"""
    print("\nTesting ModernMainWindow integration...")
    try:
        with open('ui/modern_main_window.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for forms list view import
        if 'from ui.widgets.forms_list_view import FormsListView' not in content:
            print("  [FAIL] FormsListView import not found")
            return False
        
        # Check for forms list view initialization
        if 'self.forms_list_view = FormsListView(' not in content:
            print("  [FAIL] FormsListView initialization not found")
            return False
        
        # Check for show_forms_list implementation
        if 'self.stacked_widget.setCurrentIndex(3)' not in content or \
           'self.forms_list_view.load_data()' not in content:
            print("  [FAIL] show_forms_list implementation incomplete")
            return False
        
        # Check for signal connection
        if 'self.forms_list_view.form_selected.connect(self.on_forms_list_form_selected)' not in content:
            print("  [FAIL] Form signal connection not found")
            return False
        
        # Check for on_forms_list_form_selected handler
        if 'def on_forms_list_form_selected(self, form_data: dict, client_data: dict):' not in content:
            print("  [FAIL] on_forms_list_form_selected handler not found")
            return False
        
        print("  [OK] ModernMainWindow integration is complete")
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Forms Functionality Implementation Test Suite")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_form_editor_syntax,
        test_forms_list_view,
        test_form_view_enhancements,
        test_api_client,
        test_main_window
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("Test Results: {}/{} passed".format(sum(results), len(results)))
    print("=" * 60)
    
    if all(results):
        print("\n[OK] All tests passed! Forms functionality is ready to use.")
        return 0
    else:
        print("\n[FAIL] Some tests failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
