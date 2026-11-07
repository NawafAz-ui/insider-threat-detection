"""Matched experiments A to D of the methodology (docs/EVALUATION_CRITERIA.md) on generated CERT-layout data.
No database is used. Every seed makes a new data set; every threshold is chosen on the validation part and the
results are read on the time-ordered test part. Generated data is easier than real logs: not a research finding.
   python scripts/run_experiments.py [--seeds 5] [--users 120 --days 90 --insiders 12] [--report reports]
A: single models.  B: feature groups.  C: best single model vs equal weights vs F1 weights.  D: raw vs calibrated."""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)         # lets "python scripts/x.py" find the itd package

from sklearn.metrics import brier_score_loss

from itd.baselines import add_deviations
from itd.features import DEV_FEATURES, FEATURES, SESSION_FEATURES, session_features
from itd.ingest import load_dataset
from itd.models import score_models, time_split, train_models
from itd.risk import best_f1, calibrate, combine, evaluate, fit_risk_engine
from itd.rules import RULE_NAMES, reference_metrics

FEATURE_SETS = {"28 session features": SESSION_FEATURES, "plus 10 deviations": SESSION_FEATURES + DEV_FEATURES,
                "plus recency (all 39)": FEATURES}
TOP_K = 20                 # analyst budget: the 20 highest-scored sessions of the test part
NAMES = {"lr": "Logistic Regression", "xgb": "XGBoost", "iforest": "Isolation Forest"}


def make_frame(seed, args, folder):
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts", "generate_synthetic_cert.py"), folder, "--users", str(args.users),
                           "--days", str(args.days), "--insiders", str(args.insiders), "--seed", str(seed)], stdout=subprocess.DEVNULL)
    sessions, agg = load_dataset(folder, pseudonymize=False, log=lambda *a, **k: None)
    return add_deviations(session_features(sessions, agg))[0]


def split_scores(f, cols):
    X, y = f[cols].to_numpy(float), f["label"].to_numpy(int)
    tr, va, te = time_split(len(f))
    if min(y[tr].sum(), y[va].sum(), y[te].sum()) == 0:
        return None
    models, extra = train_models(X[tr], y[tr])
    return score_models(models, extra, X[va]), y[va], score_models(models, extra, X[te]), y[te]


def at_validation_threshold(val_risk, y_val, test_risk, y_test):
    """Test metrics at the threshold that is best on validation data (risk values on a 0 to 100 scale)."""
    m = evaluate(y_test, test_risk, best_f1(y_val, val_risk)[1])
    benign = len(y_test) - int(y_test.sum())
    top = np.argsort(-test_risk, kind="stable")[:TOP_K]
    return {**m, "fp_per_1000_benign": 1000 * m["flagged"] * (1 - m["precision"]) / benign,
            "alerts_per_1000": 1000 * m["flagged"] / len(y_test), f"recall_top_{TOP_K}": float(y_test[top].sum() / y_test.sum()),
            "brier": float(brier_score_loss(y_test, np.clip(test_risk / 100, 0, 1)))}


def ensemble(pv, yv, pt, yt, weights):
    return at_validation_threshold(combine(pv, weights), yv, combine(pt, weights), yt)


def one_seed(f):
    out = {"A": {}, "B": {}, "C": {}, "D": {}, "F": {}}
    for label, cols in FEATURE_SETS.items():
        s = split_scores(f, cols)
        if s is None:
            return None
        raw_v, yv, raw_t, yt = s
        cfg = fit_risk_engine(raw_v, yv)
        pv, pt = calibrate(raw_v, cfg["calibrators"]), calibrate(raw_t, cfg["calibrators"])
        out["B"][label] = ensemble(pv, yv, pt, yt, cfg["weights"])
        if cols is not FEATURES:
            continue
        for k in pv:                                                         # A: each model, calibrated
            out["A"][NAMES[k]] = at_validation_threshold(pv[k] * 100, yv, pt[k] * 100, yt)
        best = max(cfg["val_f1"], key=cfg["val_f1"].get)                      # C
        out["C"][f"best single model ({NAMES[best]})"] = ensemble(pv, yv, pt, yt, {k: float(k == best) for k in pv})
        out["C"]["equal weights"] = ensemble(pv, yv, pt, yt, {k: 1 / len(pv) for k in pv})
        out["C"]["weights from validation F1"] = out["B"][label]
        raw_f1 = {k: best_f1(yv, v)[0] for k, v in raw_v.items()}            # D: same weights rule, raw scores
        out["D"]["raw scores"] = ensemble(raw_v, yv, raw_t, yt, {k: v / sum(raw_f1.values()) for k, v in raw_f1.items()})
        out["D"]["calibrated scores"] = out["B"][label]
    tr, va, te = time_split(len(f))                                          # F: simple reference methods
    out["F"]["combined risk score (all 39 features)"] = out["B"]["plus recency (all 39)"]
    for key, m in reference_metrics(f, f["label"].to_numpy(int), va, te).items():
        out["F"][RULE_NAMES[key]] = m
    return out


def summarize(runs):
    keys = ("precision", "recall", "f1", "pr_auc", "fp_per_1000_benign", "alerts_per_1000", f"recall_top_{TOP_K}", "brier")
    table = {}
    for ex in "ABCDF":
        for cfg in runs[0][ex]:
            vals = {k: [r[ex][cfg][k] for r in runs] for k in keys if k in runs[0][ex][cfg]}      # F has no Brier score or top-k recall
            table.setdefault(ex, {})[cfg] = {k: {"mean": float(np.mean(v)), "min": float(np.min(v)), "max": float(np.max(v))} for k, v in vals.items()}
    return table


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--users", type=int, default=120)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--insiders", type=int, default=12)
    ap.add_argument("--report", default="reports")
    args = ap.parse_args()
    runs, used = [], []
    for seed in range(7, 7 + args.seeds):
        with tempfile.TemporaryDirectory() as d:
            r = one_seed(make_frame(seed, args, d))
        if r is None:
            print(f"seed {seed}: skipped (a split has no malicious session)")
            continue
        runs.append(r); used.append(seed)
    if not runs:
        sys.exit("No usable seed.")
    table = summarize(runs)
    os.makedirs(args.report, exist_ok=True)
    with open(os.path.join(args.report, "experiments.json"), "w") as fh:
        json.dump({"note": "Generated data only. Threshold from validation data; metrics on the test part. mean with min and max over seeds.",
                   "seeds": used, "data": vars(args), "summary": table, "per_seed": runs}, fh, indent=2)
    print(f"{len(runs)} seeds {used}; {args.users} users, {args.days} days, {args.insiders} insiders. mean (min to max) on the test part\n")
    for ex, title in (("A", "A single models"), ("B", "B feature groups (combined score)"), ("C", "C combination rule"), ("D", "D raw vs calibrated (combined score)"), ("F", "F simple reference methods")):
        print(title)
        for cfg, m in table[ex].items():
            print(f"  {cfg:38s} F1 {m['f1']['mean']:.2f} ({m['f1']['min']:.2f} to {m['f1']['max']:.2f})  AP {m['pr_auc']['mean']:.2f}  "
                  f"precision {m['precision']['mean']:.2f}  recall {m['recall']['mean']:.2f}  FP/1000 benign {m['fp_per_1000_benign']['mean']:.1f}  "
                  f"top-{TOP_K} recall {m.get(f'recall_top_{TOP_K}', {}).get('mean', float('nan')):.2f}  Brier {m.get('brier', {}).get('mean', float('nan')):.4f}")
        print()
