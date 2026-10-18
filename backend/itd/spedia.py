"""SPEDIA adapter: converts the single SPEDIA event CSV (logs_SPEDIA.csv) to the CERT folder layout so the
same pipeline can read it (exploratory cross-dataset test).

The column names of logs_SPEDIA.csv are set in a mapping file (see spedia_mapping.example.json) because they
must be checked against the real file first:
    python -m itd.spedia --inspect logs_SPEDIA.csv                 # shows columns and sample values
    python -m itd.spedia --csv logs_SPEDIA.csv --map spedia_mapping.json --out data/spedia_cert
"""
import argparse
import json
import os
import numpy as np
import pandas as pd

FMT = "%m/%d/%Y %H:%M:%S"
KINDS = ("logon", "logoff", "device", "email", "file", "http")


def inspect(path, rows=3):
    df = pd.read_csv(path, dtype=str, nrows=200000)
    print(f"{len(df.columns)} columns: {list(df.columns)}\n")
    print(df.head(rows).T.to_string(), "\n")
    for c in df.columns:
        if df[c].nunique() <= 25:
            print(f"-- values of '{c}':", df[c].value_counts().head(25).to_dict())


def _match(series, needles):
    s = series.fillna("").str.lower()
    out = pd.Series(False, index=series.index)
    for n in needles:
        out |= s.str.contains(str(n).lower(), regex=False)
    return out


def convert(csv_path, m, out):
    df = pd.read_csv(csv_path, dtype=str)
    df["time"] = pd.to_datetime(df[m["time_column"]], format=m.get("time_format"), errors="coerce", utc=True).dt.tz_localize(None)
    df = df[df["time"].notna()].copy()
    df["user"] = df[m["user_column"]].fillna("unknown")
    df["pc"] = df[m["host_column"]].fillna("HOST") if m.get("host_column") else "HOST"
    df["id"] = "E" + df.index.astype(str)
    label = df[m["label_column"]].astype(str).str.lower().isin([str(v).lower() for v in m["malicious_values"]]) \
        if m.get("label_column") else pd.Series(False, index=df.index)
    kind = pd.Series("", index=df.index)
    et = df[m["event_type_column"]]
    for k in KINDS:
        needles = m["type_map"].get(k, [])
        if needles:
            kind[_match(et, needles) & (kind == "")] = k
    df["kind"] = kind
    df = df[df["kind"] != ""]
    label = label.reindex(df.index)
    os.makedirs(out, exist_ok=True)
    cols = ["id", "date", "user", "pc"]

    def save(name, frame, extra):
        frame = frame.assign(date=frame["time"].dt.strftime(FMT))
        frame[cols + extra].to_csv(os.path.join(out, f"{name}.csv"), index=False)

    logon = df[df["kind"].isin(["logon", "logoff"])].assign(activity=lambda d: np.where(d["kind"] == "logon", "Logon", "Logoff"))
    if logon.empty:                      # no explicit logon/logoff events: build sessions from activity gaps
        gap = pd.Timedelta(minutes=m.get("session_gap_minutes", 30))
        d = df.sort_values(["user", "pc", "time"])
        new = (d.groupby(["user", "pc"])["time"].diff() > gap) | d.groupby(["user", "pc"])["time"].diff().isna()
        d = d.assign(grp=new.cumsum())
        g = d.groupby("grp").agg(user=("user", "first"), pc=("pc", "first"), t0=("time", "min"), t1=("time", "max")).reset_index()
        logon = pd.concat([
            pd.DataFrame({"id": "LI" + g["grp"].astype(str), "time": g["t0"], "user": g["user"], "pc": g["pc"], "activity": "Logon"}),
            pd.DataFrame({"id": "LO" + g["grp"].astype(str), "time": g["t1"], "user": g["user"], "pc": g["pc"], "activity": "Logoff"})])
    save("logon", logon, ["activity"])
    dev = df[df["kind"] == "device"].assign(activity="Connect")
    save("device", dev, ["activity"])
    em = df[df["kind"] == "email"].assign(to=lambda d: d[m["to_column"]] if m.get("to_column") else "",
                                           size=lambda d: d[m["size_column"]] if m.get("size_column") else "0",
                                           attachments=lambda d: d[m["attachments_column"]] if m.get("attachments_column") else "0")
    save("email", em, ["to", "size", "attachments"])
    fl = df[df["kind"] == "file"].assign(filename=lambda d: d[m["filename_column"]] if m.get("filename_column") else "")
    save("file", fl, ["filename"])
    ht = df[df["kind"] == "http"].assign(url=lambda d: d[m["url_column"]] if m.get("url_column") else "")
    save("http", ht, ["url"])
    bad = df.loc[label.to_numpy(bool), ["kind", "id"]].rename(columns={"kind": "activity_type"})
    bad.loc[bad["activity_type"] == "logoff", "activity_type"] = "logon"
    bad.to_csv(os.path.join(out, "answers.csv"), index=False)
    print(f"Converted {len(df):,} events -> {out}: " + ", ".join(f"{k} {int((df.kind == k).sum()):,}" for k in KINDS) +
          f"; malicious events {len(bad):,}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--inspect")
    ap.add_argument("--csv")
    ap.add_argument("--map")
    ap.add_argument("--out", default="data/spedia_cert")
    a = ap.parse_args()
    if a.inspect:
        inspect(a.inspect)
    else:
        convert(a.csv, json.load(open(a.map)), a.out)
