"""
SIGTEMBAKAU – Run Script
Menjalankan server FastAPI dengan uvicorn.
"""
import subprocess, sys, os

python = sys.executable
root = os.path.dirname(os.path.abspath(__file__))
uvicorn = os.path.join(os.path.dirname(python), "Scripts", "uvicorn.exe")

if not os.path.exists(uvicorn):
    uvicorn_cmd = [python, "-m", "uvicorn"]
else:
    uvicorn_cmd = [uvicorn]

cmd = uvicorn_cmd + ["main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
print("=" * 55)
print("  🌿 SIGTEMBAKAU – WebGIS Tembakau Nasional")
print("=" * 55)
print(f"  Server: http://localhost:8000")
print(f"  API Docs: http://localhost:8000/api/docs")
print(f"  Login: http://localhost:8000/")
print("=" * 55)
print("  Tekan Ctrl+C untuk menghentikan server.")
print()

os.chdir(root)
subprocess.run(cmd)

