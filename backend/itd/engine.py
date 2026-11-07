"""Detection Engine (batch). Usage:  python -m itd.engine --data data/cert_synthetic [--retrain]
Steps: ingest -> sessionize -> features/baselines -> train once (or load) -> score -> risk + SHAP -> MongoDB.
Only this component writes models, baselines, thresholds and results."""
import argparse
import hashlib
import json
import os
import time
import numpy as np
from bson import ObjectId
from sklearn.metrics import brier_score_loss
from . import config
from .baselines import add_deviations
from .db import get_db, get_fs
from .explain import shap_values, top_baseline_deviations, top_shap
from .features import FEATURES, session_features
from .ingest import load_dataset
from . import rules
from . import validate
from .models import dumps, loads, score_models, time_split, train_models
from .risk import calibrate, combine, evaluate, evaluate_model, fit_risk_engine

BLOCK = 50_000


class ModelIntegrityError(RuntimeError):
    pass


def save_models(models, extra, risk_cfg, metrics):
    db, fs = get_db(), get_fs()
    for old in db.trained_models.find({}, {"files": 1}):
        for fid in old.get("files", {}).values():
            fs.delete(fid)
    db.trained_models.delete_many({})
    blobs = {name: dumps(m) for name, m in models.items()}
    files = {name: fs.put(b, filename=f"{name}.joblib") for name, b in blobs.items()}
    hashes = {name: hashlib.sha256(b).hexdigest() for name, b in blobs.items()}   # tamper check
    db.trained_models.insert_one({"_id": "current", "files": files, "sha256": hashes, "extra": extra, "risk": risk_cfg,
                                  "features": FEATURES, "metrics": metrics, "trained_at": time.time()})


def load_models():
    db, fs = get_db(), get_fs()
    doc = db.trained_models.find_one({"_id": "current"})
    if not doc:
        return None
    models = {}
    for n, fid in doc["files"].items():
        blob = fs.get(fid).read()
        if hashlib.sha256(blob).hexdigest() != doc.get("sha256", {}).get(n):
            raise ModelIntegrityError(f"Saved model '{n}' failed its integrity check; it may have been changed. Retrain with --retrain.")
        models[n] = loads(blob)
    return models, doc["extra"], doc["risk"], doc.get("metrics", {})


