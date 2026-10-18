"""Backup every collection (and GridFS model files) to BSON files; restore with --restore.
Schedule it (Windows Task Scheduler / cron) for the 'scheduled database backups' mitigation.
   python scripts/backup_db.py --out backups            python scripts/backup_db.py --restore backups/2010-01-01_0300"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # lets "python scripts/x.py" find the itd package
import argparse
import time
import bson
from itd.db import get_db


def backup(out):
    db = get_db()
    folder = os.path.join(out, time.strftime("%Y-%m-%d_%H%M"))
    os.makedirs(folder, exist_ok=True)
    for name in db.list_collection_names():
        with open(os.path.join(folder, f"{name}.bson"), "wb") as f:
            n = 0
            for doc in db[name].find():
                f.write(bson.encode(doc)); n += 1
        print(f"  {name}: {n} documents")
    print("Backup written to", folder)
    return folder


def restore(folder):
    db = get_db()
    for fn in os.listdir(folder):
        if fn.endswith(".bson"):
            name = fn[:-5]
            with open(os.path.join(folder, fn), "rb") as f:
                docs = bson.decode_all(f.read())
            db[name].delete_many({})
            if docs:
                db[name].insert_many(docs)
            print(f"  restored {name}: {len(docs)} documents")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="backups")
    ap.add_argument("--restore")
    a = ap.parse_args()
    restore(a.restore) if a.restore else backup(a.out)
