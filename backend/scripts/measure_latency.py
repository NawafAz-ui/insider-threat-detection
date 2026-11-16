"""API response times.
Usage:  python scripts/measure_latency.py --user alice --password "..." [--base http://127.0.0.1:8000] [--repeats 50]
The API and the database must be running with results stored. One persistent connection, 3 warm-up calls and N timed calls
per endpoint. Reports the median, the 95th percentile and the slowest call in milliseconds, and the size of the answer.
Reading a session or a history also writes an access-log entry, as in normal use, so the timings include that write."""
import argparse
import http.client
import json
import os
import socket
import statistics
import sys
import time
from urllib.parse import urlparse


def percentile(values, q):
    v = sorted(values)
    return v[min(len(v) - 1, int(round(q * (len(v) - 1))))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8000")
    ap.add_argument("--user", required=True)
    ap.add_argument("--password", default=os.environ.get("ITD_PASSWORD", ""))
    ap.add_argument("--repeats", type=int, default=50)
    ap.add_argument("--report", default="reports")
    a = ap.parse_args()
    if not a.password:
        raise SystemExit("Give --password or set ITD_PASSWORD.")
    u = urlparse(a.base)
    conn = http.client.HTTPConnection(u.hostname, u.port or 80, timeout=60)
    conn.connect()
    conn.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)       # do not hold small packets back

    def call(method, path, body=None, token=None):
        headers = {"Content-Type": "application/json"} if body is not None else {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        t = time.perf_counter()
        conn.request(method, path, body=json.dumps(body) if body is not None else None, headers=headers)
        resp = conn.getresponse()
        data = resp.read()
        return resp.status, data, (time.perf_counter() - t) * 1000

    status, data, _ = call("POST", "/api/login", {"username": a.user, "password": a.password})
    if status != 200:
        raise SystemExit(f"Login failed (HTTP {status}).")
    token = json.loads(data)["token"]
    status, data, _ = call("GET", "/api/sessions?limit=1", token=token)
    listing = json.loads(data)
    if status != 200 or not listing["sessions"]:
        raise SystemExit("No flagged sessions found. Run the detection engine first.")
    sid, uid = listing["sessions"][0]["session_id"], listing["sessions"][0]["user"]

    cases = [("GET /api/health", "GET", "/api/health", None),
             ("GET /api/sessions (50 rows)", "GET", "/api/sessions?limit=50", None),
             ("GET /api/sessions (200 rows)", "GET", "/api/sessions?limit=200", None),
             ("GET /api/sessions/{id}", "GET", f"/api/sessions/{sid}", None),
             ("GET /api/users/{id}", "GET", f"/api/users/{uid}", None),
             ("GET /api/run/latest", "GET", "/api/run/latest", None),
             ("GET /api/run/status", "GET", "/api/run/status", None),
             ("GET /api/run/report", "GET", "/api/run/report", None),
             ("POST chat (offline answer)", "POST", f"/api/sessions/{sid}/chat", {"question": "Why was this session flagged?"})]
    rows = []
    for name, method, path, body in cases:
        for _ in range(3):                                         # warm-up
            call(method, path, body, token)
        times, size, bad = [], 0, 0
        for _ in range(a.repeats):
            status, data, ms = call(method, path, body, token)
            times.append(ms)
            size = len(data)
            bad += status != 200
        rows.append({"endpoint": name, "n": len(times), "median_ms": statistics.median(times), "p95_ms": percentile(times, 0.95),
                     "max_ms": max(times), "kb": size / 1024, "errors": bad})
    print(f"{a.repeats} timed calls per endpoint, one connection, server {a.base}\n")
    print(f"{'endpoint':32s} {'median':>8s} {'p95':>8s} {'max':>8s} {'size KB':>8s} {'errors':>7s}")
    for r in rows:
        print(f"{r['endpoint']:32s} {r['median_ms']:7.1f}ms {r['p95_ms']:7.1f}ms {r['max_ms']:7.1f}ms {r['kb']:8.1f} {r['errors']:7d}")
    os.makedirs(a.report, exist_ok=True)
    with open(os.path.join(a.report, "latency.json"), "w") as f:
        json.dump({"base": a.base, "repeats": a.repeats, "endpoints": rows}, f, indent=2)


if __name__ == "__main__":
    main()
