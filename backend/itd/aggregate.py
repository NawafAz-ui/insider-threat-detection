"""Memory-bounded aggregation: events of each chunk are reduced to per-session counts immediately,
so the 32.8M events of CERT r4.2 never have to be in memory at once."""
import numpy as np
import pandas as pd

COLUMNS = ["n_device_connect", "n_file_events", "n_file_zip", "n_file_exe", "n_file_removable",
           "n_email_sent", "n_email_external", "n_email_attach", "email_attach_count", "email_size_kb",
           "n_http", "n_http_job", "n_http_leak", "n_file_distinct", "n_distinct_urls", "n_distinct_domains"]
JOB = ("monster.com", "indeed.com", "linkedin.com/jobs")
LEAK = ("wikileaks", "dropbox", "pastebin", "mega.nz")


def _hash(series):
    return pd.util.hash_array(series.fillna("").astype(str).to_numpy())


class Aggregator:
    def __init__(self):
        self.counts = []                                  # partial per-session sums
        self.pairs = {"file": [], "url": [], "dom": []}   # unique (session, value-hash) pairs

    def _pairs(self, kind, sid, values):
        df = pd.DataFrame({"sid": sid.to_numpy(), "h": _hash(values)}).drop_duplicates()
        self.pairs[kind].append(df)

    def add(self, kind, m: pd.DataFrame):
        """m: events with a 'sid' column (already assigned to sessions)."""
        if m.empty:
            return
        sid = m["sid"]
        if kind == "device":
            part = m[m["activity"] == "Connect"].groupby("sid").size().rename("n_device_connect").to_frame()
        elif kind == "file":
            f = m["filename"].fillna("").str.lower()
            d = pd.DataFrame({"sid": sid, "n_file_events": 1,
                              "n_file_zip": f.str.endswith((".zip", ".rar", ".7z")).astype(int),
                              "n_file_exe": f.str.endswith((".exe", ".bat", ".dll")).astype(int),
                              "n_file_removable": f.str.match(r"^[d-z]:\\").astype(int)})
            part = d.groupby("sid").sum()
            self._pairs("file", sid, m["filename"])
        elif kind == "email":
            to = m["to"].fillna("").str.lower()
            att = pd.to_numeric(m["attachments"], errors="coerce").fillna(0)
            size = pd.to_numeric(m["size"], errors="coerce").fillna(0) / 1024
            d = pd.DataFrame({"sid": sid, "n_email_sent": 1,
                              "n_email_external": to.str.replace("@dtaa.com", "", regex=False).str.contains("@").astype(int),
                              "n_email_attach": (att > 0).astype(int), "email_attach_count": att, "email_size_kb": size})
            part = d.groupby("sid").sum()
        elif kind == "http":
            url = m["url"].fillna("").str.lower()
            dom = url.str.replace(r"^https?://", "", regex=True).str.split("/").str[0]
            d = pd.DataFrame({"sid": sid, "n_http": 1,
                              "n_http_job": url.str.contains("|".join(JOB), regex=True).astype(int),
                              "n_http_leak": url.str.contains("|".join(LEAK), regex=True).astype(int)})
            part = d.groupby("sid").sum()
            self._pairs("url", sid, url)
            self._pairs("dom", sid, dom)
        else:
            raise ValueError(kind)
        self.counts.append(part)

    def result(self, n_sessions: int) -> pd.DataFrame:
        out = pd.DataFrame(0.0, index=np.arange(n_sessions), columns=COLUMNS)
        if self.counts:
            tot = pd.concat(self.counts).groupby(level=0).sum()
            out.loc[tot.index, tot.columns] = tot.to_numpy(float)
        for kind, col in (("file", "n_file_distinct"), ("url", "n_distinct_urls"), ("dom", "n_distinct_domains")):
            if self.pairs[kind]:
                p = pd.concat(self.pairs[kind]).drop_duplicates().groupby("sid").size()
                out.loc[p.index, col] = p.to_numpy(float)
        return out
