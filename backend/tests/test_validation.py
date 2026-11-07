"""Pre-flight input validation (itd/validate.py): every rule V1 to V10, and the engine stops on errors."""
import os
import subprocess
import sys

os.environ.setdefault("MONGO_URI", "mock")
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture(scope="module")
def clean(tmp_path_factory):
    d = tmp_path_factory.mktemp("clean")
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts/generate_synthetic_cert.py"), str(d),
                           "--users", "12", "--days", "30", "--insiders", "2"])
    return d


@pytest.fixture
def data(clean, tmp_path):
    """A fresh copy of the clean folder that a test may damage."""
    import shutil
    d = tmp_path / "data"
    shutil.copytree(clean, d)
    return d


def _edit(d, name, fn):
    p = d / f"{name}.csv"
    df = pd.read_csv(p, dtype=str, keep_default_na=False)
    fn(df)
    df.to_csv(p, index=False)


def _rules(rep):
    return {i["rule"] for i in rep["issues"]}


def test_clean_data_passes(clean):
    from itd import validate
    rep = validate.validate_folder(str(clean))
    assert rep["status"] == "ok" and rep["issues"] == []
    assert rep["rows"]["logon"] > 0 and "answers" in rep["rows"]


def test_missing_file_is_an_error(data):
    from itd import validate
    os.remove(data / "device.csv")
    rep = validate.validate_folder(str(data))
    assert rep["status"] == "failed" and _rules(rep) == {"V1"}
    assert "device.csv" in rep["issues"][0]["message"]


def test_missing_column_is_an_error(data):
    from itd import validate
    _edit(data, "http", lambda df: df.drop(columns=["url"], inplace=True))
    rep = validate.validate_folder(str(data))
    assert rep["status"] == "failed" and "V2" in _rules(rep)
    assert "url" in [i for i in rep["issues"] if i["rule"] == "V2"][0]["message"]


def test_bad_date_is_an_error_with_the_line_number(data):
    from itd import validate
    _edit(data, "logon", lambda df: df.__setitem__("date", df["date"].where(df.index != 3, "2010-01-04 09:00")))
    rep = validate.validate_folder(str(data))
    v3 = [i for i in rep["issues"] if i["rule"] == "V3"][0]
    assert rep["status"] == "failed" and v3["count"] == 1 and v3["example_lines"] == [5]      # line 1 is the header


def test_warnings_do_not_stop_the_run(data):
    from itd import validate
    def damage(df):
        df.loc[5, "user"] = ""
        df.loc[7, "activity"] = "Reboot"
    _edit(data, "logon", damage)
    _edit(data, "email", lambda df: df.__setitem__("size", df["size"].where(df.index != 2, "abc")))
    rep = validate.validate_folder(str(data))
    assert rep["status"] == "warnings" and {"V4", "V6", "V7"} <= _rules(rep)
    assert rep["summary"]["errors"] == 0 and rep["summary"]["warnings"] >= 3


def test_duplicate_ids_inside_and_across_files(data):
    from itd import validate
    ids = pd.read_csv(data / "email.csv", dtype=str)["id"]
    _edit(data, "email", lambda df: df.__setitem__("id", df["id"].where(df.index != 9, ids[8])))
    _edit(data, "file", lambda df: df.__setitem__("id", df["id"].where(df.index != 1, ids[0])))
    rep = validate.validate_folder(str(data))
    v5 = [i for i in rep["issues"] if i["rule"] == "V5"][0]
    assert v5["count"] == 2 and "1 inside one file, 1 across files" in v5["message"]


def test_answer_file_rules(data):
    from itd import validate
    _edit(data, "answers", lambda df: df.__setitem__("id", df["id"].where(df.index != 0, "{NOPE}")))
    assert "V9" in _rules(validate.validate_folder(str(data)))
    _edit(data, "answers", lambda df: df.rename(columns={"id": "event"}, inplace=True))
    rep = validate.validate_folder(str(data))
    assert rep["status"] == "failed" and "V8" in _rules(rep)
    os.remove(data / "answers.csv")
    rep = validate.validate_folder(str(data))
    assert rep["status"] == "warnings" and "V10" in _rules(rep)


def test_report_text_names_rule_file_and_count(data):
    from itd import validate
    _edit(data, "logon", lambda df: df.__setitem__("date", df["date"].where(df.index != 3, "bad")))
    text = validate.format_report(validate.validate_folder(str(data)))
    assert "FAILED" in text and "[V3 error] logon.csv" in text and "lines 5" in text


def test_engine_stops_before_reading_when_validation_fails(data):
    from itd import engine
    os.remove(data / "device.csv")
    with pytest.raises(SystemExit, match="validation failed"):
        engine.run(str(data), retrain=True, report_dir=str(data / "rep"))
