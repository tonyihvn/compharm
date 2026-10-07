filePath = r"C:\Users\ginte\OneDrive\Desktop\PROJECTS\PYTHON\compharm\react-backend-server\public\index.html"

with open(filePath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the Authorization line
start = content.find("headers: { 'Authorization':")
if start != -1:
    end = content.find("}", start) + 1
    auth_line = content[start:end]
    print(f"Authorization line ({len(auth_line)} chars):")
    print(repr(auth_line))
    print("\nPlain text:")
    print(auth_line)
