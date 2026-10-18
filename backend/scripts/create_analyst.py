"""Create or update an analyst account.  python -m scripts.create_analyst alice 'S3cret!' [analyst|admin]"""
import sys
from itd.db import get_db
from itd.security import hash_password

if __name__ == "__main__":
    user, pw = sys.argv[1], sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else "analyst"
    get_db().analyst_accounts.replace_one({"_id": user}, {"_id": user, "password_hash": hash_password(pw), "role": role}, upsert=True)
    print(f"Account '{user}' saved with role '{role}'.")
