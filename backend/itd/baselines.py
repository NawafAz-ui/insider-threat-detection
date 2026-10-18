"""User-relative baselines: running mean / std per user (Welford), updated after every session."""
import numpy as np
import pandas as pd
from .features import BASE_METRICS, DEV_FEATURES

MIN_HISTORY = 5      # sessions needed before a deviation is trusted
CLIP = 10.0


def _working_gap_hours(prev, cur):
    """Hours between two session starts, minus whole weekend days in between, so that a normal
    Friday-to-Monday gap is not read as a long absence."""
    d0, d1 = prev.astype("datetime64[D]"), cur.astype("datetime64[D]")
    weekend_days = int((d1 - d0).astype(int)) - int(np.busday_count(d0, d1))
    return max(float((cur - prev) / np.timedelta64(1, "h")) - 24.0 * weekend_days, 0.0)


def _floor(metric):
    return 0.5          # std floor so a never-used metric (std 0) still yields a finite deviation


def add_deviations(s: pd.DataFrame, prior: dict | None = None):
    """s: time-ordered session features (index session_id). Adds 10 dev_* columns, the user's
    mean/std *before* each session (mean_*, std_*) and hours_since_prev_session.
    Returns (frame, final_state) where final_state is the baseline to store per user."""
    prior = prior or {}
    X = s[BASE_METRICS].to_numpy(float)
    users = s["user"].to_numpy()
    starts = s["start"].to_numpy()
    n_rows, k = X.shape
    dev = np.zeros((n_rows, k)); mean_b = np.zeros((n_rows, k)); std_b = np.zeros((n_rows, k))
    recency = np.zeros(n_rows)
    state = {u: dict(n=p["n"], mean=np.array([p["mean"][m] for m in BASE_METRICS]),
                     m2=np.array([p["m2"][m] for m in BASE_METRICS]), last=None) for u, p in prior.items()}
    floors = np.array([_floor(m) for m in BASE_METRICS])
    for i in range(n_rows):
        st = state.setdefault(users[i], dict(n=0, mean=np.zeros(k), m2=np.zeros(k), last=None))
        n = st["n"]
        std = np.sqrt(st["m2"] / n) if n > 1 else np.zeros(k)
        mean_b[i], std_b[i] = st["mean"], std
        if n >= MIN_HISTORY:
            dev[i] = np.clip((X[i] - st["mean"]) / np.maximum(std, floors), -CLIP, CLIP)
        recency[i] = 0.0 if st["last"] is None else _working_gap_hours(st["last"], starts[i])
        # Welford update AFTER scoring this session
        st["n"] = n + 1
        d = X[i] - st["mean"]
        st["mean"] = st["mean"] + d / st["n"]
        st["m2"] = st["m2"] + d * (X[i] - st["mean"])
        st["last"] = starts[i]
    out = s.copy()
    out[DEV_FEATURES] = dev
    out["hours_since_prev_session"] = recency
    for j, m in enumerate(BASE_METRICS):
        out[f"mean_{m}"], out[f"std_{m}"] = mean_b[:, j], std_b[:, j]
    final = {u: {"n": int(v["n"]), "mean": dict(zip(BASE_METRICS, map(float, v["mean"]))),
                 "m2": dict(zip(BASE_METRICS, map(float, v["m2"])))} for u, v in state.items()}
    return out, final
