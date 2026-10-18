"""Build answers.csv from the CERT answer files (folder with r4.2-*/ CSVs, rows like  logon,{ID},date,user,...).
   python scripts/build_answers.py <path-to-CERT-answers> <path-to-dataset-folder>"""
import csv
import os
import sys

src, dst = sys.argv[1], sys.argv[2]
rows = 0
with open(os.path.join(dst, "answers.csv"), "w", newline="") as out:
    w = csv.writer(out)
    w.writerow(["activity_type", "id"])
    for root, _, files in os.walk(src):
        for fn in files:
            if fn.lower().endswith(".csv"):
                with open(os.path.join(root, fn), newline="", encoding="utf-8", errors="ignore") as f:
                    for r in csv.reader(f):
                        if len(r) >= 2 and r[0].lower() in ("logon", "device", "email", "file", "http"):
                            w.writerow([r[0].lower(), r[1]]); rows += 1
print(f"answers.csv written: {rows} malicious events")