def run(data_dir, retrain=False, report_dir="reports", pseudonymize=None):
    T = {}
    run_id = ObjectId()                                             # links every result to this batch run
    t0 = time.time()
    print("0/5 Input validation ...")
    check = validate.validate_folder(data_dir)
    print(validate.format_report(check))
    if check["status"] == "failed":
        raise SystemExit("Input validation failed; fix the errors above and run again.")
    db = get_db()

    def step(name, since):
        T[name] = round(time.time() - since, 1)
        return time.time()

    print("1-2/5 Ingestion and sessionization (chunked) ...")
    t = time.time()
    sessions, agg = load_dataset(data_dir, pseudonymize)
    print(f"    {len(sessions):,} sessions, {int(sessions.label.sum())} malicious")
    t = step("ingestion_and_sessions", t)
    print(f"3/5 Behavioral analytics ({len(FEATURES)} features + baselines) ...")
    feats = session_features(sessions, agg)
    prior = None
    if not retrain and db.user_baselines.count_documents({}):
        prior = {d["_id"]: d for d in db.user_baselines.find()}
    feats, final = add_deviations(feats, prior)
    X, y = feats[FEATURES].to_numpy(float), feats["label"].to_numpy(int)
    tr, va, te = time_split(len(feats))
    t = step("features_and_baselines", t)

    print("4/5 ML models ...")
    loaded = None if retrain else load_models()
    if loaded is None:
        if y[tr].sum() == 0 or y[va].sum() == 0 or y[te].sum() == 0:
            raise SystemExit("Each of train/validation/test needs at least one malicious session.")
        models, extra = train_models(X[tr], y[tr])
        risk_cfg = fit_risk_engine(score_models(models, extra, X[va]), y[va])
        save_models(models, extra, risk_cfg, {"validation_f1": risk_cfg["val_f1"]})
        models, extra, risk_cfg, metrics = load_models()      # trained once, saved, then loaded to score
    else:
        models, extra, risk_cfg, metrics = loaded
    t = step("models", t)

    print("5/5 Risk engine + SHAP ...")
    raw = score_models(models, extra, X)
    # models saved before calibration was added have no calibrators and keep scoring with raw scores
    scores = calibrate(raw, risk_cfg["calibrators"]) if risk_cfg.get("calibrators") else raw
    risk = combine(scores, risk_cfg["weights"])
    thr = risk_cfg["threshold"]
    if loaded is None:  # test-set evaluation (never used for tuning: every threshold comes from validation data)
        metrics["test"] = {"risk_engine": {**evaluate(y[te], risk[te], thr), "brier": float(brier_score_loss(y[te], risk[te] / 100))},
                           **{k: evaluate_model(y[te], scores[k][te], risk_cfg["val_thresholds"][k], raw[k][te]) for k in scores}}
        metrics["test"].update(rules.reference_metrics(feats, y, va, te))      # simple reference methods, thresholds from validation data
        metrics["sizes"] = {"train": len(tr), "validation": len(va), "test": len(te)}
        db.trained_models.update_one({"_id": "current"}, {"$set": {"metrics": metrics}})
    splits = np.empty(len(feats), dtype=object)
    if loaded is None:
        splits[tr], splits[va], splits[te] = "train", "validation", "test"
    else:                                   # a saved model never saw this batch: its time parts mean nothing here
        splits[:] = "scored"

    ids = feats.index.to_numpy()
    cols = ["user", "pc", "start", "end", "label"] + [c for c in feats.columns if c.startswith(("mean_", "std_", "dev_"))] + \
           [m for m in set(FEATURES) | set(m[4:] for m in FEATURES if m.startswith("dev_"))]
    cols = list(dict.fromkeys(c for c in cols if c in feats.columns))
    flagged = 0
    for a in range(0, len(feats), BLOCK):
        b = min(a + BLOCK, len(feats))
        sv = shap_values(models["xgb"], X[a:b])
        rows = feats[cols].iloc[a:b].to_dict("records")
        docs = []
        for k, row in enumerate(rows):
            i = a + k
            fl = bool(risk[i] >= thr)
            flagged += fl
            docs.append({"_id": ids[i], "session_id": ids[i], "run_id": run_id, "user": row["user"], "pc": row["pc"],
                         "start": row["start"].to_pydatetime(), "end": row["end"].to_pydatetime(),
                         "risk_score": round(float(risk[i]), 1), "flagged": fl,
                         "model_scores": {m: round(float(v[i]), 4) for m, v in scores.items()},
                         "top_shap": top_shap(sv[k], X[i], row), "baseline_deviations": top_baseline_deviations(row),
                         "label": int(row["label"]), "split": splits[i]})
        db.results.delete_many({"_id": {"$in": [d["_id"] for d in docs]}})      # same ids from an earlier run are replaced
        db.results.insert_many(docs)
    db.results.delete_many({"run_id": {"$ne": run_id}})            # old results go only after the new ones are saved
    db.results.create_index([("flagged", 1), ("risk_score", -1)])
    db.results.create_index([("user", 1), ("start", 1)])          # user history page
    t = step("risk_and_shap", t)
    db.user_baselines.delete_many({})
    items = [{"_id": u, **v} for u, v in final.items()]
    for a in range(0, len(items), 5000):
        db.user_baselines.insert_many(items[a:a + 5000])
    step("save_baselines", t)

    info = {"seconds": round(time.time() - t0, 1), "step_seconds": T, "sessions": len(feats), "flagged": int(flagged),
            "threshold": thr, "weights": risk_cfg["weights"], "at": time.time(), "validation": check["summary"],
            "metrics": {"test": metrics.get("test"), "sizes": metrics.get("sizes"), "validation_f1": risk_cfg.get("val_f1"),
                        "validation_thresholds": risk_cfg.get("val_thresholds"), "calibrators": risk_cfg.get("calibrators")}}
    db.runs.insert_one({"_id": run_id, **info})
    os.makedirs(report_dir, exist_ok=True)
    with open(os.path.join(report_dir, "metrics.json"), "w") as f:
        json.dump({"run": {k: v for k, v in info.items() if k not in ("at", "metrics")}, **metrics}, f, indent=2, default=str)
    with open(os.path.join(report_dir, "validation.json"), "w") as f:
        json.dump(check, f, indent=2)
    print_summary(info, risk_cfg, metrics)
    return {**info, "run_id": run_id}


def print_summary(info, risk_cfg, metrics):
    print(f"\nDone in {info['seconds']} s ({info['step_seconds']}): {info['sessions']:,} sessions, {info['flagged']:,} flagged")
    print("Weights:", {k: round(v, 3) for k, v in risk_cfg["weights"].items()}, "| threshold:", round(risk_cfg["threshold"], 1))
    t = metrics.get("test")
    if t:
        print(f"{'model':12s} {'prec':>6s} {'recall':>7s} {'F1':>6s} {'PR-AUC':>7s} {'Brier':>7s}   (test set)")
        for k, m in t.items():
            print(f"{k:12s} {m.get('precision', 0):6.2f} {m.get('recall', 0):7.2f} {m.get('f1', 0):6.2f} {m.get('pr_auc') or 0:7.2f} {m.get('brier') or 0:7.3f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="folder with logon/device/email/file/http/answers CSV files")
    ap.add_argument("--retrain", action="store_true", help="train new models and rebuild baselines")
    ap.add_argument("--pseudonymize", action="store_true", help="replace user ids with keyed hashes (PSEUDONYM_KEY)")
    ap.add_argument("--report", default="reports")
    a = ap.parse_args()
    run(a.data, a.retrain, a.report, True if a.pseudonymize else None)
