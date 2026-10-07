filePath = r"C:\Users\ginte\OneDrive\Desktop\PROJECTS\PYTHON\compharm\react-backend-server\public\index.html"

# Read fresh
with open(filePath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the actual line
start = content.find("async function loadClients()")
section = content[start:start+500]
lines = section.split('\n')

print("Current state of loadClients (first 8 lines):")
for i, line in enumerate(lines[:8], 1):
    print(f"{i}: {repr(line)}")

print("\n\nLine 4 exactly:")
print(repr(lines[3]))
