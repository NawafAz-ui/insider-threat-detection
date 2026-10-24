"""Step 3 - Behavioral analytics: 28 session features + 10 deviation features + 1 recency = 39."""
import numpy as np
import pandas as pd
from . import config

SESSION_FEATURES = [
    "duration_min", "logon_hour", "logoff_hour", "day_of_week", "is_weekend", "is_after_hours",
    "logoff_missing", "n_events_total", "events_per_hour",
    "n_device_connect", "device_after_hours",
    "n_file_events", "n_file_distinct", "n_file_zip", "n_file_exe", "n_file_removable",
    "n_email_sent", "n_email_external", "n_email_attach", "email_attach_count", "email_size_kb",
    "n_http", "n_distinct_urls", "n_distinct_domains", "n_http_job", "n_http_leak",
    "n_distinct_pcs_day", "n_sessions_day",
]
# the 10 metrics that get a per-user running mean/std baseline
BASE_METRICS = [
    "logon_hour", "duration_min", "n_device_connect", "n_distinct_urls", "n_file_events",
    "n_file_zip", "n_email_sent", "n_email_external", "email_size_kb", "n_http_leak",
]
BASE_LABELS = {
    "logon_hour": "Usual logon hour", "duration_min": "Usual session length (minutes)",
    "n_device_connect": "Removable devices per session", "n_distinct_urls": "Web pages per session",
    "n_file_events": "Files touched per session", "n_file_zip": "Archive files per session",
    "n_email_sent": "Emails sent per session", "n_email_external": "Emails outside the company per session",
    "email_size_kb": "Email size per session (KB)", "n_http_leak": "File-sharing or leak site visits per session",
}
DEV_FEATURES = [f"dev_{m}" for m in BASE_METRICS]
FEATURES = SESSION_FEATURES + DEV_FEATURES + ["hours_since_prev_session"]
assert len(SESSION_FEATURES) == 28 and len(DEV_FEATURES) == 10 and len(FEATURES) == 39

# plain-words text for the dashboard / assistant: {v} = value in this session, {m} = user's usual value
TEXT = {
    "duration_min": "Session lasted {v:.0f} minutes (usual {m:.0f}).",
    "logon_hour": "Logged on at {v:.1f}h (usual {m:.1f}h).",
    "n_device_connect": "Connected {v:.0f} removable device(s) (usual {m:.1f}).",
    "n_distinct_urls": "Visited {v:.0f} distinct web pages (usual {m:.1f}).",
    "n_file_events": "Touched {v:.0f} files (usual {m:.1f}).",
    "n_file_zip": "Handled {v:.0f} archive (.zip) files (usual {m:.1f}).",
    "n_email_sent": "Sent {v:.0f} emails (usual {m:.1f}).",
    "n_email_external": "Sent {v:.0f} emails outside the company (usual {m:.1f}).",
    "email_size_kb": "Sent {v:.0f} KB of email (usual {m:.0f} KB).",
    "n_http_leak": "Visited {v:.0f} file-sharing / leak sites (usual {m:.1f}).",
}
FEATURE_TEXT = {
    "is_after_hours": "Session started outside normal working hours.",
    "device_after_hours": "Removable device used outside working hours ({v:.0f} connection(s)).",
    "n_file_removable": "Files copied to a removable drive: {v:.0f}.",
    "n_file_exe": "Executable files handled: {v:.0f}.",
    "email_attach_count": "Email attachments sent: {v:.0f}.",
    "n_http_job": "Visited job-search sites: {v:.0f}.",
    "hours_since_prev_session": "Working hours since the user's previous session: {v:.1f}.",
    "logoff_missing": "Session had no logoff event.",
    "n_distinct_pcs_day": "Used {v:.0f} different PCs that day.",
    "events_per_hour": "Activity rate was {v:.1f} events per hour.",
    "n_events_total": "Total of {v:.0f} events in the session.",
    "n_email_attach": "Emails with attachments: {v:.0f}.",
}


def describe(feature, value, mean=None):
    """Plain-words description of one feature value."""
    base = feature[4:] if feature.startswith("dev_") else feature
    if base in TEXT and mean is not None:
        return TEXT[base].format(v=value, m=mean)
    if feature in FEATURE_TEXT:
        return FEATURE_TEXT[feature].format(v=value)
    return f"{feature.replace('_', ' ').capitalize()}: {value:.1f}."


def session_features(sessions: pd.DataFrame, agg: pd.DataFrame) -> pd.DataFrame:
    """sessions: output of build_sessions (+label); agg: per-session aggregates indexed by sid."""
    s = sessions.set_index("session_id").copy()
    a = agg.reindex(sessions["sid"].to_numpy()).fillna(0)
    a.index = s.index
    for c in a.columns:
        s[c] = a[c]
    s["duration_min"] = (s["end"] - s["start"]).dt.total_seconds() / 60
    s["logon_hour"] = s["start"].dt.hour + s["start"].dt.minute / 60
    s["logoff_hour"] = s["end"].dt.hour + s["end"].dt.minute / 60
    s["day_of_week"] = s["start"].dt.dayofweek
    s["is_weekend"] = (s["day_of_week"] >= 5).astype(int)
    s["is_after_hours"] = ((s["logon_hour"] >= config.AFTER_HOURS_START) | (s["logon_hour"] < config.AFTER_HOURS_END)).astype(int)
    s["device_after_hours"] = s["n_device_connect"] * s["is_after_hours"]
    s["n_events_total"] = s[["n_device_connect", "n_file_events", "n_email_sent", "n_http"]].sum(axis=1)
    s["events_per_hour"] = s["n_events_total"] / np.maximum(s["duration_min"] / 60, 0.25)
    day = s["start"].dt.date
    s["n_distinct_pcs_day"] = s.groupby([s["user"], day])["pc"].transform("nunique")
    s["n_sessions_day"] = s.groupby([s["user"], day])["pc"].transform("size")
    return s
