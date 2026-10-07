filePath = r"C:\Users\ginte\OneDrive\Desktop\PROJECTS\PYTHON\compharm\react-backend-server\public\index.html"

with open(filePath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the Authorization line
start = content.find("async function loadClients()")
section = content[start:start+400]
print("Found section:")
print(section)
print("\n\n=== Now searching for the Authorization pattern ===")
auth_start = section.find("headers: { 'Authorization':")
if auth_start != -1:
    segment = section[auth_start:auth_start+150]
    print(f"\nAuthorization segment:\n{repr(segment)}")
