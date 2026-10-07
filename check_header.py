import sys
sys.stdout.reconfigure(encoding='utf-8')

filePath = r"C:\Users\ginte\OneDrive\Desktop\PROJECTS\PYTHON\compharm\react-backend-server\public\index.html"

with open(filePath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the Authorization line
start = content.find("async function loadClients()")
section = content[start:start+500]
lines = section.split('\n')[:6]

print("loadClients function (first 6 lines):")
for i, line in enumerate(lines, 1):
    print(f"{i}: {line}")
