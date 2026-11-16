"""Integrated test (docs/INTEGRATED_TESTING_PLAN.pdf): every part running together. Starts the API, a second API that
requires HTTPS, the worker and the dashboard against a scratch database, runs cases IT1 to IT9 and writes
reports/integration/results.json. The main database is not touched; the scratch database is dropped at the end.
Needs MongoDB running and Node (dashboard). Page load needs Chrome and puppeteer-core on NODE_PATH, else it is skipped.
   python scripts/integration_test.py [--keep]"""
import argparse
import json
import os
import secrets
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone

import httpx
import jwt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DB, API, API_TLS, WEB = "itd_integration", 8100, 8101, 5180
BASE, CONTAINER = f"http://127.0.0.1:{API}", "insider-threat-detection-mongo-1"
results, procs = [], {}


def case(cid, name, expected, check):
    """Run one check; it returns (passed, observed). Any exception is a failed case with the error as observation."""
    t = time.time()
    try:
        ok, seen = check()
    except Exception as e:                                              # a crash is a finding, not the end of the run
        ok, seen = False, f"{type(e).__name__}: {e}"
    results.append({"id": cid, "name": name, "expected": expected, "observed": seen, "passed": bool(ok), "seconds": round(time.time() - t, 2)})
    print(f"{'PASS' if ok else 'FAIL'} {cid} {name}: {seen}", flush=True)


def start(name, cmd, env, cwd):
    log = open(os.path.join(OUT, f"{name}.log"), "w")
    procs[name] = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT)


def wait_for(url, timeout=90):
    end = time.time() + timeout
    while time.time() < end:
        try:
            if httpx.get(url, timeout=2).status_code < 500:
                return True
        except httpx.HTTPError:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"{url} did not answer")


def login(c, user, pw):
    r = c.post("/api/login", json={"username": user, "password": pw})
    r.raise_for_status()
    return {"Authorization": "Bearer " + r.json()["token"]}


def run_and_wait(c, admin, dataset, retrain, timeout=300):
    r = c.post("/api/run", json={"dataset": dataset, "retrain": retrain}, headers=admin)
    assert r.status_code == 202, (r.status_code, r.text)
    end = time.time() + timeout
    while time.time() < end:
        req = c.get("/api/run/status", headers=admin).json()["request"]
        if req["status"] in ("done", "failed"):
            return req
        time.sleep(0.5)
    raise RuntimeError(f"run on {dataset} did not finish in {timeout} s")


def make_data(root):
    gen = os.path.join(root, "generated")
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts", "generate_synthetic_cert.py"), gen, "--users", "60",
                           "--days", "80", "--insiders", "8"], stdout=subprocess.DEVNULL)
    shutil.copytree(os.path.join(ROOT, "data", "spedia_cert"), os.path.join(root, "spedia_cert"))
    for name, damage in (("bad_no_device", lambda d: os.remove(os.path.join(d, "device.csv"))),
                         ("bad_column", lambda d: _edit(d, "http.csv", lambda lines: [",".join(x.split(",")[:4]) + "\n" for x in lines])),
                         ("bad_date", lambda d: _edit(d, "logon.csv", lambda lines: lines[:3] + [lines[3].replace(lines[3].split(",")[1], "2010-01-05 09:00:00", 1)] + lines[4:])),
                         ("warn_duplicates", lambda d: (_edit(d, "http.csv", lambda lines: lines + [lines[1]]),
                                                        _edit(d, "answers.csv", lambda lines: lines + ["http,{NO-SUCH-EVENT}\n"])))):
        d = os.path.join(root, name)
        shutil.copytree(gen, d)
        damage(d)
    e = os.path.join(root, "edges")                                    # hand-made session edges (IT6)
    os.makedirs(e)
    rows = {"logon": ["id,date,user,pc,activity", "L1,01/04/2010 09:00:00,EDGE01,PC-E1,Logon", "L2,01/04/2010 22:00:00,EDGE01,PC-E1,Logon",
                      "L3,01/04/2010 23:00:00,EDGE01,PC-E1,Logoff", "L4,01/05/2010 09:00:00,EDGE02,PC-E1,Logon",
                      "L5,01/05/2010 17:00:00,EDGE02,PC-E1,Logoff", "L6,01/05/2010 10:00:00,EDGE02,PC-E2,Logon",
                      "L7,01/05/2010 11:00:00,EDGE02,PC-E2,Logoff"],
            "http": ["id,date,user,pc,url", "H1,01/04/2010 08:59:00,EDGE01,PC-E1,http://a.com/x", "H2,01/04/2010 12:00:00,EDGE01,PC-E1,http://a.com/y",
                     "H3,01/04/2010 21:30:00,EDGE01,PC-E1,http://a.com/z", "H4,01/04/2010 12:00:00,EDGE01,PC-E9,http://a.com/w"],
            "device": ["id,date,user,pc,activity"], "email": ["id,date,user,pc,to,size,attachments"], "file": ["id,date,user,pc,filename"]}
    for k, lines in rows.items():
        open(os.path.join(e, f"{k}.csv"), "w").write("\n".join(lines) + "\n")


