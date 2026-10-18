"""Manage analyst accounts (the analyst_accounts collection): create, read, update, delete.
   python -m scripts.analysts list
   python -m scripts.analysts add alice "Password1!" [analyst|admin]
   python -m scripts.analysts role alice admin
   python -m scripts.analysts password alice "NewPassword2!"
   python -m scripts.analysts delete alice"""
import sys
from itd.db import get_db
from itd.security import hash_password

ROLES = ("analyst", "admin")


def add(user, pw, role="analyst"):
    assert role in ROLES, f"role must be one of {ROLES}"
    get_db().analyst_accounts.insert_one({"_id": user, "password_hash": hash_password(pw), "role": role})


def list_all():
    return [{"username": d["_id"], "role": d["role"]} for d in get_db().analyst_accounts.find().sort("_id", 1)]


def set_role(user, role):
    assert role in ROLES, f"role must be one of {ROLES}"
    return get_db().analyst_accounts.update_one({"_id": user}, {"$set": {"role": role}}).matched_count


def set_password(user, pw):
    return get_db().analyst_accounts.update_one({"_id": user}, {"$set": {"password_hash": hash_password(pw)}}).matched_count


def delete(user):
    return get_db().analyst_accounts.delete_one({"_id": user}).deleted_count


if __name__ == "__main__":
    cmd, args = (sys.argv[1] if len(sys.argv) > 1 else "list"), sys.argv[2:]
    if cmd == "list":
        for a in list_all():
            print(f"{a['username']:20s} {a['role']}")
    elif cmd == "add":
        add(*args); print("created", args[0])
    elif cmd == "role":
        print("updated" if set_role(*args) else "no such user")
    elif cmd == "password":
        print("updated" if set_password(*args) else "no such user")
    elif cmd == "delete":
        print("deleted" if delete(*args) else "no such user")
    else:
        print(__doc__)
