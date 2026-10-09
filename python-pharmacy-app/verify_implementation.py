#!/usr/bin/env python3
"""Final verification of form preview and editing implementation"""

import re

def verify_implementation():
    """Verify all implementation requirements are met"""
    with open('ui/admin_panel.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print('=' * 70)
    print('IMPLEMENTATION VERIFICATION REPORT')
    print('=' * 70)
    
    # 1. Check for required classes
    print('\n[1] CLASS DEFINITIONS:')
    classes = {
        'FormPreviewDialog': 'class FormPreviewDialog(QDialog):',
        'FormEditorWithPreviewDialog': 'class FormEditorWithPreviewDialog(QDialog):'
    }
    
    for name, pattern in classes.items():
        if pattern in content:
            print(f'  [OK] {name} defined')
        else:
            print(f'  [FAIL] {name} NOT found')
    
    # 2. Check FormPreviewDialog methods
    print('\n[2] FormPreviewDialog METHODS:')
    preview_methods = [
        ('init_ui', 'def init_ui(self):'),
        ('render_form_preview', 'def render_form_preview(self, layout):'),
        ('render_section', 'def render_section(self, layout, section):'),
        ('render_question', 'def render_question(self, layout, question):'),
    ]
    
    for name, pattern in preview_methods:
        if pattern in content:
            print(f'  [OK] {name}')
        else:
            print(f'  [FAIL] {name} NOT found')
    
    # 3. Check FormEditorWithPreviewDialog methods
    print('\n[3] FormEditorWithPreviewDialog METHODS:')
    editor_methods = [
        ('init_ui', 'def init_ui(self):'),
        ('on_json_changed', 'def on_json_changed(self):'),
        ('update_preview', 'def update_preview(self, form_data):'),
        ('render_preview_section', 'def render_preview_section(self, section):'),
        ('render_preview_question', 'def render_preview_question(self, question):'),
        ('reset_json', 'def reset_json(self):'),
        ('save_form', 'def save_form(self):'),
    ]
    
    for name, pattern in editor_methods:
        if pattern in content:
            print(f'  [OK] {name}')
        else:
            print(f'  [FAIL] {name} NOT found')
    
    # 4. Check AdminPanel method updates
    print('\n[4] AdminPanel METHOD UPDATES:')
    if 'FormPreviewDialog(self, form_data, form_name)' in content:
        print(f'  [OK] preview_form() uses FormPreviewDialog')
    else:
        print(f'  [FAIL] preview_form() does NOT use FormPreviewDialog')
    
    if 'FormEditorWithPreviewDialog(self, form_data, self.api_url, token, form_id)' in content:
        print(f'  [OK] edit_form() uses FormEditorWithPreviewDialog')
    else:
        print(f'  [FAIL] edit_form() does NOT use FormEditorWithPreviewDialog')
    
    # 5. Check key features
    print('\n[5] KEY FEATURES:')
    features = {
        'JSON Validation': 'json.JSONDecodeError',
        'Live Preview': 'self.json_editor.textChanged.connect(self.on_json_changed)',
        'Bearer Token Auth': 'f"Bearer {token}"',
        'Error Handling': 'QMessageBox.critical',
        'Form Format Support': 'form_data.get("pages",',
        'Scrollable Content': 'QScrollArea',
        'Split View': 'QSplitter',
    }
    
    for feature, pattern in features.items():
        count = content.count(pattern)
        if count > 0:
            print(f'  [OK] {feature} ({count} instances)')
        else:
            print(f'  [FAIL] {feature} NOT found')
    
    # 6. Check imports
    print('\n[6] REQUIRED IMPORTS:')
    required_imports = [
        'QDialog',
        'QScrollArea',
        'QFrame',
        'QSplitter',
        'QPlainTextEdit',
    ]
    
    for imp in required_imports:
        if imp in content:
            print(f'  [OK] {imp}')
        else:
            print(f'  [FAIL] {imp} NOT found')
    
    # 7. File statistics
    print('\n[7] FILE STATISTICS:')
    lines = content.split('\n')
    print(f'  Total lines: {len(lines)}')
    print(f'  Non-empty lines: {sum(1 for line in lines if line.strip())}')
    
    # Find key line numbers
    for i, line in enumerate(lines, 1):
        if 'class FormPreviewDialog' in line:
            print(f'  FormPreviewDialog starts at line {i}')
        if 'class FormEditorWithPreviewDialog' in line:
            print(f'  FormEditorWithPreviewDialog starts at line {i}')
    
    # 8. Compile check
    print('\n[8] SYNTAX VALIDATION:')
    try:
        import py_compile
        py_compile.compile('ui/admin_panel.py', doraise=True)
        print('  [OK] Python syntax is valid')
    except SyntaxError as e:
        print(f'  [FAIL] Syntax error: {e}')
    
    # 9. Import check
    print('\n[9] MODULE IMPORT:')
    try:
        from ui.admin_panel import FormPreviewDialog, FormEditorWithPreviewDialog, AdminPanel
        print('  [OK] FormPreviewDialog imported')
        print('  [OK] FormEditorWithPreviewDialog imported')
        print('  [OK] AdminPanel imported')
    except Exception as e:
        print(f'  [FAIL] Import error: {e}')
    
    print('\n' + '=' * 70)
    print('VERIFICATION COMPLETE!')
    print('=' * 70)


if __name__ == '__main__':
    import os
    os.chdir('.')  # Already in the correct directory
    verify_implementation()
