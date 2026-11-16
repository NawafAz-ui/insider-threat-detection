"""Preprocess a dataset folder exactly as the engine does, but stop before the database and the models:
input check (rules V1 to V10), sessions, events per session, features, baselines and the time-ordered
split (config.SPLIT: 80% training, 20% test, no validation part). Nothing is written to MongoDB and no
model is trained.
   python scripts/prepare_split.py <dataset folder> <output folder>
Writes train.csv.gz and test.csv.gz (one row per session) and summary.json."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from itd import validate  # noqa: E402
from itd.baselines import add_deviations  # noqa: E402
from itd.features import FEATURES, session_features  # noqa: E402
from itd.ingest import FILES, data_file, iter_chunks, load_dataset  # noqa: E402
from itd.models import time_split  # noqa: E402
from itd.sessionize import assign_events  # noqa: E402


def main(src, out):
    os.makedirs(out, exist_ok=True)
    t0 = time.time()
    check = validate.validate_folder(src)
    print(validate.format_report(check), flush=True)
    if check["status"] == "failed":
        raise SystemExit("Input validation failed; nothing was prepared.")
    t1 = time.time()
    sessions, agg = load_dataset(src)
    # the aggregator counts only Connect events for devices, so count every kept device event here
    device_kept = sum(len(assign_events(sessions, c)) for c in iter_chunks(data_file(src, "device"), FILES["device"]))
    feats, _ = add_deviations(session_features(sessions, agg), None)
    tr, te = time_split(len(feats))
    t2 = time.time()
    assert feats["start"].is_monotonic_increasing and len(tr) + len(te) == len(feats)

    bad = feats["label"] == 1
    summary = {
        "dataset": os.path.abspath(src), "created": time.strftime("%Y-%m-%d %H:%M:%S"),
        "validation": check,
        "sessions": {"total": len(feats), "malicious": int(bad.sum()), "users": int(feats["user"].nunique()),
                     "malicious_users": int(feats.loc[bad, "user"].nunique()), "pcs": int(feats["pc"].nunique()),
                     "first_start": str(feats["start"].min()), "last_start": str(feats["start"].max()),
                     "logoff_missing": int(feats["logoff_missing"].sum())},
        "events_in_sessions": {"logon": check["rows"].get("logon"), "device": int(device_kept),
                               "file": int(feats["n_file_events"].sum()), "email": int(feats["n_email_sent"].sum()),
                               "http": int(feats["n_http"].sum())},
        "features": FEATURES, "columns_written": list(feats.columns), "split": {},
    }
    for name, idx in (("train", tr), ("test", te)):
        part = feats.iloc[idx]
        path = os.path.join(out, f"{name}.csv.gz")
        part.to_csv(path)
        summary["split"][name] = {
            "sessions": len(part), "malicious": int(part["label"].sum()), "malicious_pct": round(100 * part["label"].mean(), 3),
            "users": int(part["user"].nunique()), "malicious_users": int(part.loc[part["label"] == 1, "user"].nunique()),
            "first_start": str(part["start"].min()), "last_start": str(part["start"].max()),
            "file": os.path.basename(path), "bytes": os.path.getsize(path)}
        print(f"{name}: {len(part):,} sessions, {int(part['label'].sum())} malicious", flush=True)
    summary["engine_can_train"] = summary["split"]["train"]["malicious"] >= 2 and summary["split"]["test"]["malicious"] > 0
    summary["seconds"] = {"validation": round(t1 - t0, 1), "preprocessing": round(t2 - t1, 1), "writing": round(time.time() - t2, 1)}
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
