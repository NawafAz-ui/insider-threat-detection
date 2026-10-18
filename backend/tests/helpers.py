"""Test helper: turn a CERT-layout folder into ONE SPEDIA-like CSV with different column names."""
import os
import pandas as pd


def make_fake_spedia(cert_dir, out_csv):
    parts = []
    for kind, label_kind in (("logon", None), ("device", None), ("email", None), ("file", None), ("http", None)):
        df = pd.read_csv(os.path.join(cert_dir, f"{kind}.csv"), dtype=str)
        t = pd.to_datetime(df["date"], format="%m/%d/%Y %H:%M:%S")
        et = (df["activity"].str.lower() if kind == "logon" else "usb_" + df["activity"].str.lower() if kind == "device"
              else {"email": "email_sent", "file": "file_modified", "http": "http_request"}[kind])
        parts.append(pd.DataFrame({"timestamp": t.dt.strftime("%Y-%m-%dT%H:%M:%S"), "user": df["user"], "host": df["pc"],
                                   "event_type": et, "url": df.get("url"), "recipient": df.get("to"),
                                   "size": df.get("size"), "attachments": df.get("attachments"),
                                   "filename": df.get("filename"), "_id": df["id"]}))
    allv = pd.concat(parts, ignore_index=True)
    bad = set(pd.read_csv(os.path.join(cert_dir, "answers.csv"), dtype=str)["id"])
    allv["label"] = allv["_id"].isin(bad).astype(int)
    allv.drop(columns="_id").to_csv(out_csv, index=False)
