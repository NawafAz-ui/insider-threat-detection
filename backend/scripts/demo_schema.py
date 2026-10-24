"""Show that MongoDB enforces the schema: valid documents are accepted, invalid ones are rejected.
   python scripts/demo_schema.py        (run `python -m itd.schema apply` first)"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))   # lets "python scripts/x.py" find the itd package

from pymongo.errors import WriteError

from itd.db import get_db
from itd.schema import SCHEMAS, server_status, validate

db = get_db()
print("=== 1. Is validation active on the server? ===")
for coll, on in server_status(db).items():
    print(f"  {coll:18s} {'ON' if on else 'OFF  (run: python -m itd.schema apply)'}")

CASES = [
    ("A valid analyst account", "analyst_accounts", {"_id": "schema_demo_ok", "password_hash": "$2b$12$" + "a" * 53, "role": "analyst"}, True),
    ("Role that does not exist ('superuser')", "analyst_accounts", {"_id": "schema_demo_1", "password_hash": "$2b$12$" + "a" * 53, "role": "superuser"}, False),
    ("Plain-text password instead of a bcrypt hash", "analyst_accounts", {"_id": "schema_demo_2", "password_hash": "Password123", "role": "analyst"}, False),
    ("Access log with an unknown action", "access_log", {"at": time.time(), "user": "schema_demo", "action": "deleted_everything", "ip": None}, False),
    ("Access log with an over-long question (301 characters)", "access_log", {"at": time.time(), "user": "schema_demo", "action": "assistant_question", "ip": None, "question": "x" * 301}, False),
    ("A valid access-log entry", "access_log", {"at": time.time(), "user": "schema_demo", "action": "demo_entry", "ip": None}, True),
]
print("\n=== 2. Try to insert valid and invalid documents ===")
for title, coll, doc, expect_ok in CASES:
    local = validate(SCHEMAS[coll], doc, coll)
    try:
        res = db[coll].insert_one(dict(doc))
        outcome = "ACCEPTED" if expect_ok else "ACCEPTED (unexpected: validation is not active)"
        db[coll].delete_one({"_id": res.inserted_id})                       # clean up
    except WriteError as e:
        outcome = f"REJECTED by MongoDB (code {e.code})" if not expect_ok else f"REJECTED (unexpected): {e}"
    print(f"  {title}\n      rule check: {'valid' if not local else local[0]}\n      MongoDB:    {outcome}")

print("\n=== 3. An update that breaks a rule is rejected too ===")
db.analyst_accounts.delete_many({"_id": "schema_demo_upd"})
db.analyst_accounts.insert_one({"_id": "schema_demo_upd", "password_hash": "$2b$12$" + "a" * 53, "role": "analyst"})
try:
    db.analyst_accounts.update_one({"_id": "schema_demo_upd"}, {"$set": {"role": "root"}})
    print("  Changing the role to 'root': ACCEPTED (unexpected: validation is not active)")
except WriteError as e:
    print(f"  Changing the role to 'root': REJECTED by MongoDB (code {e.code})")
db.analyst_accounts.delete_many({"_id": "schema_demo_upd"})
print("\nDemo documents were removed again.")
