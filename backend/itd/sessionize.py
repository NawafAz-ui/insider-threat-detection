"""Step 2 - Preprocessing: login-to-logout sessions per user and PC."""
import numpy as np
import pandas as pd
from . import config


def build_sessions(logon: pd.DataFrame) -> pd.DataFrame:
    """A session starts at a Logon. It ends at the matching Logoff; a missing logoff closes the
    session at the next Logon or after 12 hours, whichever comes first. Sessions that cross
    midnight are kept whole."""
    ev = logon.sort_values(["user", "pc", "time"]).reset_index(drop=True)
    max_len = pd.Timedelta(hours=config.SESSION_MAX_HOURS).to_timedelta64()
    rows = []
    for (user, pc), g in ev.groupby(["user", "pc"], sort=False):
        times, acts = g["time"].to_numpy(), g["activity"].to_numpy()
        i, n = 0, len(g)
        while i < n:
            if acts[i] == "Logon":
                start = times[i]
                end, missing = start + max_len, 1
                for j in range(i + 1, n):
                    if acts[j] == "Logoff":
                        end, missing, i = min(times[j], end), 0, j
                        break
                    if acts[j] == "Logon":              # next logon closes the session
                        end, missing, i = min(times[j], end), 1, j - 1
                        break
                rows.append((user, pc, start, end, missing))
            i += 1
    s = pd.DataFrame(rows, columns=["user", "pc", "start", "end", "logoff_missing"])
    s = s.sort_values("start", kind="stable").reset_index(drop=True)
    s["sid"] = np.arange(len(s))
    s["session_id"] = "S" + s["sid"].astype(str).str.zfill(7)
    return s


def assign_events(sessions: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Attach each event to the session (same user + PC) that contains it. Adds column 'sid'."""
    if events.empty:
        return events.assign(sid=pd.Series(dtype="int64"))
    s = sessions[["sid", "user", "pc", "start", "end"]]
    e = events.sort_values("time", kind="stable")
    m = pd.merge_asof(e, s, left_on="time", right_on="start", by=["user", "pc"], direction="backward")
    m = m[m["sid"].notna() & (m["time"] <= m["end"])].copy()
    m["sid"] = m["sid"].astype("int64")
    return m.drop(columns=["start", "end"])
