"""Exploratory cross-dataset evaluation: train on CERT, test on SPEDIA (converted with itd.spedia),
using only the features that vary in BOTH datasets.
   python -m itd.cross_eval --train data/cert_synthetic --test data/spedia_cert"""
import argparse
import json
import os
import numpy as np
from .baselines import add_deviations
from .features import FEATURES, session_features
from .ingest import load_dataset
from .models import score_models, time_split, train_models
from .risk import combine, evaluate, evaluate_model, fit_risk_engine


def build(folder):
    s, agg = load_dataset(folder, pseudonymize=False, log=lambda *a, **k: None)
    f, _ = add_deviations(session_features(s, agg))
    return f


def run(train_dir, test_dir, report_dir="reports"):
    a, b = build(train_dir), build(test_dir)
    shared = [f for f in FEATURES if a[f].nunique() > 1 and b[f].nunique() > 1]
    dropped = [f for f in FEATURES if f not in shared]
    print(f"Shared features used: {len(shared)} of {len(FEATURES)}. Dropped (constant in one dataset): {dropped}")
    Xa, ya = a[shared].to_numpy(float), a["label"].to_numpy(int)
    tr, va, te = time_split(len(a))
    models, extra = train_models(Xa[tr], ya[tr])
    cfg = fit_risk_engine(score_models(models, extra, Xa[va]), ya[va])

    def evaluate_on(X, y):
        sc = score_models(models, extra, X)
        r = combine(sc, cfg["weights"])
        return {"sessions": int(len(y)), "malicious_share": float(y.mean()),
                "risk_engine": evaluate(y, r, cfg["threshold"]), **{k: evaluate_model(y, v) for k, v in sc.items()}}

    res = {"note": "EXPLORATORY: trained on the first dataset, tested on the second with shared features only.",
           "shared_features": shared, "dropped_features": dropped,
           "same_dataset_test": evaluate_on(Xa[te], ya[te]),
           "cross_dataset_test": evaluate_on(b[shared].to_numpy(float), b["label"].to_numpy(int))}
    os.makedirs(report_dir, exist_ok=True)
    with open(os.path.join(report_dir, "cross_dataset.json"), "w") as f:
        json.dump(res, f, indent=2)
    for name in ("same_dataset_test", "cross_dataset_test"):
        r = res[name]
        print(f"\n{name}: {r['sessions']:,} sessions, {r['malicious_share']:.1%} malicious")
        for k in ("risk_engine", "lr", "xgb", "iforest"):
            m = r[k]
            print(f"  {k:12s} precision {m.get('precision', 0):.2f}  recall {m.get('recall', 0):.2f}  F1 {m.get('f1', 0):.2f}  PR-AUC {m.get('pr_auc') or 0:.2f}")
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True)
    ap.add_argument("--test", required=True)
    ap.add_argument("--report", default="reports")
    x = ap.parse_args()
    run(x.train, x.test, x.report)
