"""Engine time and peak memory at growing data sizes, in a scratch database (your real data is not touched).
Usage:  python scripts/measure_resources.py [--sizes 60,120,240,480] [--days 90]
Needs:  pip install psutil, MongoDB running. For each size it generates a dataset, runs the whole engine with new models in a
subprocess (DB_NAME=itd_perf) and records the wall time, the peak memory of that process (and its children) and the seconds of
each engine step. The scratch database is dropped at the end."""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERF_DB = "itd_perf"


def run_and_measure(cmd, env=None, cwd=ROOT, poll=0.05):
    """Run cmd. Returns (seconds, peak memory in MB, return code, last lines of output). Memory = process plus children."""
    import psutil
    t0 = time.perf_counter()
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    peak, proc = 0, psutil.Process(p.pid)
    while p.poll() is None:
        try:
            rss = proc.memory_info().rss + sum(c.memory_info().rss for c in proc.children(recursive=True))
            peak = max(peak, rss)
        except psutil.Error:
            pass
        time.sleep(poll)
    out = p.stdout.read()
    return time.perf_counter() - t0, peak / 2 ** 20, p.returncode, out.strip().splitlines()[-6:]


def count_rows(folder):
    return sum(sum(1 for _ in open(os.path.join(folder, f"{k}.csv"), encoding="utf-8")) - 1
               for k in ("logon", "device", "email", "file", "http"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="60,120,240,480", help="numbers of users, comma separated")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--report", default="reports")
    a = ap.parse_args()
    sys.path.insert(0, ROOT)
    from itd import config
    from pymongo import MongoClient
    assert PERF_DB != config.DB_NAME, "the scratch database must differ from the real one"
    env = {**os.environ, "DB_NAME": PERF_DB}
    client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
    client.drop_database(PERF_DB)
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for users in [int(x) for x in a.sizes.split(",")]:
            folder = os.path.join(tmp, f"perf_{users}")
            subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts", "generate_synthetic_cert.py"), folder,
                                   "--users", str(users), "--days", str(a.days), "--insiders", str(max(8, users // 10))],
                                  cwd=ROOT, stdout=subprocess.DEVNULL)
            events = count_rows(folder)
            print(f"{users} users: {events:,} events, running the engine ...", flush=True)
            secs, mb, code, tail = run_and_measure([sys.executable, "-m", "itd.engine", "--data", folder, "--retrain",
                                                    "--report", os.path.join(tmp, f"rep_{users}")], env=env)
            row = {"users": users, "events": events, "seconds": secs, "peak_mb": mb, "return_code": code}
            if code == 0:
                run = client[PERF_DB].runs.find_one(sort=[("at", -1)]) or {}
                row.update(sessions=run.get("sessions"), flagged=run.get("flagged"), step_seconds=run.get("step_seconds", {}))
            else:
                row["error"] = " | ".join(tail)
            rows.append(row)
    client.drop_database(PERF_DB)
    steps = ["ingestion_and_sessions", "features_and_baselines", "models", "risk_and_shap"]
    print(f"\n{'users':>6s} {'events':>9s} {'sessions':>9s} {'total s':>8s} {'peak MB':>8s}   " + "  ".join(f"{s[:14]:>14s}" for s in steps))
    for r in rows:
        if r["return_code"]:
            print(f"{r['users']:6d}  FAILED: {r['error']}")
            continue
        print(f"{r['users']:6d} {r['events']:9,d} {r['sessions']:9,d} {r['seconds']:8.1f} {r['peak_mb']:8.0f}   "
              + "  ".join(f"{r['step_seconds'].get(s, 0):14.1f}" for s in steps))
    os.makedirs(a.report, exist_ok=True)
    with open(os.path.join(a.report, "resources.json"), "w") as f:
        json.dump({"days": a.days, "sizes": rows}, f, indent=2)


if __name__ == "__main__":
    main()
