"""Step 4 - ML models: Logistic Regression (baseline), XGBoost (main), Isolation Forest (unsupervised)."""
import io
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from . import config


def time_split(n):
    """Sessions are already sorted by time: first 70% train, next 15% validation, last 15% test."""
    a, b = int(n * config.SPLIT[0]), int(n * (config.SPLIT[0] + config.SPLIT[1]))
    return np.arange(0, a), np.arange(a, b), np.arange(b, n)


def train_models(X_train, y_train):
    pos = max(int(y_train.sum()), 1)
    lr = make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=2000))
    lr.fit(X_train, y_train)
    xgb = XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1, subsample=0.9,
                        scale_pos_weight=(len(y_train) - pos) / pos, eval_metric="aucpr",
                        random_state=config.RANDOM_STATE, n_jobs=2)
    xgb.fit(X_train, y_train)
    iso = IsolationForest(n_estimators=200, contamination="auto", random_state=config.RANDOM_STATE, n_jobs=2)
    iso.fit(X_train)                         # unsupervised: labels are not used
    raw = -iso.score_samples(X_train)        # higher = more unusual
    iso_scale = (float(raw.min()), float(raw.max()))
    return {"lr": lr, "xgb": xgb, "iforest": iso}, {"iforest_scale": iso_scale}


def score_models(models, extra, X):
    """Each model returns a score in 0..1 (Isolation Forest is scaled with the training range)."""
    lo, hi = extra["iforest_scale"]
    iso = np.clip((-models["iforest"].score_samples(X) - lo) / (hi - lo + 1e-9), 0, 1)
    return {"lr": models["lr"].predict_proba(X)[:, 1], "xgb": models["xgb"].predict_proba(X)[:, 1], "iforest": iso}


def dumps(model) -> bytes:
    buf = io.BytesIO()
    joblib.dump(model, buf)
    return buf.getvalue()


def loads(b: bytes):
    return joblib.load(io.BytesIO(b))
