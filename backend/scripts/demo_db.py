"""Database demo: shows every collection, then Create / Read / Update / Delete on one analyst account.
   python scripts/demo_db.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # lets "python scripts/x.py" find the itd package
import json
import time
from itd.db import get_db, get_fs
from itd.security import check_password, hash_password


def short(doc, limit=600):
    return (json.dumps(doc, indent=2, default=str)[:limit] + " ...") if len(json.dumps(doc, default=str)) > limit else json.dumps(doc, indent=2, default=str)


def main():
    db = get_db()
    print("=== 1. Collections and document counts ===")
    for name in ["results", "trained_models", "user_baselines", "analyst_accounts", "access_log", "runs", "fs.files", "fs.chunks"]:
        print(f"  {name:18s} {db[name].count_documents({}):>8,}")
    print("\n  results index:", [i["name"] for i in db.results.list_indexes()])

    print("\n=== 2. One document from each main collection ===")
    r = db.results.find_one({"flagged": True}, sort=[("risk_score", -1)])
    print("results (highest risk):\n" + short(r))
    b = db.user_baselines.find_one()
    print("\nuser_baselines:\n" + short({"_id": b["_id"], "n": b["n"], "mean": dict(list(b["mean"].items())[:3]), "...": "10 metrics in total"}) if b else "user_baselines: empty")
    m = db.trained_models.find_one({"_id": "current"})
    if m:
        print("\ntrained_models (models themselves are in GridFS):\n" + short({"files": list(m["files"]), "sha256": {k: v[:12] + "..." for k, v in m["sha256"].items()},
                                                                    "weights": m["risk"]["weights"], "threshold": m["risk"]["threshold"]}))
    a = db.analyst_accounts.find_one({}, {"password_hash": 0})
    print("\nanalyst_accounts (password hash hidden):\n" + short(a))

    print("\n=== 3. CRUD on analyst_accounts (temporary account 'demo_user') ===")
    col = db.analyst_accounts
    col.delete_many({"_id": "demo_user"})
    col.insert_one({"_id": "demo_user", "password_hash": hash_password("First-Pass1!"), "role": "analyst"})
    print("CREATE  inserted demo_user")
    d = col.find_one({"_id": "demo_user"})
    print(f"READ    role={d['role']}, password stored as bcrypt hash ({d['password_hash'][:7]}...), old password checks: {check_password('First-Pass1!', d['password_hash'])}")
    col.update_one({"_id": "demo_user"}, {"$set": {"role": "admin", "password_hash": hash_password("Second-Pass2!")}})
    d = col.find_one({"_id": "demo_user"})
    print(f"UPDATE  role={d['role']}, old password still works: {check_password('First-Pass1!', d['password_hash'])}, new password works: {check_password('Second-Pass2!', d['password_hash'])}")
    col.delete_one({"_id": "demo_user"})
    print(f"DELETE  demo_user exists afterwards: {col.find_one({'_id': 'demo_user'}) is not None}")

    print("\n=== 4. Access log: the API's only write ===")
    db.access_log.insert_one({"at": time.time(), "user": "demo_db", "action": "demo_entry", "ip": "local"})
    for e in db.access_log.find().sort("at", -1).limit(5):
        print(f"  {time.strftime('%H:%M:%S', time.localtime(e['at']))}  {e.get('user', ''):10s} {e['action']}")
    db.access_log.delete_many({"action": "demo_entry"})


if __name__ == "__main__":
    main()
