import urllib.request
import time
import subprocess
import sys

# Start API server in background
proc = subprocess.Popen([sys.executable, "scripts/api-server.py"])
time.sleep(2)

try:
    with urllib.request.urlopen("http://localhost:8000/api/health") as response:
        print("Health status:", response.status, response.read().decode())
    with urllib.request.urlopen("http://localhost:8000/api/overview") as response:
        print("Overview status:", response.status, response.read()[:100].decode())
finally:
    proc.terminate()
    proc.wait()
    print("API server stopped successfully.")
