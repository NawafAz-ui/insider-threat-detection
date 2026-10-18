"""SHAP (TreeExplainer on XGBoost) top-3 features and top-3 baseline deviations, in plain words."""
import numpy as np
import shap
from .features import BASE_METRICS, FEATURES, describe


def shap_values(xgb, X):
    sv = shap.TreeExplainer(xgb).shap_values(X)
    return np.asarray(sv)


def top_shap(sv_row, x_row, frame_row, k=3):
    idx = [i for i in np.argsort(-sv_row)[:k] if sv_row[i] > 0]
    top = float(sv_row[idx[0]]) if idx else 1.0
    out = []
    for i in idx:
        f = FEATURES[i]
        base = f[4:] if f.startswith("dev_") else f
        mean = frame_row.get(f"mean_{base}") if base in BASE_METRICS else None
        val = frame_row[base] if f.startswith("dev_") else x_row[i]
        out.append({"feature": f, "value": round(float(x_row[i]), 3), "shap": round(float(sv_row[i]), 4),
                    "strength": "strong" if sv_row[i] >= 0.25 * top else "minor",
                    "text": describe(base if f.startswith("dev_") else f, float(val), None if mean is None else float(mean))})
    return out


def top_baseline_deviations(frame_row, k=3):
    devs = []
    for m in BASE_METRICS:
        z = float(frame_row[f"dev_{m}"])
        if z > 0:
            devs.append({"metric": m, "value": round(float(frame_row[m]), 3), "user_mean": round(float(frame_row[f"mean_{m}"]), 3),
                         "user_std": round(float(frame_row[f"std_{m}"]), 3), "z": round(z, 2),
                         "text": describe(m, float(frame_row[m]), float(frame_row[f"mean_{m}"]))})
    return sorted(devs, key=lambda d: -d["z"])[:k]
