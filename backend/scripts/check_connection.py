"""Check that database, API and dashboard are connected end to end.
   python scripts/check_connection.py --user alice --password "ChooseAStrongOne1!"
   [--api http://127.0.0.1:8000] [--web http://localhost:5173]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # lets "python scripts/x.py" find the itd package
import argparse
import httpx

ap = argparse.ArgumentParser()
ap.add_argument("--api", default="http://127.0.0.1:8000")
ap.add_argument("--web", default="http://localhost:5173")
ap.add_argument("--user", default="alice")
ap.add_argument("--password", required=True)
a = ap.parse_args()
bad = 0


def line(name, good, hint=""):
    global bad
    bad += not good
    print(f"[{'OK' if good else 'FAIL'}] {name}" + ("" if good else f"  -> {hint}"))


# 1. database
try:
    from itd.db import get_db
    db = get_db()
    names = db.list_collection_names()
    line("Database reachable", True)
    flagged, total = db.results.count_documents({"flagged": True}), db.results.count_documents({})
    line(f"Results stored ({total:,} sessions, {flagged:,} flagged)", flagged > 0, "run: python -m itd.engine --data data\\cert_synthetic --retrain")
    line(f"Analyst accounts ({db.analyst_accounts.count_documents({})})", db.analyst_accounts.count_documents({}) > 0,
         "run: python -m scripts.analysts add alice \"Password\"")
    line("Models saved", db.trained_models.count_documents({}) > 0, "run the engine with --retrain")
except Exception as e:
    line("Database reachable", False, f"start Docker Desktop and run: docker compose up -d  ({type(e).__name__})")

# 2. API
token = None
try:
    r = httpx.get(a.api + "/openapi.json", timeout=5)
    line("API reachable", r.status_code == 200, "start it: python -m itd.serve")
    h = httpx.get(a.api + "/api/health", timeout=5)
    line("API health (API -> database)", h.status_code == 200, "the API is up but cannot reach MongoDB: docker compose up -d")
    r = httpx.post(a.api + "/api/login", json={"username": a.user, "password": a.password}, timeout=10)
    line("API login (API -> database)", r.status_code == 200, f"HTTP {r.status_code}: check the username/password and that the database is running")
    token = r.json().get("token") if r.status_code == 200 else None
    if token:
        r = httpx.get(a.api + "/api/sessions?limit=1", headers={"Authorization": f"Bearer {token}"}, timeout=10)
        n = r.json().get("sessions", []) if r.status_code == 200 else []
        line("API session list (API -> database)", bool(n), f"HTTP {r.status_code}")
except Exception as e:
    line("API reachable", False, f"start it: python -m itd.serve  ({type(e).__name__})")

# 3. dashboard -> API through the dashboard server's proxy
try:
    r = httpx.post(a.web + "/api/login", json={"username": a.user, "password": a.password}, timeout=10)
    line("Dashboard proxy (dashboard -> API)", r.status_code == 200, f"HTTP {r.status_code}: the dashboard server cannot reach the API; check vite.config.js and that the API is on port 8000")
except Exception as e:
    line("Dashboard reachable", False, f"start it: cd frontend; npm run dev  ({type(e).__name__})")

print("\nEverything is connected." if not bad else f"\n{bad} check(s) failed. Fix them in order from the top.")
sys.exit(1 if bad else 0)