def _edit(folder, name, fn):
    path = os.path.join(folder, name)
    lines = open(path).readlines()
    open(path, "w").writelines(fn(lines))


def main(keep):
    from pymongo import MongoClient
    from itd.security import hash_password
    mongo = MongoClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=5000)
    mongo.admin.command("ping")
    mongo.drop_database(DB)
    data = tempfile.mkdtemp(prefix="itd_it_data_")
    make_data(data)
    secret, pw = secrets.token_urlsafe(32), secrets.token_urlsafe(16)
    db = mongo[DB]
    for user, role in (("it_admin", "admin"), ("it_analyst", "analyst")):
        db.analyst_accounts.insert_one({"_id": user, "password_hash": hash_password(pw), "role": role})
    env = {**os.environ, "DB_NAME": DB, "JWT_SECRET": secret, "ITD_DATA_ROOT": data, "MONGO_URI": "mongodb://127.0.0.1:27017",
           "PYTHONUNBUFFERED": "1"}
    start("api", [sys.executable, "-m", "itd.serve", "--port", str(API)], env, ROOT)
    start("api_https", [sys.executable, "-m", "itd.serve", "--port", str(API_TLS), "--cert", "none", "--key", "none"],
          {**env, "REQUIRE_HTTPS": "1"}, ROOT)
    start("worker", [sys.executable, "-m", "itd.worker"], env, ROOT)
    start("web", ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", str(WEB), "--strictPort"], {**env, "API_URL": BASE}, os.path.join(ROOT, "..", "frontend"))
    c = httpx.Client(base_url=BASE, timeout=30)
    try:
        wait_for(f"{BASE}/api/health"); wait_for(f"http://127.0.0.1:{API_TLS}/api/health"); wait_for(f"http://127.0.0.1:{WEB}/")
        admin, analyst = login(c, "it_admin", pw), login(c, "it_analyst", pw)

        def it1():
            t = time.time(); h = c.get("/api/health"); th = time.time() - t
            t = time.time(); w = httpx.get(f"http://127.0.0.1:{WEB}/", timeout=10); tw = time.time() - t
            ok = h.status_code == 200 and w.status_code == 200 and th < 2 and tw < 2
            return ok, f"health {h.status_code} in {th * 1000:.0f} ms ({h.json()}), dashboard {w.status_code} in {tw * 1000:.0f} ms"
        case("IT1", "Start-up: health check, database, dashboard", "All answer, each within 2 seconds", it1)

        state = {}

        def it2():
            req = run_and_wait(c, admin, "generated", True)
            latest = c.get("/api/run/latest", headers=admin).json()
            m = (latest.get("metrics") or {}).get("test", {}).get("risk_engine", {})
            flagged = c.get("/api/sessions", headers=analyst).json()["sessions"]
            state["scores"] = {d["_id"]: d["risk_score"] for d in db.results.find({}, {"risk_score": 1})}
            ok = req["status"] == "done" and len(state["scores"]) > 0 and db.trained_models.count_documents({}) == 1 and flagged
            return ok, (f"status {req['status']}, {len(state['scores']):,} sessions stored, {len(flagged)} flagged, test precision "
                        f"{m.get('precision', 0):.2f}, recall {m.get('recall', 0):.2f}, F1 {m.get('f1', 0):.2f}")
        case("IT2", "Administrator starts a run with new models, the worker finishes it", "Done, results and models stored, flagged list filled", it2)

        def it3():
            steps = []
            lst = c.get("/api/sessions", headers=analyst); steps.append(("flagged list", lst.status_code == 200 and lst.json()["sessions"]))
            top = lst.json()["sessions"][0]
            det = c.get(f"/api/sessions/{top['session_id']}", headers=analyst)
            steps.append(("session and its reasons", det.status_code == 200 and det.json().get("top_shap") is not None))
            ch = c.post(f"/api/sessions/{top['session_id']}/chat", json={"question": "Why was this session flagged?"}, headers=analyst)
            steps.append(("question to the assistant", ch.status_code == 200 and ch.json().get("fields_used") and not ch.json().get("declined")))
            up = c.get(f"/api/users/{top['user']}", headers=analyst); steps.append(("user page", up.status_code == 200))
            rep = c.get("/api/run/report", headers=analyst); steps.append(("run report", rep.status_code == 200 and "<html" in rep.text.lower()))
            logged = {a: db.access_log.count_documents({"user": "it_analyst", "action": a}) for a in ("session_viewed", "assistant_question", "user_viewed", "report_viewed")}
            steps.append(("access log", all(v >= 1 for v in logged.values())))
            done = sum(1 for _, ok in steps if ok)
            return done == len(steps), f"task completion {done} of {len(steps)} steps ({', '.join(n for n, ok in steps if not ok) or 'all worked'}), log entries {logged}"
        case("IT3", "Analyst workflow: list, session, assistant, user page, report", "Every step works and is logged", it3)

        def it4():
            out = {"analyst asks for a run": c.post("/api/run", json={"dataset": "generated"}, headers=analyst).status_code,
                   "no token": c.get("/api/sessions").status_code}
            old = jwt.encode({"sub": "it_analyst", "role": "analyst", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}, secret, algorithm="HS256")
            out["expired token"] = c.get("/api/sessions", headers={"Authorization": f"Bearer {old}"}).status_code
            out["plain HTTP when HTTPS is required"] = httpx.get(f"http://127.0.0.1:{API_TLS}/api/sessions", headers=analyst).status_code
            return out == {"analyst asks for a run": 403, "no token": 401, "expired token": 401, "plain HTTP when HTTPS is required": 426}, str(out)
        case("IT4", "Access control (the login throttle is checked last, in IT4b)", "403, 401, 401 and 426", it4)

        def it5():
            before = db.results.count_documents({})
            seen = {}
            for name, rule in (("bad_no_device", "V1"), ("bad_column", "V2"), ("bad_date", "V3")):
                req = run_and_wait(c, admin, name, True)
                seen[name] = (req["status"], rule in (req.get("message") or "") or rule in (c.get("/api/run/status", headers=admin).json()["request"].get("log") or ""))
            kept = db.results.count_documents({}) == before                 # checked before the warnings run replaces them
            req = run_and_wait(c, admin, "warn_duplicates", False)
            warn = db.runs.find_one(sort=[("at", -1)]).get("validation") or {}
            seen["warn_duplicates"] = (req["status"], warn.get("warnings", 0) >= 2)
            ok = all(s == ("failed", True) for k, s in seen.items() if k != "warn_duplicates") and seen["warn_duplicates"] == ("done", True) and kept
            return ok, f"{seen}, results kept after the failed runs: {kept}"
        case("IT5", "Bad input: missing file, missing column, wrong date, repeated ids and labels without an event",
             "Runs stop with V1, V2 and V3, the warnings run finishes", it5)

        def it6():
            from itd.baselines import add_deviations
            from itd.features import session_features
            from itd.ingest import load_dataset
            req = run_and_wait(c, admin, "edges", False)                   # stored sessions come from the worker's run
            s = {(d["user"], str(d["start"])[11:16]): d for d in db.results.find({"user": {"$in": ["EDGE01", "EDGE02"]}})}
            # the stored results keep scores and reasons, not the counts, so the counts are read from the same preprocessing code
            ses, agg = load_dataset(os.path.join(data, "edges"), pseudonymize=False, log=lambda *a: None)
            f, _ = add_deviations(session_features(ses, agg))
            f = f.assign(hm=f["start"].dt.strftime("%H:%M")).set_index(["user", "hm"])
            checks = {"run done": req["status"] == "done" and len(s) == 4,
                      "12-hour cap": str(s.get(("EDGE01", "09:00"), {}).get("end", ""))[11:16] == "21:00",
                      "only the in-session web visit counted": bool(f.loc[("EDGE01", "09:00"), "n_http"] == 1 and f.loc[("EDGE01", "22:00"), "n_http"] == 0),
                      "overlap not in the baseline": bool(f.loc[("EDGE02", "10:00"), "mean_duration_min"] == 0)}
            return all(checks.values()), str(checks)
        case("IT6", "Session edges: 12-hour cap, events outside sessions, overlapping sessions",
             "Cap at 21:00, outside events dropped, the overlapping session not compared with the open one", it6)

        def it7():
            notes = {}
            req = run_and_wait(c, admin, "generated", False)
            again = {d["_id"]: d["risk_score"] for d in db.results.find({}, {"risk_score": 1}) if d["_id"] in state["scores"]}
            notes["same scores without retraining"] = req["status"] == "done" and again == state["scores"]
            r = c.post("/api/run", json={"dataset": "generated", "retrain": True}, headers=admin)
            while c.get("/api/run/status", headers=admin).json()["request"]["status"] != "running":
                time.sleep(0.2)
            procs["worker"].kill(); procs["worker"].wait()
            st = c.get("/api/run/status", headers=admin).json()["request"]["status"]
            start("worker", [sys.executable, "-m", "itd.worker"], env, ROOT)
            time.sleep(4)
            after = c.get("/api/run/status", headers=admin).json()["request"]
            notes["stopped worker: shown as running, then failed"] = r.status_code == 202 and st == "running" and after["status"] == "failed"
            subprocess.run(["docker", "stop", CONTAINER], check=True, capture_output=True)
            down = c.get("/api/sessions", headers=analyst)
            subprocess.run(["docker", "start", CONTAINER], check=True, capture_output=True)
            end = time.time() + 60
            while time.time() < end and c.get("/api/health").status_code != 200:
                time.sleep(1)
            back = c.get("/api/sessions", headers=analyst)
            notes["database stopped: 503, then back"] = down.status_code == 503 and back.status_code == 200
            notes["worker still running after the outage"] = procs["worker"].poll() is None
            return all(notes.values()), str(notes) + f", message while down: {down.json().get('detail')!r}"
        case("IT7", "Reliability: same data again, worker stopped during a run, MongoDB stopped",
             "Same scores, the stopped run is marked failed, 503 with a clear message and recovery", it7)

        def it8():
            req = run_and_wait(c, admin, "spedia_cert", True)
            m = c.get("/api/run/latest", headers=admin).json()["metrics"]["test"]["risk_engine"]
            return req["status"] == "done", (f"status {req['status']}, {db.results.count_documents({})} sessions, "
                                             f"test precision {m['precision']:.2f}, recall {m['recall']:.2f}, F1 {m['f1']:.2f}")
        case("IT8", "SPEDIA through the whole chain", "The run finishes and results are stored", it8)

        def it9():
            top = c.get("/api/sessions", headers=analyst).json()["sessions"][0]
            calls = {"list": ("get", "/api/sessions", None), "detail": ("get", f"/api/sessions/{top['session_id']}", None),
                     "user history": ("get", f"/api/users/{top['user']}", None), "latest run": ("get", "/api/run/latest", None),
                     "offline chat": ("post", f"/api/sessions/{top['session_id']}/chat", {"question": "Why was this session flagged?"})}
            out, worst = {}, 0
            for name, (verb, url, body) in calls.items():
                ts = []
                for _ in range(30):
                    t = time.time(); getattr(c, verb)(url, headers=analyst, **({"json": body} if body else {})); ts.append((time.time() - t) * 1000)
                ts.sort()
                out[name] = f"median {statistics.median(ts):.1f} ms, p95 {ts[int(len(ts) * .95) - 1]:.1f} ms"
                worst = max(worst, ts[-1])
            page = subprocess.run(["node", os.path.join(ROOT, "scripts", "page_load.mjs"), f"http://127.0.0.1:{WEB}/", "it_analyst", pw],
                                  capture_output=True, text=True, timeout=120)
            pl = json.loads(page.stdout) if page.returncode == 0 else {"skipped": page.stderr.strip()[-200:]}
            ok = worst < 2000 and (pl.get("flagged_list_ms", 0) < 2000 if "flagged_list_ms" in pl else True)
            return ok, f"{out}, slowest {worst:.0f} ms, page load {pl}"
        case("IT9", "Speed: API response times (30 calls each) and page load in a browser", "Under 2 seconds (NF3)", it9)

        def it4b():
            codes = [c.post("/api/login", json={"username": "it_analyst", "password": "wrong"}).status_code for _ in range(6)]
            return codes[:5] == [401] * 5 and codes[5] == 429, f"five wrong passwords {codes[:5]}, then {codes[5]}"
        case("IT4b", "Login throttle: wrong password five times", "Five 401 answers, then 429", it4b)
    finally:
        for p in procs.values():
            p.terminate()
        for p in procs.values():
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()
        subprocess.run(["docker", "start", CONTAINER], capture_output=True)
        if not keep:
            mongo.drop_database(DB)
            shutil.rmtree(data, ignore_errors=True)
    passed = sum(r["passed"] for r in results)
    json.dump({"run_at": time.strftime("%Y-%m-%d %H:%M"), "passed": passed, "total": len(results), "cases": results},
              open(os.path.join(OUT, "results.json"), "w"), indent=2)
    print(f"\n{passed} of {len(results)} cases passed. Details: {os.path.join(OUT, 'results.json')}")
    return passed == len(results)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="keep the scratch database and data folder")
    ap.add_argument("--out", default=os.path.join(ROOT, "reports", "integration"))
    a = ap.parse_args()
    OUT = a.out
    os.makedirs(OUT, exist_ok=True)
    sys.exit(0 if main(a.keep) else 1)
