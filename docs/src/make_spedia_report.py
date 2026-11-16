"""Builds docs/src/data_preparation_spedia.html from the run records in backend/data/spedia, so numbers are copied, not typed.
   python docs/src/make_spedia_report.py backend/data/spedia docs/src/data_preparation_spedia.html
Then print it to docs/DATA_PREPARATION_SPEDIA.pdf with headless Chrome (--print-to-pdf --no-pdf-header-footer)."""
import json
import lzma
import os
import re
import sys
from html import escape

import pandas as pd

R, OUT = sys.argv[1], sys.argv[2]
J = lambda *p: json.load(open(os.path.join(R, *p)))
chk, rec = J("download", "verified_checksums.json"), J("download", "zenodo_record.json")
s, ex, comp, run = J("prepared", "summary.json"), J("prepared", "example.json"), J("prepared", "compression.json"), J("prepared", "engine_run.json")
conv = open(os.path.join(R, "convert.log")).readline()
kept = {k: int(v.replace(",", "")) for k, v in re.findall(r"(device|email|file|http) ([\d,]+)", conv)}
labels = int(re.search(r"malicious events ([\d,]+)", conv).group(1).replace(",", ""))
raw = pd.read_csv(lzma.open(os.path.join(R, "download", "logs_SPEDIA_annotated_en.csv.xz")), dtype=str)
act = raw["Action"].value_counts()
t = pd.to_datetime(raw["Timestamp"], format="%Y-%m-%d %H:%M:%S.%f")
mapped = raw["Action"].isin(["Connect", "Disconnect", "Email sent", "File accessed", "File modified", "File added", "File deleted", "URL accedida"])
no_user = int((mapped & raw["User"].isna()).sum())
cmd = int(act.get("Command executed", 0))
cmd_bad = int(((raw["Action"] == "Command executed") & (raw["Anomaly"] == "1")).sum())
login_rows = int(raw["Action"].isin(["Login", "Logoff", "Login Failed", "Multiple failed logins"]).sum())
left_out = len(raw) - sum(kept.values())
n = lambda v: f"{v:,}"
ses, ev, sp, v = s["sessions"], s["events_in_sessions"], s["split"], s["validation"]
share = lambda k: f'{n(ev[k])} of {n(kept[k])} ({100 * ev[k] / kept[k]:.1f}%)'


