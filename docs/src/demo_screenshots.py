"""Retake the data-dependent screenshots of docs/DEMO.md from a COPY of the main database (itd_demo), so the real
database and its accounts are not touched. Needs MongoDB, Node, Chrome and puppeteer-core on NODE_PATH.
   backend/.venv/bin/python docs/src/demo_screenshots.py"""
import html
import os
import secrets
import subprocess
import sys
import time

import httpx

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACK, SHOTS = os.path.join(REPO, "backend"), os.path.join(REPO, "docs", "screenshots")
sys.path.insert(0, BACK)
from pymongo import MongoClient  # noqa: E402
from itd.security import hash_password  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
API, WEB, DEMO = 8200, 5181, "itd_demo"


def wait(url):
    for _ in range(120):
        try:
            if httpx.get(url, timeout=2).status_code < 500:
                return
        except httpx.HTTPError:
            pass
        time.sleep(0.5)
    raise RuntimeError(url)


def terminal_png(name, title, text):
    """Real command output drawn as a terminal window, like the earlier terminal screenshots."""
    page = os.path.join(SHOTS, f".{name}.html")
    open(page, "w").write(f"""<html><body style="margin:0;background:#1e1e1e"><div style="font:13px Menlo,monospace;color:#d4d4d4;padding:14px 18px">
<div style="color:#9cdcfe;margin-bottom:8px">{html.escape(title)}</div><pre style="margin:0;white-space:pre-wrap">{html.escape(text)}</pre></div></body></html>""")
    lines = text.count("\n") + 4
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size=1000,{min(60 + lines * 17, 1600)}",
                    "--force-device-scale-factor=1.5", f"--screenshot={os.path.join(SHOTS, name)}", f"file://{page}"], capture_output=True)
    os.remove(page)


def main():
    m = MongoClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=5000)
    src, dst = m["insider_threat"], m[DEMO]
    m.drop_database(DEMO)
    for coll in ("results", "user_baselines", "trained_models", "runs", "run_requests", "fs.files", "fs.chunks"):
        docs = list(src[coll].find())
        if docs:
            dst[coll].insert_many(docs)
    pw = secrets.token_urlsafe(12)
    for user, role in (("alice", "analyst"), ("admin", "admin")):
        dst.analyst_accounts.insert_one({"_id": user, "password_hash": hash_password(pw), "role": role})
    env = {**os.environ, "DB_NAME": DEMO, "JWT_SECRET": secrets.token_urlsafe(32), "ITD_DATA_ROOT": os.path.join(BACK, "data"),
           "PYTHONUNBUFFERED": "1", "API_URL": f"http://127.0.0.1:{API}"}
    procs = [subprocess.Popen([sys.executable, "-m", "itd.serve", "--port", str(API)], cwd=BACK, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL),
             subprocess.Popen([sys.executable, "-m", "itd.worker"], cwd=BACK, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL),
             subprocess.Popen(["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", str(WEB), "--strictPort"], cwd=os.path.join(REPO, "frontend"),
                              env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)]
    try:
        wait(f"http://127.0.0.1:{API}/api/health"); wait(f"http://127.0.0.1:{WEB}/")
        r = subprocess.run(["node", os.path.join(REPO, "docs", "src", "take_screenshots.mjs"), f"http://127.0.0.1:{WEB}/",
                            f"http://127.0.0.1:{API}", pw, SHOTS], capture_output=True, text=True, timeout=600)
        print(r.stdout.strip(), r.stderr.strip()[-800:])
        out = subprocess.run([sys.executable, "scripts/check_connection.py", "--api", f"http://127.0.0.1:{API}", "--web",
                              f"http://127.0.0.1:{WEB}", "--user", "alice", "--password", pw], cwd=BACK, capture_output=True, text=True)
        api = subprocess.run([sys.executable, "scripts/demo_api.py", "--base", f"http://127.0.0.1:{API}", "--user", "alice", "--password", pw],
                             cwd=BACK, capture_output=True, text=True)
        open(os.path.join(SHOTS, "10-demo-api-results.md"), "w").write(
            "# API demo results\n\nReal output of `python scripts/demo_api.py --user alice --password ********` on a copy of the main database "
            f"(SPEDIA), {time.strftime('%d %B %Y')}.\n\n```\n{api.stdout.strip()}\n```\n")
        terminal_png("01-connection-check.png", "python scripts/check_connection.py --user alice --password ********", out.stdout + out.stderr)
        t = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=BACK, capture_output=True, text=True, env={**os.environ, "MONGO_URI": "mock"})
        tail = t.stdout.strip().splitlines()[-1]                     # the count line
        s = subprocess.run([sys.executable, "-m", "itd.schema", "check"], cwd=BACK, capture_output=True, text=True)
        terminal_png("13-tests-and-schema-check.png", "python -m pytest -q   and   python -m itd.schema check (main database)", tail + "\n\n" + s.stdout + s.stderr)
        subprocess.run(["rm", "-rf", os.path.join(BACK, ".pytest_tmp")])
    finally:
        for p in procs:
            p.terminate()
        m.drop_database(DEMO)


if __name__ == "__main__":
    main()
