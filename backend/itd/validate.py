"""Step 0 - Input validation (pre-flight). Checks the CERT-layout folder BEFORE the engine reads it.
Errors stop the run. Warnings are reported and the data is still accepted exactly as ingest.py reads it.
Every rule has an id (V1 ...) so the report, the tests and docs/DATA_RULES.md can refer to it.
Usage:  python -m itd.validate data/cert_synthetic"""
import json
import os
import sys

import numpy as np
import pandas as pd

from .ingest import CHUNK, FILES

DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
ACTIVITIES = {"logon": {"Logon", "Logoff"}, "device": {"Connect", "Disconnect"}}
NUMERIC = {"email": ("size", "attachments")}       # an invalid value becomes 0 in aggregate.py
MAX_EXAMPLES = 5                                    # example line numbers kept per rule

RULES = {   # id -> (severity, meaning). Kept here so docs and tests read one list.
    "V1": ("error", "a required CSV file is missing"),
    "V2": ("error", "a required column is missing"),
    "V3": ("error", "a date does not match MM/DD/YYYY HH:MM:SS"),
    "V4": ("warning", "id, user or pc is empty (the event cannot belong to a session)"),
    "V5": ("warning", "an event id appears more than once (also across files)"),
    "V6": ("warning", "unknown activity value (the event is ignored)"),
    "V7": ("warning", "email size or attachments is not a number (counted as 0)"),
    "V8": ("error", "answers.csv has no 'id' column"),
    "V9": ("warning", "answer ids that match no event (those labels are lost)"),
    "V10": ("warning", "no malicious labels (answers.csv is missing or empty): every session is labelled 0 and training will stop"),
}


def _issue(rule, file, count, rows=()):
    return {"rule": rule, "severity": RULES[rule][0], "file": file, "message": RULES[rule][1],
            "count": int(count), "example_lines": [int(r) for r in list(rows)[:MAX_EXAMPLES]]}


def _hash(series):
    return pd.util.hash_pandas_object(series.fillna(""), index=False).to_numpy()


def _blank(series):
    return series.isna() | (series.str.strip() == "")


def _check_file(path, kind, chunk):
    """Read one event file in chunks. Returns (rows, issues, id_hashes)."""
    issues, hashes, rows = {}, [], 0

    def add(rule, mask, offset):
        n = int(mask.sum())
        if n:
            d = issues.setdefault(rule, {"count": 0, "rows": []})
            d["count"] += n
            if len(d["rows"]) < MAX_EXAMPLES:
                d["rows"] += list(np.flatnonzero(mask.to_numpy()) + offset + 2)      # line 1 is the header

    for ch in pd.read_csv(path, usecols=FILES[kind], chunksize=chunk, dtype=str):
        t = pd.to_datetime(ch["date"], format=DATE_FORMAT, errors="coerce")
        add("V3", t.isna(), rows)
        add("V4", _blank(ch["id"]) | _blank(ch["user"]) | _blank(ch["pc"]), rows)
        if kind in ACTIVITIES:
            add("V6", ~ch["activity"].isin(ACTIVITIES[kind]), rows)
        for col in NUMERIC.get(kind, ()):
            add("V7", ch[col].notna() & pd.to_numeric(ch[col], errors="coerce").isna(), rows)
        hashes.append(_hash(ch["id"]))
        rows += len(ch)
    return rows, issues, (np.concatenate(hashes) if hashes else np.array([], dtype="uint64"))


def validate_folder(folder, chunk=CHUNK):
    """Return a report dict: status ('ok', 'warnings' or 'failed'), issues, row counts."""
    issues, files, hashes = [], {}, {}
    missing = [f"{n}.csv" for n in FILES if not os.path.exists(os.path.join(folder, f"{n}.csv"))]
    if missing:
        issues.append({**_issue("V1", ", ".join(missing), len(missing)), "message": f"{RULES['V1'][1]}: {', '.join(missing)}"})
        return _finish(folder, issues, files)

    for kind in FILES:
        path = os.path.join(folder, f"{kind}.csv")
        header = list(pd.read_csv(path, nrows=0, dtype=str).columns)
        absent = [c for c in FILES[kind] if c not in header]
        if absent:
            issues.append({**_issue("V2", f"{kind}.csv", len(absent)), "message": f"{RULES['V2'][1]}: {', '.join(absent)}"})
            continue
        rows, found, hashes[kind] = _check_file(path, kind, chunk)
        files[kind] = rows
        for rule, d in found.items():
            issues.append(_issue(rule, f"{kind}.csv", d["count"], d["rows"]))

    if len(hashes) == len(FILES):
        allh = np.concatenate(list(hashes.values()))
        dup_inside = sum(len(h) - len(np.unique(h)) for h in hashes.values())
        dup_all = len(allh) - len(np.unique(allh))
        if dup_all:
            issues.append({**_issue("V5", "all event files", dup_all), "message": f"{RULES['V5'][1]} ({dup_inside} inside one file, {dup_all - dup_inside} across files)"})
        ans = os.path.join(folder, "answers.csv")
        if not os.path.exists(ans):
            issues.append(_issue("V10", "answers.csv", 0))
        else:
            a = pd.read_csv(ans, dtype=str)
            if "id" not in a.columns:
                issues.append(_issue("V8", "answers.csv", 1))
            else:
                files["answers"] = len(a)
                lost = int((~np.isin(_hash(a["id"]), allh)).sum())
                if lost:
                    issues.append(_issue("V9", "answers.csv", lost))
                if len(a) == 0:
                    issues.append(_issue("V10", "answers.csv", 0))
    return _finish(folder, issues, files)


def _finish(folder, issues, files):
    errors = [i for i in issues if i["severity"] == "error"]
    status = "failed" if errors else ("warnings" if issues else "ok")
    return {"folder": os.path.abspath(folder), "status": status, "rows": files, "issues": issues,
            "summary": {"status": status, "errors": len(errors), "warnings": len(issues) - len(errors), "rows": files}}


def format_report(rep):
    lines = [f"    Input validation: {rep['status'].upper()}  " + ", ".join(f"{k}.csv {v:,}" for k, v in rep["rows"].items())]
    for i in rep["issues"]:
        where = f" (lines {', '.join(map(str, i['example_lines']))})" if i["example_lines"] else ""
        lines.append(f"    [{i['rule']} {i['severity']}] {i['file']}: {i['message']} - {i['count']:,}{where}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python -m itd.validate <data folder> [report.json]")
    report = validate_folder(sys.argv[1])
    print(format_report(report))
    if len(sys.argv) > 2:
        with open(sys.argv[2], "w") as f:
            json.dump(report, f, indent=2)
    raise SystemExit(1 if report["status"] == "failed" else 0)
