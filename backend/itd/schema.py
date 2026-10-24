"""Database schema: validation rules ($jsonSchema), indexes and a checker. Run once by an administrator:
    python -m itd.schema apply     create/update the collections with validation rules and indexes
    python -m itd.schema check     check every stored document against the rules and show server status
MongoDB then rejects documents that break the rules (for example a role other than analyst/admin)."""
import re
import sys
from datetime import datetime

from bson import ObjectId

from .features import BASE_METRICS, FEATURES

NUM = "number"                      # MongoDB: int, long or double
UNIT = {"bsonType": NUM, "minimum": 0, "maximum": 1}
SESSION_ID = {"bsonType": "string", "pattern": "^S[0-9]{1,12}$"}
USER = {"bsonType": "string", "minLength": 1, "maxLength": 64}
ACTIONS = ["login_ok", "login_failed", "session_viewed", "user_viewed", "assistant_question", "demo_entry"]


def obj(required, props, extra_ok=True):
    return {"bsonType": "object", "required": required, "properties": props}


SCHEMAS = {
    "results": obj(
        ["_id", "session_id", "run_id", "user", "pc", "start", "end", "risk_score", "flagged", "model_scores",
         "top_shap", "baseline_deviations", "label", "split"],
        {"_id": SESSION_ID, "session_id": SESSION_ID, "run_id": {"bsonType": "objectId"}, "user": USER,
         "pc": {"bsonType": "string", "minLength": 1}, "start": {"bsonType": "date"}, "end": {"bsonType": "date"},
         "risk_score": {"bsonType": NUM, "minimum": 0, "maximum": 100}, "flagged": {"bsonType": "bool"},
         "model_scores": obj(["lr", "xgb", "iforest"], {"lr": UNIT, "xgb": UNIT, "iforest": UNIT}),
         "top_shap": {"bsonType": "array", "maxItems": 3, "items": obj(
             ["feature", "value", "shap", "strength", "text"],
             {"feature": {"bsonType": "string"}, "value": {"bsonType": NUM}, "shap": {"bsonType": NUM},
              "strength": {"enum": ["strong", "minor"]}, "text": {"bsonType": "string"}})},
         "baseline_deviations": {"bsonType": "array", "maxItems": 3, "items": obj(
             ["metric", "value", "user_mean", "user_std", "z", "text"],
             {"metric": {"enum": BASE_METRICS}, "value": {"bsonType": NUM}, "user_mean": {"bsonType": NUM},
              "user_std": {"bsonType": NUM}, "z": {"bsonType": NUM, "minimum": 0, "maximum": 10},
              "text": {"bsonType": "string"}})},
         "label": {"enum": [0, 1]}, "split": {"enum": ["train", "validation", "test"]}}),
    "user_baselines": obj(
        ["_id", "n", "mean", "m2"],
        {"_id": USER, "n": {"bsonType": NUM, "minimum": 1},
         "mean": obj(BASE_METRICS, {m: {"bsonType": NUM} for m in BASE_METRICS}),
         "m2": obj(BASE_METRICS, {m: {"bsonType": NUM, "minimum": 0} for m in BASE_METRICS})}),
    "analyst_accounts": obj(
        ["_id", "password_hash", "role"],
        {"_id": {"bsonType": "string", "pattern": "^[A-Za-z0-9_.-]{1,64}$"},
         "password_hash": {"bsonType": "string", "pattern": "^\\$2[aby]\\$[0-9]{2}\\$"},     # bcrypt hash, never a plain password
         "role": {"enum": ["analyst", "admin"]}}),
    "access_log": obj(
        ["at", "user", "action"],
        {"at": {"bsonType": NUM, "minimum": 0}, "user": {"bsonType": "string", "minLength": 1, "maxLength": 64},
         "action": {"enum": ACTIONS}, "ip": {"bsonType": ["string", "null"]},
         "session_id": SESSION_ID, "viewed_user": USER, "question": {"bsonType": "string", "maxLength": 300}}),
    "runs": obj(
        ["_id", "at", "seconds", "sessions", "flagged", "threshold", "weights"],
        {"_id": {"bsonType": "objectId"}, "at": {"bsonType": NUM, "minimum": 0}, "seconds": {"bsonType": NUM, "minimum": 0},
         "sessions": {"bsonType": NUM, "minimum": 0}, "flagged": {"bsonType": NUM, "minimum": 0},
         "threshold": {"bsonType": NUM, "minimum": 0, "maximum": 100},
         "weights": obj(["lr", "xgb", "iforest"], {"lr": UNIT, "xgb": UNIT, "iforest": UNIT}),
         "step_seconds": {"bsonType": "object"}, "metrics": {"bsonType": ["object", "null"]}}),
    "trained_models": obj(
        ["_id", "files", "sha256", "risk", "features", "trained_at"],
        {"_id": {"bsonType": "string"},
         "files": obj(["lr", "xgb", "iforest"], {k: {"bsonType": "objectId"} for k in ("lr", "xgb", "iforest")}),
         "sha256": obj(["lr", "xgb", "iforest"], {k: {"bsonType": "string", "pattern": "^[0-9a-f]{64}$"} for k in ("lr", "xgb", "iforest")}),
         "risk": obj(["weights", "threshold"], {"threshold": {"bsonType": NUM, "minimum": 0, "maximum": 100}}),
         "features": {"bsonType": "array", "minItems": len(FEATURES), "maxItems": len(FEATURES), "items": {"bsonType": "string"}},
         "trained_at": {"bsonType": NUM}}),
}

