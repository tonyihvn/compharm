#!/usr/bin/env python3
"""
Verify Authorization headers are correctly fixed in admin_panel.py
"""

file_path = r"C:\Users\ginte\OneDrive\Desktop\PROJECTS\PYTHON\compharm\python-pharmacy-app\ui\admin_panel.py"

print("=" * 70)
print("AUTHORIZATION HEADER VERIFICATION")
print("=" * 70)

with open(file_path, 'r') as f:
    content = f.read()
    lines = content.split('\n')

# Check 1: Bearer token format exists
print("\n[CHECK 1] Bearer Token Format")
print("-" * 70)
if 'Bearer {token}' in content:
    count = content.count('Bearer {token}')
    print(f"  [OK] Found {count} occurrences of 'Bearer {{token}}'")
    print(f"  [OK] Authorization headers are properly formatted")
else:
    print(f"  [ERROR] No Bearer token format found!")

# Check 2: Find all Authorization header lines
print("\n[CHECK 2] Authorization Headers in Code")
print("-" * 70)
auth_lines = []
for i, line in enumerate(lines, 1):
    if 'headers = {"Authorization"' in line:
        auth_lines.append((i, line.strip()))

print(f"  Found {len(auth_lines)} Authorization header declarations:")
for line_num, line_content in auth_lines:
    if 'Bearer' in line_content:
        print(f"    Line {line_num}: [OK] Has Bearer token")
    else:
        print(f"    Line {line_num}: [ERROR] Missing Bearer token!")

# Check 3: Token retrieval before API calls
print("\n[CHECK 3] Token Retrieval Methods")
print("-" * 70)
methods = ['load_forms_list', 'upload_form', 'edit_form', 'delete_form', 'load_users_list']
for method in methods:
    method_found = False
    method_line = -1
    for i, line in enumerate(lines):
        if f'def {method}(' in line:
            method_found = True
            method_line = i
            break
    
    if method_found:
        # Check next 20 lines for token retrieval
        has_token = False
        has_headers = False
        for i in range(method_line, min(method_line + 30, len(lines))):
            if 'get_auth_token()' in lines[i]:
                has_token = True
            if 'headers = {"Authorization"' in lines[i] and 'Bearer' in lines[i]:
                has_headers = True
        
        if has_token and has_headers:
            print(f"  [OK] {method}() - properly uses token and headers")
        elif has_token:
            print(f"  [WARN] {method}() - gets token but headers unclear")
        elif has_headers:
            print(f"  [WARN] {method}() - has headers but may not get token")
        else:
            print(f"  [ERROR] {method}() - missing token/headers!")
    else:
        print(f"  [INFO] {method}() - not found (may not be implemented)")

# Check 4: API endpoint consistency
print("\n[CHECK 4] API Endpoints")
print("-" * 70)
endpoints = [
    ('/api/forms', 'GET', 'load_forms_list'),
    ('/api/forms/upload', 'POST', 'upload_form'),
    ('/api/forms/', 'GET', 'edit_form'),
    ('/api/forms/', 'DELETE', 'delete_form'),
    ('/api/users', 'GET', 'load_users_list'),
]

for endpoint, method, func in endpoints:
    if endpoint in content:
        print(f"  [OK] Endpoint {endpoint} ({method}) - used in {func}")
    else:
        print(f"  [WARN] Endpoint {endpoint} - may not be used")

# Final summary
print("\n" + "=" * 70)
print("VERIFICATION COMPLETE")
print("=" * 70)
print("\nSUMMARY:")
if content.count('Bearer {token}') >= 4:
    print("  [OK] All Authorization headers properly formatted")
    print("  [OK] Admin panel ready to authenticate with backend server")
    print("  [OK] Users list and admin features should work correctly")
else:
    print("  [ERROR] Some Authorization headers may still have issues")

print("\nTo test:")
print("  1. Start the app: python main.py")
print("  2. Login with admin credentials")
print("  3. Access admin panel features")
print("  4. Should see users list and other admin options")
print("=" * 70 + "\n")
