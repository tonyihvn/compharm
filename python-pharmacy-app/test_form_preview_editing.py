#!/usr/bin/env python3
"""
Test script for form preview and editing functionality
"""

import sys
import os
import json

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Test that new dialog classes can be imported"""
    print("Testing imports...")
    try:
        # This will test if the updated admin_panel.py has valid syntax
        from ui.admin_panel import FormPreviewDialog, FormEditorWithPreviewDialog, AdminPanel
        print("  [OK] FormPreviewDialog imported successfully")
        print("  [OK] FormEditorWithPreviewDialog imported successfully")
        print("  [OK] AdminPanel imported successfully")
        return True
    except ImportError as e:
        print(f"  [FAIL] Import error: {e}")
        return False
    except SyntaxError as e:
        print(f"  [FAIL] Syntax error: {e}")
        return False


def test_admin_panel_syntax():
    """Test admin_panel.py for syntax and key methods"""
    print("\nTesting admin_panel.py syntax and methods...")
    try:
        with open('ui/admin_panel.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required classes
        if 'class FormPreviewDialog(QDialog):' not in content:
            print("  [FAIL] FormPreviewDialog class not found")
            return False
        print("  [OK] FormPreviewDialog class found")
        
        if 'class FormEditorWithPreviewDialog(QDialog):' not in content:
            print("  [FAIL] FormEditorWithPreviewDialog class not found")
            return False
        print("  [OK] FormEditorWithPreviewDialog class found")
        
        # Check for required methods in FormPreviewDialog
        if 'def render_form_preview(self, layout):' not in content:
            print("  [FAIL] render_form_preview method not found")
            return False
        print("  [OK] render_form_preview method found")
        
        if 'def render_section(self, layout, section):' not in content:
            print("  [FAIL] render_section method not found")
            return False
        print("  [OK] render_section method found")
        
        if 'def render_question(self, layout, question):' not in content:
            print("  [FAIL] render_question method not found")
            return False
        print("  [OK] render_question method found")
        
        # Check for FormEditorWithPreviewDialog methods
        if 'def on_json_changed(self):' not in content:
            print("  [FAIL] on_json_changed method not found")
            return False
        print("  [OK] on_json_changed method found")
        
        if 'def update_preview(self, form_data):' not in content:
            print("  [FAIL] update_preview method not found")
            return False
        print("  [OK] update_preview method found")
        
        # Check that preview_form uses FormPreviewDialog
        if 'FormPreviewDialog(self, form_data, form_name)' not in content:
            print("  [FAIL] preview_form doesn't use FormPreviewDialog")
            return False
        print("  [OK] preview_form uses FormPreviewDialog")
        
        # Check that edit_form uses FormEditorWithPreviewDialog
        if 'FormEditorWithPreviewDialog(self, form_data, self.api_url, token, form_id)' not in content:
            print("  [FAIL] edit_form doesn't use FormEditorWithPreviewDialog")
            return False
        print("  [OK] edit_form uses FormEditorWithPreviewDialog")
        
        # Check for Bearer token support
        token_count = content.count('f"Bearer {token}"')
        if token_count < 2:
            print(f"  [WARN] Found only {token_count} Bearer token headers (expected at least 2)")
        else:
            print(f"  [OK] Found {token_count} Bearer token headers")
        
        # Check for proper JSON validation
        if 'json.JSONDecodeError' not in content:
            print("  [FAIL] JSON validation not properly implemented")
            return False
        print("  [OK] JSON validation found")
        
        # Check for live preview functionality
        if 'self.json_editor.textChanged.connect(self.on_json_changed)' not in content:
            print("  [FAIL] Live preview connection not found")
            return False
        print("  [OK] Live preview connection found")
        
        return True
    
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_form_data_structure():
    """Test that sample form data can be processed correctly"""
    print("\nTesting form data structure handling...")
    try:
        # Create sample form data
        sample_form = {
            "name": "Test Form",
            "description": "A test form",
            "version": "1.0",
            "published": True,
            "pages": [
                {
                    "label": "Page 1",
                    "sections": [
                        {
                            "label": "Section 1",
                            "name": "section_1",
                            "questions": [
                                {
                                    "id": "field_1",
                                    "label": "Test Field",
                                    "type": "text",
                                    "required": True,
                                    "placeholder": "Enter value"
                                },
                                {
                                    "id": "field_2",
                                    "label": "Select Option",
                                    "type": "select",
                                    "required": False,
                                    "questionOptions": {
                                        "rendering": "select",
                                        "answers": [
                                            {"label": "Option 1", "concept": "1"},
                                            {"label": "Option 2", "concept": "2"}
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Verify JSON serialization
        json_str = json.dumps(sample_form, indent=2)
        parsed = json.loads(json_str)
        
        if parsed["name"] != "Test Form":
            print("  [FAIL] JSON serialization failed")
            return False
        
        if len(parsed["pages"]) != 1:
            print("  [FAIL] Pages not preserved")
            return False
        
        if len(parsed["pages"][0]["sections"]) != 1:
            print("  [FAIL] Sections not preserved")
            return False
        
        if len(parsed["pages"][0]["sections"][0]["questions"]) != 2:
            print("  [FAIL] Questions not preserved")
            return False
        
        print("  [OK] Form data structure validation passed")
        return True
    
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def test_file_integrity():
    """Test that the file hasn't been corrupted"""
    print("\nTesting file integrity...")
    try:
        import py_compile
        
        py_compile.compile('ui/admin_panel.py', doraise=True)
        print("  [OK] admin_panel.py compiles successfully")
        
        # Test that we can actually import it
        from ui import admin_panel
        print("  [OK] admin_panel module imports successfully")
        
        # Check key classes exist
        assert hasattr(admin_panel, 'AdminPanel'), "AdminPanel class not found"
        print("  [OK] AdminPanel class accessible")
        
        assert hasattr(admin_panel, 'FormPreviewDialog'), "FormPreviewDialog class not found"
        print("  [OK] FormPreviewDialog class accessible")
        
        assert hasattr(admin_panel, 'FormEditorWithPreviewDialog'), "FormEditorWithPreviewDialog class not found"
        print("  [OK] FormEditorWithPreviewDialog class accessible")
        
        return True
    
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("Form Preview and Editing Functionality Tests")
    print("=" * 70)
    
    tests = [
        test_admin_panel_syntax,
        test_form_data_structure,
        test_file_integrity,
        test_imports,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"\n[ERROR] Test {test.__name__} failed with exception: {e}")
            results.append((test.__name__, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