# (keys, options). Why: the flagged list, the user page, login throttling, newest-run lookups.
INDEXES = {
    "results": [([("flagged", 1), ("risk_score", -1)], {}), ([("user", 1), ("start", 1)], {})],
    "access_log": [([("action", 1), ("user", 1), ("at", -1)], {"name": "throttle_by_user"}),
                   ([("action", 1), ("ip", 1), ("at", -1)], {"name": "throttle_by_ip"}),
                   ([("at", -1)], {"name": "newest_first"})],
    "runs": [([("at", -1)], {"name": "latest_run"})],
}


# ---- a small checker with the same rules, so documents can be checked without a server -------------------
def _is(v, t):
    return {"string": lambda: isinstance(v, str), "bool": lambda: isinstance(v, bool), "date": lambda: isinstance(v, datetime),
            "object": lambda: isinstance(v, dict), "array": lambda: isinstance(v, (list, tuple)), "null": lambda: v is None,
            "objectId": lambda: isinstance(v, ObjectId),
            NUM: lambda: isinstance(v, (int, float)) and not isinstance(v, bool)}[t]()


def validate(schema: dict, value, path="doc") -> list:
    """Return a list of problems (empty = valid). Supports the keywords used in SCHEMAS."""
    errs = []
    types = schema.get("bsonType")
    if types is not None and not any(_is(value, t) for t in ([types] if isinstance(types, str) else types)):
        return [f"{path}: expected {types}, got {type(value).__name__}"]
    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} is not one of {schema['enum'][:6]}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errs.append(f"{path}: {value} is below {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errs.append(f"{path}: {value} is above {schema['maximum']}")
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errs.append(f"{path}: too short")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errs.append(f"{path}: longer than {schema['maxLength']} characters")
        if "pattern" in schema and not re.search(schema["pattern"], value):
            errs.append(f"{path}: does not match the required pattern")
    if isinstance(value, dict):
        for k in schema.get("required", []):
            if k not in value:
                errs.append(f"{path}: missing '{k}'")
        for k, sub in schema.get("properties", {}).items():
            if k in value:
                errs += validate(sub, value[k], f"{path}.{k}")
    if isinstance(value, (list, tuple)):
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errs.append(f"{path}: more than {schema['maxItems']} items")
        if "minItems" in schema and len(value) < schema["minItems"]:
            errs.append(f"{path}: fewer than {schema['minItems']} items")
        for i, item in enumerate(value):
            if "items" in schema:
                errs += validate(schema["items"], item, f"{path}[{i}]")
    return errs


# ---- administrator commands --------------------------------------------------------------------------------
def apply(db) -> dict:
    """Create or update every collection with its validation rules, then create the indexes."""
    existing = set(db.list_collection_names())
    for name, schema in SCHEMAS.items():
        opts = dict(validator={"$jsonSchema": schema}, validationLevel="strict", validationAction="error")
        if name in existing:
            db.command("collMod", name, **opts)
        else:
            db.create_collection(name, **opts)
    made = {}
    for name, specs in INDEXES.items():
        made[name] = [db[name].create_index(keys, **o) for keys, o in specs]
    return made


def server_status(db) -> dict:
    """For each collection: is a validator active on the server?"""
    out = {}
    for info in db.list_collections():
        if info["name"] in SCHEMAS:
            opt = info.get("options", {})
            out[info["name"]] = bool(opt.get("validator")) and opt.get("validationAction") == "error"
    return out


def check(db, limit=20000) -> dict:
    """Check stored documents against the rules. Returns {collection: (checked, [problems])}."""
    res = {}
    for name, schema in SCHEMAS.items():
        bad, n = [], 0
        for doc in db[name].find().limit(limit):
            n += 1
            for e in validate(schema, doc, name):
                bad.append((doc.get("_id"), e))
        res[name] = (n, bad)
    return res


def main(argv):
    from .db import get_db
    db = get_db()
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "apply":
        for coll, names in apply(db).items():
            print(f"  indexes on {coll}: {', '.join(names)}")
        for coll, on in server_status(db).items():
            print(f"  {coll:18s} validation {'ON' if on else 'off'}")
        print("Schema applied. Documents that break the rules are now rejected by MongoDB.")
    elif cmd == "check":
        active, bad_total = server_status(db), 0
        for coll, (n, bad) in check(db).items():
            bad_total += len(bad)
            print(f"  {coll:18s} {n:>8,} documents checked, {len(bad)} problem(s); server validation {'ON' if active.get(coll) else 'off'}")
            for _id, e in bad[:3]:
                print(f"      {_id}: {e}")
        print("All stored documents follow the rules." if not bad_total else f"{bad_total} problem(s) found. Re-run the engine with --retrain to rebuild the results.")
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv)
