"""Dataset preparation: scripts/extract_cert.py keeps only the columns the engine reads and changes no value,
scripts/prepare_split.py preprocesses and splits without the database or models, gzip-compressed input gives
the same result as plain CSV, and the SPEDIA adapter keeps device Disconnect events apart from connections."""
import gzip
import json
import shutil
import os
import subprocess
import sys
import tarfile

os.environ.setdefault("MONGO_URI", "mock")
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import extract_cert  # noqa: E402
import prepare_split  # noqa: E402
from itd.ingest import FILES  # noqa: E402


def _release(tmp_path):
    """A small archive shaped like r4.2.tar.bz2: the event files carry extra columns the engine never reads."""
    gen = tmp_path / "gen"
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts/generate_synthetic_cert.py"), str(gen),
                           "--users", "20", "--days", "40", "--insiders", "3"])
    rel = tmp_path / "r4.2"
    (rel / "LDAP").mkdir(parents=True)
    for kind in FILES:
        df = pd.read_csv(gen / f"{kind}.csv", dtype=str)
        df.insert(len(df.columns), "notes", "secret words, with a comma")
        df.to_csv(rel / f"{kind}.csv", index=False)
    (rel / "readme.txt").write_text("release notes")
    (rel / "LDAP" / "2010-01.csv").write_text("employee_name,user_id\n")
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "evil.txt").write_text("outside")
    archive = tmp_path / "r4.2.tar.bz2"
    with tarfile.open(archive, "w:bz2") as tar:
        tar.add(rel, arcname="r4.2")
        tar.add(tmp_path / "other" / "evil.txt", arcname="../evil.txt")   # a member that points outside
    return gen, archive


def test_extract_keeps_the_engine_columns_unchanged_and_prepare_splits_by_time(tmp_path):
    gen, archive = _release(tmp_path)
    data, ref, prep = tmp_path / "data", tmp_path / "ref", tmp_path / "prep"
    extract_cert.main(str(archive), str(data), str(ref))

    manifest = json.load(open(data / "extract_manifest.json"))
    for kind, cols in FILES.items():
        got = pd.read_csv(data / f"{kind}.csv", dtype=str)
        want = pd.read_csv(gen / f"{kind}.csv", dtype=str)[cols]
        assert list(got.columns) == cols
        pd.testing.assert_frame_equal(got, want)                     # same rows, same order, same values
        assert manifest["files"][f"{kind}.csv"]["rows"] == len(want)
        dropped = manifest["files"][f"{kind}.csv"]["dropped_columns"]
        assert "notes" in dropped and not set(dropped) & set(cols)
    assert (ref / "r4.2" / "readme.txt").read_text() == "release notes"
    assert (ref / "r4.2" / "LDAP" / "2010-01.csv").exists()
    assert not (tmp_path / "evil.txt").exists()                     # nothing is written outside the reference folder

    (data / "answers.csv").write_bytes((gen / "answers.csv").read_bytes())
    prepare_split.main(str(data), str(prep))
    s = json.load(open(prep / "summary.json"))
    parts = s["split"]
    assert sum(p["sessions"] for p in parts.values()) == s["sessions"]["total"]
    assert parts["train"]["sessions"] == int(s["sessions"]["total"] * 0.80) and set(parts) == {"train", "test"}
    assert parts["train"]["last_start"] <= parts["test"]["first_start"]
    assert sum(p["malicious"] for p in parts.values()) == s["sessions"]["malicious"] > 0
    train = pd.read_csv(prep / "train.csv.gz")
    assert len(train) == parts["train"]["sessions"] and set(s["features"]) <= set(train.columns)


def _generated(tmp_path, name="plain"):
    d = tmp_path / name
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts/generate_synthetic_cert.py"), str(d),
                           "--users", "20", "--days", "40", "--insiders", "3"])
    return d


def test_gzip_compressed_folder_gives_the_same_sessions_as_plain_csv(tmp_path):
    from itd import config, jobs, validate
    from itd.ingest import load_dataset
    plain = _generated(tmp_path)
    packed = tmp_path / "data" / "packed"
    packed.mkdir(parents=True)
    for f in plain.glob("*.csv"):
        with open(f, "rb") as src, gzip.open(packed / (f.name + ".gz"), "wb") as dst:
            shutil.copyfileobj(src, dst)
    assert not list(packed.glob("*.csv"))                                   # only .csv.gz files are left
    assert validate.validate_folder(str(packed))["rows"] == validate.validate_folder(str(plain))["rows"]
    (s1, a1), (s2, a2) = load_dataset(str(plain)), load_dataset(str(packed))
    pd.testing.assert_frame_equal(s1, s2)
    pd.testing.assert_frame_equal(a1, a2)
    old = config.DATA_ROOT
    config.DATA_ROOT = str(tmp_path / "data")
    try:
        assert jobs.list_datasets() == ["packed"] and jobs.dataset_path("packed")
    finally:
        config.DATA_ROOT = old


def test_spedia_adapter_keeps_device_disconnects_apart(tmp_path):
    from helpers import make_fake_spedia
    from itd import spedia
    cert = _generated(tmp_path)
    make_fake_spedia(str(cert), str(tmp_path / "fake.csv"))
    spedia.convert(str(tmp_path / "fake.csv"), json.load(open(os.path.join(ROOT, "spedia_mapping.example.json"))), str(tmp_path / "sp"))
    want = pd.read_csv(cert / "device.csv")["activity"].value_counts()
    got = pd.read_csv(tmp_path / "sp" / "device.csv")["activity"].value_counts()
    assert got.to_dict() == want.to_dict() and set(got.index) == {"Connect", "Disconnect"}


def test_spedia_exact_type_match_keeps_failed_logins_out():
    from itd.spedia import _match
    s = pd.Series(["Login", "Login Failed", "Logoff", None])
    assert _match(s, ["Login"], exact=True).tolist() == [True, False, False, False]
    assert _match(s, ["login"]).tolist() == [True, True, False, False]          # substring matching stays the default


def test_spedia_drops_events_without_a_user_when_asked(tmp_path):
    from itd import spedia
    pd.DataFrame({"Timestamp": ["2025-03-06 10:00:00.000", "2025-03-06 10:05:00.000"], "User": ["u1", None], "Agent_name": "h1",
                  "Action": "Email sent", "To": "x@y.com", "Size": "1", "Attachments": "0", "Url": "", "Filename": "", "Path": "",
                  "Anomaly": ["0", "1"]}).to_csv(tmp_path / "s.csv", index=False)
    m = json.load(open(os.path.join(ROOT, "spedia_mapping.json")))
    spedia.convert(str(tmp_path / "s.csv"), m, str(tmp_path / "out"))
    assert pd.read_csv(tmp_path / "out" / "email.csv")["user"].tolist() == ["u1"]
    assert pd.read_csv(tmp_path / "out" / "answers.csv").empty                # the dropped event leaves no label behind
