"""Step 1 - Ingestion: read the CERT-layout CSV files with pandas, in chunks, and reduce them to
per-session aggregates. Folder layout is documented in docs/CSV_LAYOUT.md."""
import hashlib
import hmac
import os
import pandas as pd
from . import config
from .aggregate import Aggregator
from .sessionize import assign_events, build_sessions

CHUNK = 500_000
FILES = {  # name -> columns to keep (saves memory on the 32.8M-event CERT r4.2)
    "logon": ["id", "date", "user", "pc", "activity"],
    "device": ["id", "date", "user", "pc", "activity"],
    "email": ["id", "date", "user", "pc", "to", "size", "attachments"],
    "file": ["id", "date", "user", "pc", "filename"],
    "http": ["id", "date", "user", "pc", "url"],
}


class Pseudonymizer:
    """user id -> stable keyed hash (HMAC-SHA256), so analysts never see the real id."""
    def __init__(self, key):
        self.key, self.cache = key.encode(), {}

    def __call__(self, series):
        for u in series.unique():
            if u not in self.cache:
                self.cache[u] = "U-" + hmac.new(self.key, str(u).encode(), hashlib.sha256).hexdigest()[:10]
        return series.map(self.cache)


def iter_chunks(path, cols, pseudo=None):
    for chunk in pd.read_csv(path, usecols=cols, chunksize=CHUNK, dtype=str):
        chunk["time"] = pd.to_datetime(chunk["date"], format="%m/%d/%Y %H:%M:%S")
        chunk = chunk.drop(columns="date")
        if pseudo is not None:
            chunk["user"] = pseudo(chunk["user"])
        yield chunk


def check_folder(folder):
    missing = [f"{n}.csv" for n in FILES if not os.path.exists(os.path.join(folder, f"{n}.csv"))]
    if missing:
        raise FileNotFoundError(f"Missing in {folder}: {', '.join(missing)}. See docs/CSV_LAYOUT.md for the expected layout.")


def load_dataset(folder, pseudonymize=None, log=print):
    """Return (sessions, agg): sessions with a 'label' column (1 = contains an event from the answer file)
    and a per-session aggregate frame (indexed by sid)."""
    check_folder(folder)
    pseudonymize = config.PSEUDONYMIZE if pseudonymize is None else pseudonymize
    pseudo = Pseudonymizer(config.PSEUDONYM_KEY) if pseudonymize else None
    ans = os.path.join(folder, "answers.csv")
    bad = set(pd.read_csv(ans, dtype=str)["id"]) if os.path.exists(ans) else set()

    logon = pd.concat(list(iter_chunks(os.path.join(folder, "logon.csv"), FILES["logon"], pseudo)), ignore_index=True)
    sessions = build_sessions(logon)
    bad_sids = set(assign_events(sessions, logon).query("id in @bad")["sid"]) if bad else set()
    log(f"    logon: {len(logon):,} events -> {len(sessions):,} sessions")
    del logon

    agg = Aggregator()
    for kind in ("device", "file", "email", "http"):
        n = 0
        for chunk in iter_chunks(os.path.join(folder, f"{kind}.csv"), FILES[kind], pseudo):
            m = assign_events(sessions, chunk)
            if bad:
                bad_sids.update(m.loc[m["id"].isin(bad), "sid"])
            agg.add(kind, m)
            n += len(chunk)
        log(f"    {kind}: {n:,} events")
    sessions["label"] = sessions["sid"].isin(bad_sids).astype(int)
    return sessions, agg.result(len(sessions))
