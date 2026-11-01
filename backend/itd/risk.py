"""Step 5 - Risk engine: calibrated scores, weighted 0-100 risk score, F1-optimal threshold, evaluation metrics."""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, precision_recall_curve, precision_score, recall_score, f1_score

CALIBRATION_C = 10.0     # mild regularization: the validation part has few malicious sessions, so the curve is kept gentle


def best_f1(y, s):
    """Best F1 over all thresholds, and the threshold that gives it."""
    p, r, t = precision_recall_curve(y, s)
    f = 2 * p[:-1] * r[:-1] / np.maximum(p[:-1] + r[:-1], 1e-12)
    i = int(np.argmax(f)) if len(f) else 0
    return float(f[i]) if len(f) else 0.0, float(t[i]) if len(t) else 0.5


def fit_calibrators(val_scores: dict, y_val):
    """Platt scaling, one curve per model: p = 1 / (1 + exp(-(a * score + b))). Fitted on validation data only."""
    out = {}
    for k, s in val_scores.items():
        m = LogisticRegression(C=CALIBRATION_C, max_iter=1000).fit(np.asarray(s, float).reshape(-1, 1), y_val)
        out[k] = {"a": float(m.coef_[0, 0]), "b": float(m.intercept_[0])}
    return out


def calibrate(scores: dict, calibrators: dict):
    return {k: 1.0 / (1.0 + np.exp(-(calibrators[k]["a"] * np.asarray(v, float) + calibrators[k]["b"]))) for k, v in scores.items()}


def fit_risk_engine(val_scores: dict, y_val):
    """Calibrate each model on validation data, weight it by its validation F1 and set the flag threshold at the
    best F1 of the combined score. Nothing here sees the test labels. (The engine refuses a validation part without
    a malicious session, so the F1 values cannot all be zero.)"""
    cal = fit_calibrators(val_scores, y_val)
    p = calibrate(val_scores, cal)
    best = {k: best_f1(y_val, v) for k, v in p.items()}
    f1s = {k: b[0] for k, b in best.items()}
    tot = sum(f1s.values()) or 1.0
    weights = {k: f / tot for k, f in f1s.items()}
    f1, thr = best_f1(y_val, combine(p, weights))
    return {"calibrators": cal, "weights": weights, "val_f1": f1s, "val_thresholds": {k: b[1] for k, b in best.items()},
            "threshold": thr, "val_f1_combined": f1}


def combine(scores: dict, weights: dict):
    return 100.0 * sum(weights[k] * scores[k] for k in weights)


def evaluate(y, scores_0_100, threshold=None):
    pred = (scores_0_100 >= threshold).astype(int) if threshold is not None else None
    out = {"pr_auc": float(average_precision_score(y, scores_0_100)) if y.sum() else None}     # average precision
    if pred is not None:
        out.update(precision=float(precision_score(y, pred, zero_division=0)),
                   recall=float(recall_score(y, pred, zero_division=0)),
                   f1=float(f1_score(y, pred, zero_division=0)), flagged=int(pred.sum()), positives=int(y.sum()))
    return out


def evaluate_model(y, s, threshold, raw=None):
    """Test metrics of one model at a threshold chosen on validation data (0..1 scale), with the Brier score
    of the calibrated scores and, when given, of the raw scores."""
    out = {**evaluate(y, s * 100, threshold * 100), "validation_threshold": threshold, "brier": float(brier_score_loss(y, s))}
    if raw is not None:
        out["brier_raw"] = float(brier_score_loss(y, raw))
    return out
