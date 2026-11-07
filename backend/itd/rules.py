"""Simple reference methods: no learning, only one flag threshold chosen on the validation part.
They answer the question "does the model beat a rule an analyst could write by hand?"
(docs/EVALUATION_CRITERIA.md, comparison F). A rule gives each session a score (higher = more suspicious) and the
flag threshold is chosen on validation data exactly like for the models, so the test part is never used for tuning."""
from .features import DEV_FEATURES
from .risk import best_f1, evaluate

RULE_NAMES = {
    "rule_after_hours": "Rule: after-hours session",
    "rule_hand_written": "Rule: after hours with a removable device or leak site",
    "rule_deviation": "Rule: largest deviation from the user's own normal",
    "no_skill": "No skill: flag every session",
}


def rule_scores(feats):
    """One score per session and rule. The first two are 0 or 1; the third is the largest of the 10 deviation features."""
    after = feats["is_after_hours"].to_numpy(float) > 0
    risky = (feats["n_device_connect"].to_numpy(float) > 0) | (feats["n_http_leak"].to_numpy(float) > 0)
    return {"rule_after_hours": after.astype(float),
            "rule_hand_written": (after & risky).astype(float),
            "rule_deviation": feats[DEV_FEATURES].to_numpy(float).max(axis=1)}


def reference_metrics(feats, y, va, te):
    """Test-part metrics of the reference methods. va and te are the index arrays of the validation and test parts."""
    out = {}
    benign = len(te) - int(y[te].sum())
    for key, s in rule_scores(feats).items():
        thr = best_f1(y[va], s[va])[1]                              # chosen on validation data only
        m = evaluate(y[te], s[te], thr)
        out[key] = {**m, "threshold": float(thr), "fp_per_1000_benign": 1000 * m["flagged"] * (1 - m["precision"]) / benign,
                    "alerts_per_1000": 1000 * m["flagged"] / len(te)}
    p = float(y[te].mean())                                         # no skill: flag everything, so precision is the share of malicious sessions
    out["no_skill"] = {"precision": p, "recall": 1.0, "f1": 2 * p / (1 + p), "pr_auc": p, "flagged": int(len(te)),
                       "positives": int(y[te].sum()), "fp_per_1000_benign": 1000.0, "alerts_per_1000": 1000.0}
    return out
