"""Call every API endpoint and print the results (for the demo and screenshots).
   python scripts/demo_api.py --user alice --password "ChooseAStrongOne1!"  [--base http://127.0.0.1:8000]"""
import argparse
import json
import httpx

ap = argparse.ArgumentParser()
ap.add_argument("--base", default="http://127.0.0.1:8000")
ap.add_argument("--user", default="alice")
ap.add_argument("--password", required=True)
a = ap.parse_args()
c = httpx.Client(base_url=a.base, timeout=30, verify=False)
n = 0


def show(title, r, keep=None):
    global n
    n += 1
    body = r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
    if keep and isinstance(body, dict):
        body = {k: body[k] for k in keep if k in body}
    print(f"\n{n}. {title}\n   -> HTTP {r.status_code}\n   {json.dumps(body, indent=2)[:700]}")


show("Login with a wrong password (expect 401)", c.post("/api/login", json={"username": a.user, "password": "wrong"}))
show("Session list without a token (expect 401)", c.get("/api/sessions"))
show("Login with an injection attempt (expect 422)", c.post("/api/login", json={"username": {"$ne": ""}, "password": {"$ne": ""}}))
r = c.post("/api/login", json={"username": a.user, "password": a.password})
show("Login with the right password (expect 200 and a token)", r, keep=["username", "expires_minutes"])
h = {"Authorization": "Bearer " + r.json()["token"]}
r = c.get("/api/sessions?limit=3", headers=h)
show("Flagged sessions, highest risk first (limit 3)", r)
sid = r.json()["sessions"][0]["session_id"]
r = c.get(f"/api/sessions/{sid}", headers=h)
show(f"Session detail for {sid}", r, keep=["session_id", "risk_score", "threshold", "model_scores", "top_shap", "baseline_deviations"])
show("Ask the assistant", c.post(f"/api/sessions/{sid}/chat", headers=h, json={"question": "Why was this session flagged?"}), keep=["answer", "fields_used", "mode"])
show("Session id with a bad format (expect 422)", c.get("/api/sessions/%7B%22%24ne%22%3A1%7D", headers=h))
show("Session that does not exist (expect 404)", c.get("/api/sessions/S9999999", headers=h))
show("Question over 300 characters (expect 422)", c.post(f"/api/sessions/{sid}/chat", headers=h, json={"question": "x" * 301}))
print("\nDone. Check the access_log collection for the login, view and question entries.")
