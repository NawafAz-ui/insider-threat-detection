"""Generate a SMALL synthetic dataset in the CERT r4.2 CSV layout.

Output folder: logon.csv, device.csv, email.csv, file.csv, http.csv, answers.csv
Replace this folder with the real CERT r4.2 files to run the same pipeline.
Usage: python scripts/generate_synthetic_cert.py data/cert_synthetic --users 120 --days 90
"""
import argparse
import os
import random
import string
from datetime import datetime, timedelta

import pandas as pd

FMT = "%m/%d/%Y %H:%M:%S"
NORMAL_URLS = ["news.example.com/today", "intranet.dtaa.com/wiki", "search.example.com/q", "docs.dtaa.com/policy",
               "mail.dtaa.com/inbox", "stackoverflow.com/questions", "weather.example.com", "cnn.com/world"]
JOB_URLS = ["monster.com/jobs", "indeed.com/search", "linkedin.com/jobs"]
LEAK_URLS = ["wikileaks.org/submit", "dropbox.com/upload", "pastebin.com/new", "mega.nz/upload"]
NORMAL_FILES = [".doc", ".pdf", ".txt", ".xls", ".jpg"]


def eid(rng):
    return "{" + "".join(rng.choices(string.ascii_uppercase + string.digits, k=4)) + "-" + \
           "".join(rng.choices(string.ascii_uppercase + string.digits, k=8)) + "-" + \
           "".join(rng.choices(string.ascii_uppercase + string.digits, k=8)) + "}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--users", type=int, default=120)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--insiders", type=int, default=12)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    os.makedirs(a.out, exist_ok=True)

    start = datetime(2010, 1, 4)
    users = [f"U{str(i).zfill(4)}" for i in range(a.users)]
    prof = {u: dict(pc=f"PC-{1000 + i}", hour=rng.gauss(9, 0.8), usb=rng.random() < 0.1,
                    mails=rng.randint(1, 6), http=rng.randint(3, 12), files=rng.randint(1, 5),
                    job=rng.random() < 0.15) for i, u in enumerate(users)}
    insiders = rng.sample(users, a.insiders)
    # attack windows: one early (training period) and one in the validation or test period,
    # so every time-ordered split contains malicious sessions
    attacks = {}
    D = a.days
    for k, u in enumerate(insiders):
        late = (int(D * 0.72), int(D * 0.82)) if k % 2 == 0 else (int(D * 0.88), D - 6)
        wins = []
        for lo, hi in [(10, int(D * 0.62)), late]:
            s0 = rng.randint(lo, max(lo, hi - 4))
            wins.append((s0, s0 + rng.randint(2, 4)))
        attacks[u] = (rng.choice([1, 2]), wins)

    logon, device, email, files, http, answers = [], [], [], [], [], []

    def add(rows, row, kind=None, mal=False):
        rows.append(row)
        if mal:
            answers.append((kind, row[0]))

    for d in range(a.days):
        day = start + timedelta(days=d)
        if day.weekday() >= 5:
            continue
        for u in users:
            p = prof[u]
            if rng.random() < 0.06:  # absent
                continue
            scen, wins = attacks.get(u, (0, []))
            mal = any(w0 <= d <= w1 for w0, w1 in wins)
            subtle = mal and rng.random() < 0.3      # hard cases: normal hours, a single bad action
            hour = p["hour"] + rng.gauss(0, 0.5)
            if mal and not subtle:
                hour = rng.choice([rng.uniform(19, 23), rng.uniform(5, 6.5), p["hour"]])
            t0 = day + timedelta(hours=max(0, hour))
            dur = timedelta(hours=rng.gauss(8, 0.6) if not mal else rng.uniform(1.5, 5) if not subtle else rng.gauss(8, 0.6))
            t1 = t0 + dur
            pc = p["pc"]
            add(logon, (eid(rng), t0.strftime(FMT), u, pc, "Logon"), "logon", mal)
            if rng.random() > 0.03:  # 3% missing logoff
                add(logon, (eid(rng), t1.strftime(FMT), u, pc, "Logoff"), "logon", mal)

            def at():
                return (t0 + (t1 - t0) * rng.random()).strftime(FMT)

            for _ in range(max(0, int(rng.gauss(p["http"], 2)))):
                url = rng.choice(JOB_URLS) if p["job"] and rng.random() < 0.15 else rng.choice(NORMAL_URLS)
                add(http, (eid(rng), at(), u, pc, "http://" + url, "x"))
            for _ in range(max(0, int(rng.gauss(p["mails"], 1.5)))):
                ext = rng.random() < 0.08
                to = "friend@gmail.com" if ext else f"{rng.choice(users).lower()}@dtaa.com"
                add(email, (eid(rng), at(), u, pc, to, "", "", f"{u.lower()}@dtaa.com",
                            int(abs(rng.gauss(30000, 10000))), int(rng.random() < 0.15), "x"))
            for _ in range(max(0, int(rng.gauss(p["files"], 1.2)))):
                add(files, (eid(rng), at(), u, pc, f"C:\\docs\\f{rng.randint(1, 999)}{rng.choice(NORMAL_FILES)}", "x"))
            if p["usb"] and rng.random() < 0.15:
                a_t = at()
                add(device, (eid(rng), a_t, u, pc, "", "Connect"))
                add(device, (eid(rng), a_t, u, pc, "", "Disconnect"))

            if mal and scen == 1:  # data theft via USB and archives
                for _ in range(1 if subtle else rng.randint(1, 3)):
                    add(device, (eid(rng), at(), u, pc, "R1;R2", "Connect"), "device", True)
                for _ in range(rng.randint(1, 3) if subtle else rng.randint(8, 25)):
                    add(files, (eid(rng), at(), u, pc, f"R:\\copy\\x{rng.randint(1, 999)}.zip", "x"), "file", True)
                if rng.random() < 0.6:
                    add(http, (eid(rng), at(), u, pc, "http://" + rng.choice(JOB_URLS), "x"), "http", True)
            elif mal and scen == 2:  # leaking through uploads and external email
                for _ in range(1 if subtle else rng.randint(2, 6)):
                    add(http, (eid(rng), at(), u, pc, "http://" + rng.choice(LEAK_URLS), "x"), "http", True)
                for _ in range(1 if subtle else rng.randint(2, 5)):
                    add(email, (eid(rng), at(), u, pc, "drop@gmail.com", "", "", f"{u.lower()}@dtaa.com",
                                int(rng.uniform(800000, 4000000)), 3, "x"), "email", True)

    def save(name, cols, rows):
        pd.DataFrame(rows, columns=cols).to_csv(os.path.join(a.out, name), index=False)

    save("logon.csv", ["id", "date", "user", "pc", "activity"], logon)
    save("device.csv", ["id", "date", "user", "pc", "file_tree", "activity"], device)
    save("email.csv", ["id", "date", "user", "pc", "to", "cc", "bcc", "from", "size", "attachments", "content"], email)
    save("file.csv", ["id", "date", "user", "pc", "filename", "content"], files)
    save("http.csv", ["id", "date", "user", "pc", "url", "content"], http)
    save("answers.csv", ["activity_type", "id"], answers)
    print(f"{a.out}: {len(logon)+len(device)+len(email)+len(files)+len(http)} events, "
          f"{a.insiders} insiders, {len(answers)} malicious events")


if __name__ == "__main__":
    main()