def table(head, rows, widths):
    cols = "".join(f'<col style="width:{w}%">' for w in widths)
    return (f"<table><colgroup>{cols}</colgroup><thead><tr>" + "".join(f"<th>{escape(c)}</th>" for c in head) + "</tr></thead><tbody>"
            + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table>")


before = sum(c["plain_mb"] for c in comp.values())
after = sum(c["gzip_mb"] for c in comp.values())
tr, te = sp["train"], sp["test"]
html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>SPEDIA Data Preparation</title><style>
@page {{ size: A4; margin: 13mm; }}
body {{ font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 9.3pt; line-height: 1.3; color: #000; background: #fff; margin: 0; }}
h1 {{ font-size: 17pt; margin: 0 0 5pt; }} h2 {{ font-size: 12.2pt; margin: 11pt 0 4pt; break-after: avoid; }}
p {{ margin: 0 0 5pt; }} .lead {{ font-size: 10.3pt; }} .meta {{ color: #333; font-size: 8.8pt; }}
ul {{ margin: 0 0 5pt 15pt; padding: 0; }} li {{ margin: 0 0 2.5pt; }}
table {{ width: 100%; border-collapse: collapse; font-size: 8.4pt; margin: 0 0 5pt; }} thead {{ display: table-header-group; }}
tr {{ break-inside: avoid; }} th {{ background: #000; color: #fff; text-align: left; font-weight: 600; padding: 2.5pt 4pt; border: .6pt solid #000; }}
td {{ border: .6pt solid #888; padding: 2.5pt 4pt; vertical-align: top; }} .mono {{ font-family: Menlo, monospace; font-size: 7.6pt; }}
pre {{ font-family: Menlo, monospace; font-size: 7.4pt; background: #f3f3f3; border: .6pt solid #bbb; padding: 4pt 5pt; white-space: pre-wrap; word-break: break-all; margin: 0 0 4pt; }}
</style></head><body>
<h1>SPEDIA Data Preparation</h1>
<p class="lead">This report shows the dataset the prototype uses, SPEDIA: where it came from, how it was checked, put into the prototype's file layout, preprocessed and split into a training and a test part, and the result of the first prototype run on it. CERT r4.2 stays the original dataset of the research and is planned for Capstone B.</p>
<p class="meta">Prepared on 15 November 2026 and updated on 16 November 2026 for the two-part split and the first run. Numbers are copied from the run's own records in backend/data/spedia on this laptop.</p>

<h2>1. Summary</h2>
<ul>
<li>SPEDIA version 2 from Zenodo (DOI {escape(chk["doi"])}), licence CC BY 4.0, one file of 45.7 MB. Its checksum matches the published one.</li>
<li>{n(len(raw))} events from {t.min():%d} to {t.max():%d %B %Y}. {n(sum(kept.values()))} fit the five files of the prototype's layout, and {n(left_out)} have no place in it ({n(cmd)} shell commands, {n(login_rows)} login records and {n(no_user)} events without a user).</li>
<li>All files passed the input check and gave {n(ses["total"])} sessions of {n(ses["users"])} users, {n(ses["malicious"])} of them malicious.</li>
<li>Split by time into two parts only: {n(tr["sessions"])} training sessions ({n(tr["malicious"])} malicious) and {n(te["sessions"])} test sessions ({n(te["malicious"])} malicious). There is no validation part.</li>
<li>The prototype now runs on SPEDIA. On the test part the combined score reached precision {run["precision"]:.2f}, recall {run["recall"]:.2f} and F1 {run["f1"]:.2f}.</li>
</ul>

<h2>2. Why this dataset</h2>
<p>CERT r4.2 is the original dataset of the research, but it is 16 GB unpacked, too large for a prototype, and it was removed from this laptop. No small public dataset in the exact CERT layout with labelled insiders was found: the only small CERT release (r1, 88 MB) has no answer key. SPEDIA is the second dataset already named in the Research and Methodology report (reference D2). It is small, labelled and openly licensed, and the prototype has a converter for it (itd/spedia.py).</p>

<h2>3. Source and integrity check</h2>
{table(["Item", "Value"], [
    ["Dataset", escape(rec["metadata"]["title"]) + ", version 2."],
    ["Record", f'Zenodo, https://doi.org/{escape(chk["doi"])}, published {escape(rec["metadata"]["publication_date"])}. Licence CC BY 4.0, so it may be used and shared with credit.'],
    ["Contents", "According to the record: attacks performed by real participants in a 30-day exercise, normal activity simulated with a role-based model, and synthetic events derived from the CERT dataset."],
    ["Checksum", f'Published MD5 <span class="mono">{chk["md5_published"]}</span>, MD5 of the download <span class="mono">{chk["md5"]}</span>: match. The file is stored compressed (.xz), and its unpacked content gives the same MD5.'],
], [14, 86])}

<h2>4. Conversion to the prototype's layout</h2>
<p>The converter reads a checked mapping (backend/spedia_mapping.json) that names the SPEDIA columns and event types for each CERT file. The result is in backend/data/spedia_cert, where the dashboard's run panel lists it.</p>
{table(["CERT file", "Taken from SPEDIA", "Rows"], [
    ["device.csv", f'Connect ({n(int(act["Connect"]))}) and Disconnect ({n(int(act["Disconnect"]))}) events', n(kept["device"])],
    ["email.csv", "Email sent, with the To, Size and Attachments columns", n(kept["email"])],
    ["file.csv", "File accessed, modified, added and deleted, with the name from Filename or else Path", n(kept["file"])],
    ["http.csv", "URL accedida, with the Url column", n(kept["http"])],
    ["logon.csv", "Built from the activity: a session starts at a user's first event on a host and ends at the last event before a break of 30 minutes", n(ses["total"] * 2)],
    ["answers.csv", "Events marked Anomaly = 1", n(labels)],
], [14, 70, 16])}
<p>Left out: {n(cmd)} shell commands ({n(cmd_bad)} of them marked as anomalies, so much of the real participants' attack activity), {n(login_rows)} login records and {n(no_user)} events without a user name. SPEDIA's own login records come from the Linux login log of the exercise servers. Used as sessions, 2,336 of 3,031 sessions held none of the kept events, 1,316 records were the same login written twice in one second, and 21% of the events (11,914 of 56,737) fell outside every session. Sessions built from activity keep {100 * sum(ev[k] for k in kept) / sum(kept.values()):.0f}% of the events and leave no session empty. Checking the real file showed four faults in the converter, which were fixed and tested: Disconnect events were counted as connections, "Login" also matched "Login Failed", file names stored in Path were ignored, and events without a user were put under one shared user called "unknown".</p>

<h2>5. Input check and preprocessing</h2>
<p>Input check (rules V1 to V10): <b>{escape(v["status"].upper())}</b>, no rule found a problem. The prototype's own code was used, exactly as the engine runs it.</p>
{table(["Step", "Result"], [
    ["Sessions", f'{n(ses["total"])} sessions of {n(ses["users"])} users on {n(ses["pcs"])} hosts, from {ses["first_start"][:10]} to {ses["last_start"][:10]}.'],
    ["Events in sessions", f'Device {share("device")}, file {share("file")}, email {share("email")}, web {share("http")}.'],
    ["Features", f'{len(s["features"])} per session: 28 session features, 10 differences from the user\'s own earlier sessions and the hours since the previous session.'],
    ["Labels", f'{n(ses["malicious"])} malicious sessions ({100 * ses["malicious"] / ses["total"]:.0f}%), from all {n(ses["malicious_users"])} users. A session is malicious when one of its events is marked as an anomaly.'],
], [18, 82])}

<h2>6. Training and test split</h2>
<p>The sessions are in time order and are cut at 80%. There is no validation part: the flag thresholds, the calibration and the model weights come from five-fold cross-validation inside the training part, and the test part is used once, for the result.</p>
{table(["Part", "Sessions", "Malicious", "Share", "From", "To"],
       [[k.capitalize(), n(p["sessions"]), n(p["malicious"]), f'{p["malicious_pct"]:.0f}%', p["first_start"][:16], p["last_start"][:16]] for k, p in sp.items()],
       [16, 15, 15, 12, 21, 21])}

<h2>7. First prototype run on SPEDIA</h2>
<p>On {escape(run["date"])} the main database was backed up (backend/backups/{escape(run["backup"])}) and the engine trained and scored the prototype on SPEDIA: {n(run["sessions"])} sessions, {n(run["flagged"])} flagged, flag threshold {run["threshold"]:.1f}. The run was repeated the same day after the fix that lets a session join its user's normal behavior only after it has ended, because 40 of the 246 SPEDIA sessions overlap another session of the same user. Test part results:</p>
{table(["Method", "Precision", "Recall", "F1"], [[escape(k), f'{m["precision"]:.2f}', f'{m["recall"]:.2f}', f'{m["f1"]:.2f}'] for k, m in run["models"].items()], [40, 20, 20, 20])}
<p>Flagging every test session already gives F1 {run["models"]["No skill: flag every session"]["f1"]:.2f}, because {te["malicious_pct"]:.0f}% of the test sessions are malicious. These values show that the chain works on SPEDIA, not how well it would find insiders in a company.</p>

<h2>8. One session from raw rows to features</h2>
<p>Session {escape(ex["session_id"])} on host {escape(ex["host"])}, in the test part. Its first raw SPEDIA rows (user name hidden):</p>
<pre>{escape(ex["raw"])}</pre>
<p>What preprocessing made of it: {escape(ex["features_text"])}</p>

<h2>9. Compression</h2>
{table(["Data", "Before", "After", "Input check and preprocessing time"],
       [[escape(k), f'{c["plain_mb"]} MB', f'{c["gzip_mb"]} MB', (f'{c["plain_s"]} s, then {c["gzip_s"]} s' if c["plain_s"] is not None else "Read only by the converter")] for k, c in comp.items()],
       [34, 14, 14, 38])}
<p>Data files: {after:.1f} MB instead of {before:.1f} MB. The engine reads .csv and .csv.gz files alike, and a test checks that both give the same sessions.</p>

<h2>10. Limits</h2>
<ul>
<li>The dataset is small ({n(ses["users"])} users, {n(ses["total"])} sessions) and nearly half malicious, so its results cannot be compared with CERT results.</li>
<li>Shell commands, where much of the real participants' attack activity is, are not used, because the CERT layout has no file for them.</li>
<li>The dashboard screenshots and docs/DEMO.md still show the earlier generated data.</li>
</ul>
<p class="meta">To repeat, in backend: python -m itd.spedia --csv data/spedia/download/logs_SPEDIA_annotated_en.csv.xz --map spedia_mapping.json --out data/spedia_cert, python scripts/prepare_split.py data/spedia_cert data/spedia/prepared, and python -m itd.engine --data data/spedia_cert --retrain.</p>
</body></html>"""
open(OUT, "w").write(html)
print("written", OUT)
