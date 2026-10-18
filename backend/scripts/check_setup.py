"""Check the development environment.   python scripts/check_setup.py"""
import importlib
import os
import shutil
import subprocess
import sys

ok = True


def line(name, good, hint=""):
    global ok
    ok &= good
    print(f"[{'OK' if good else 'FAIL'}] {name}" + ("" if good else f"  -> {hint}"))


line(f"Python {sys.version.split()[0]} (need 3.10+)", sys.version_info >= (3, 10), "install Python 3.10 or newer")
for mod in ["pandas", "numpy", "sklearn", "xgboost", "shap", "fastapi", "uvicorn", "pymongo", "bcrypt", "jwt", "httpx", "cryptography"]:
    try:
        importlib.import_module(mod); line(f"package {mod}", True)
    except ImportError:
        line(f"package {mod}", False, "pip install -r requirements.txt (with the virtual environment active)")
node = shutil.which("node")
if node:
    v = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
    line(f"Node.js {v} (need 18+)", int(v.lstrip("v").split(".")[0]) >= 18, "install Node.js 18 or newer")
else:
    line("Node.js", False, "install Node.js 18+ from nodejs.org")
line("npm", bool(shutil.which("npm")), "comes with Node.js")
line("git", bool(shutil.which("git")), "install Git from git-scm.com")
try:
    from pymongo import MongoClient
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MongoClient(uri, serverSelectionTimeoutMS=2000).admin.command("ping")
    line(f"MongoDB reachable at {uri}", True)
except Exception:
    line("MongoDB reachable", False, "start Docker Desktop, then: docker compose up -d (from the project root)")
print("\nAll good. Next: python scripts/generate_synthetic_cert.py data/cert_synthetic" if ok else "\nFix the FAIL lines above, then run this again.")
