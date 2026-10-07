import re

filePath = r"C:\Users\ginte\OneDrive\Desktop\PROJECTS\PYTHON\compharm\react-backend-server\public\index.html"

with open(filePath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and fix the malformed Authorization header
# Current state: headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`
# It appears to be showing as: headers: { 'Authorization': `****** }

# Let's find the specific pattern and replace it
old_pattern = r"headers: \{ 'Authorization': `[^`]*\}"
# Match up to the closing brace

# More precise: find loadClients function and replace its Authorization header
if "async function loadClients()" in content:
    # Find the function
    start_idx = content.find("async function loadClients()")
    # Find the next occurrence of "async function" after this one
    next_func_idx = content.find("async function", start_idx + 10)
    
    # Extract the loadClients function
    func_section = content[start_idx:next_func_idx]
    
    # Replace the header in this section
    fixed_section = re.sub(
        r"headers: \{ 'Authorization': `[^}]*\}",
        "headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`",
        func_section
    )
    
    # Replace in the content
    content = content[:start_idx] + fixed_section + content[next_func_idx:]
    
    with open(filePath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[OK] File fixed!")
    
    # Verify
    with open(filePath, 'r', encoding='utf-8') as f:
        content = f.read()
        start = content.find('async function loadClients')
        section = content[start:start+400]
        lines = section.split('\n')[:5]
        for i, line in enumerate(lines, 1):
            print(f"Line {i}: {line}")
else:
    print("ERROR: Could not find loadClients function")
