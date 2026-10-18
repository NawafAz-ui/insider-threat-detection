"""Step 5 - Risk engine: weighted 0-100 risk score, F1-optimal threshold, evaluation metrics."""
import numpy as np
from sklearn.metrics import average_precision_score, precision_recall_curve, precision_score, recall_score, f1_score


def best_f1(y, s):
    """Best F1 over all thresholds, and the threshold that gives it."""
    p, r, t = precision_recall_curve(y, s)
    f = 2 * p[:-1] * r[:-1] / np.maximum(p[:-1] + r[:-1], 1e-12)
    i = int(np.argmax(f)) if len(f) else 0
    return float(f[i]) if len(f) else 0.0, float(t[i]) if len(t) else 0.5


def fit_risk_engine(val_scores: dict, y_val):
    """Weights proportional to each model's validation F1; threshold = best F1 of the combined score."""
    f1s = {k: best_f1(y_val, v)[0] for k, v in val_scores.items()}
    tot = sum(f1s.values()) or 1.0
    weights = {k: f / tot for k, f in f1s.items()}
    risk = combine(val_scores, weights)
    f1, thr = best_f1(y_val, risk)
    return {"weights": weights, "val_f1": f1s, "threshold": thr, "val_f1_combined": f1}


def combine(scores: dict, weights: dict):
    return 100.0 * sum(weights[k] * scores[k] for k in weights)


def evaluate(y, scores_0_100, threshold=None):
    pred = (scores_0_100 >= threshold).astype(int) if threshold is not None else None
    out = {"pr_auc": float(average_precision_score(y, scores_0_100)) if y.sum() else None}
    if pred is not None:
        out.update(precision=float(precision_score(y, pred, zero_division=0)),
                   recall=float(recall_score(y, pred, zero_division=0)),
                   f1=float(f1_score(y, pred, zero_division=0)), flagged=int(pred.sum()), positives=int(y.sum()))
    return out


def evaluate_model(y, s):
    f1, thr = best_f1(y, s)
    return {**evaluate(y, s * 100, thr * 100), "best_threshold": thr}
