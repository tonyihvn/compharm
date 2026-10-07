filePath = r"C:\Users\ginte\OneDrive\Desktop\PROJECTS\PYTHON\compharm\react-backend-server\public\index.html"

with open(filePath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the loadClients function and fix the Authorization header
# The buggy line is around line 808
for i in range(len(lines)):
    if "'Authorization': `" in lines[i]:
        print(f"Found Authorization line at index {i}: {lines[i][:80]}")
        # Replace with correct version
        # The line should be: headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`
        # But we need to escape the $ properly
        lines[i] = "                    headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`\n"
        print(f"Replaced with: {lines[i][:80]}")
        break

with open(filePath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("[DONE] File fixed!")

# Verify
with open(filePath, 'r', encoding='utf-8') as f:
    content = f.read()
    start = content.find("async function loadClients()")
    section = content[start:start+400]
    print("\nVerification (first 5 lines):")
    for i, line in enumerate(section.split('\n')[:5], 1):
        print(f"{i}: {line}")
