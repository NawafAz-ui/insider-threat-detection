import os
import subprocess
import sys

os.environ["MONGO_URI"] = "mock"
import pytest
from fastapi.testclient import TestClient

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(__file__))


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    d = tmp_path_factory.mktemp("cert")
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts/generate_synthetic_cert.py"), str(d),
                           "--users", "60", "--days", "80", "--insiders", "8"])
    from itd import engine
    from itd.db import get_db
    from itd.security import hash_password
    engine.run(str(d), retrain=True, report_dir=str(d / "rep"))
    get_db().analyst_accounts.insert_one({"_id": "alice", "password_hash": hash_password("pw123"), "role": "analyst"})
    from itd.api import app
    return TestClient(app)


def tok(c, pw="pw123"):
    r = c.post("/api/login", json={"username": "alice", "password": pw})
    return r


def test_feature_count():
    from itd.features import FEATURES
    assert len(FEATURES) == 39


def test_login_and_auth(client):
    assert tok(client, "bad").status_code == 401
    assert client.get("/api/sessions").status_code == 401
    assert client.get("/api/sessions", headers={"Authorization": "Bearer junk"}).status_code == 401
    assert tok(client).status_code == 200


def test_injection_rejected(client):
    r = client.post("/api/login", json={"username": {"$ne": ""}, "password": {"$ne": ""}})
    assert r.status_code == 422
    h = {"Authorization": "Bearer " + tok(client).json()["token"]}
    assert client.get("/api/sessions/%7B%22%24ne%22%3A1%7D", headers=h).status_code == 422


def test_list_sorted_and_detail(client):
    h = {"Authorization": "Bearer " + tok(client).json()["token"]}
    body = client.get("/api/sessions", headers=h).json()
    lst = body["sessions"]
    assert body["total"] >= len(lst) and body["threshold"] >= 0
    assert lst and all(a["risk_score"] >= b["risk_score"] for a, b in zip(lst, lst[1:]))
    d = client.get(f"/api/sessions/{lst[0]['session_id']}", headers=h).json()
    assert 0 <= d["risk_score"] <= 100 and len(d["top_shap"]) <= 3 and "R" in d["evidence"]


def test_chat_names_fields_and_is_logged(client):
    from itd.db import get_db
    h = {"Authorization": "Bearer " + tok(client).json()["token"]}
    sid = client.get("/api/sessions", headers=h).json()["sessions"][0]["session_id"]
    r = client.post(f"/api/sessions/{sid}/chat", headers=h, json={"question": "Why was this flagged?"}).json()
    assert r["fields_used"] and set(r["fields_used"]) <= set(r["evidence"])
    assert get_db().access_log.count_documents({"action": "assistant_question"}) >= 1
    assert client.post(f"/api/sessions/{sid}/chat", headers=h, json={"question": "x" * 301}).status_code == 422


def test_assistant_gets_no_identifiers(client):
    from itd import assistant
    from itd.db import get_db
    doc = get_db().results.find_one({"flagged": True})
    blob = str(assistant.build_evidence(doc))
    assert doc["user"] not in blob and doc["pc"] not in blob


def test_list_is_fast(client):
    import time
    h = {"Authorization": "Bearer " + tok(client).json()["token"]}
    t = time.time()
    client.get("/api/sessions", headers=h)
    assert time.time() - t < 2          # proposal: dashboard pages load in under two seconds


def test_sessionization_rules():
    import pandas as pd
    from itd.sessionize import build_sessions
    d = lambda s: pd.Timestamp(s)
    ev = pd.DataFrame([
        ("u", "pc", d("2010-01-04 09:00"), "Logon"), ("u", "pc", d("2010-01-04 17:00"), "Logoff"),   # normal
        ("u", "pc", d("2010-01-05 09:00"), "Logon"),                                               # missing logoff, next logon closes it
        ("u", "pc", d("2010-01-05 11:00"), "Logon"),
        ("u", "pc", d("2010-01-06 09:00"), "Logon"),                                               # missing logoff, capped at 12 h
        ("u", "pc", d("2010-01-06 22:00"), "Logon"), ("u", "pc", d("2010-01-07 01:00"), "Logoff"),  # crosses midnight
    ], columns=["user", "pc", "time", "activity"])
    s = build_sessions(ev).sort_values("start").reset_index(drop=True)
    assert len(s) == 5
    assert s.loc[0, "logoff_missing"] == 0 and s.loc[1, "logoff_missing"] == 1
    assert s.loc[1, "end"] == d("2010-01-05 11:00")
    assert (s.loc[3, "end"] - s.loc[3, "start"]) == pd.Timedelta(hours=12) or s.loc[3, "end"] <= d("2010-01-06 22:00")
    assert s.loc[4, "end"] == d("2010-01-07 01:00")


def test_baseline_uses_only_past_sessions():
    import pandas as pd
    from itd.baselines import add_deviations
    from itd.features import BASE_METRICS
    n = 12
    f = pd.DataFrame({m: [1.0] * n for m in BASE_METRICS})
    f["n_device_connect"] = [0.0] * (n - 1) + [5.0]                     # sudden USB use in the last session
    f["user"], f["start"] = "u", pd.date_range("2010-01-04 09:00", periods=n, freq="D")
    f.index = [f"S{i}" for i in range(n)]
    out, final = add_deviations(f)
    assert out["dev_n_device_connect"].iloc[-1] > 3 and out["dev_n_device_connect"].iloc[:5].eq(0).all()
    assert final["u"]["n"] == n


def test_working_gap_ignores_weekend():
    import numpy as np
    from itd.baselines import _working_gap_hours
    fri, mon = np.datetime64("2010-01-08T17:00"), np.datetime64("2010-01-11T09:00")
    assert _working_gap_hours(fri, mon) == 16.0                           # 64 h on the clock minus 48 h weekend


def test_model_tamper_is_detected(client):
    import pytest
    from itd import engine
    from itd.db import get_db
    doc = get_db().trained_models.find_one({"_id": "current"})
    good = dict(doc["sha256"])
    get_db().trained_models.update_one({"_id": "current"}, {"$set": {"sha256.xgb": "0" * 64}})
    with pytest.raises(engine.ModelIntegrityError):
        engine.load_models()
    get_db().trained_models.update_one({"_id": "current"}, {"$set": {"sha256": good}})
    assert engine.load_models() is not None


def test_https_required_when_enabled(client):
    from itd import config
    config.REQUIRE_HTTPS = True
    try:
        assert client.get("/api/sessions").status_code == 426
        assert client.get("/api/sessions", headers={"x-forwarded-proto": "https"}).status_code == 401
    finally:
        config.REQUIRE_HTTPS = False


def test_llm_answer_is_validated(client, monkeypatch):
    """A (mocked) LLM reply may only cite evidence ids that exist; bad ids are dropped."""
    from itd import assistant, config
    from itd.db import get_db
    doc = get_db().results.find_one({"flagged": True})

    class R:
        def raise_for_status(self): pass
        def json(self): return {"content": [{"type": "text", "text": '{"answer": "Because of S1.", "fields_used": ["S1", "X9", "R"]}'}]}
    monkeypatch.setattr(config, "LLM_API_KEY", "test")
    monkeypatch.setattr(assistant.httpx, "post", lambda *a, **k: R())
    res = assistant.answer(doc, "why?")
    assert res["mode"] == "llm" and set(res["fields_used"]) <= {"S1", "R"} and "X9" not in res["fields_used"]
    monkeypatch.setattr(assistant.httpx, "post", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("down")))
    assert assistant.answer(doc, "why?")["mode"] == "template"         # falls back when the API fails


def test_spedia_adapter_and_cross_eval(client, tmp_path):
    import json
    from helpers import make_fake_spedia
    from itd import cross_eval, spedia
    cert = tmp_path / "cert"
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts/generate_synthetic_cert.py"), str(cert),
                           "--users", "60", "--days", "80", "--insiders", "8"])
    make_fake_spedia(str(cert), str(tmp_path / "fake.csv"))
    spedia.convert(str(tmp_path / "fake.csv"), json.load(open(os.path.join(ROOT, "spedia_mapping.example.json"))), str(tmp_path / "sp"))
    res = cross_eval.run(str(cert), str(tmp_path / "sp"), str(tmp_path / "rep"))
    assert res["shared_features"] and res["cross_dataset_test"]["sessions"] > 0


def test_login_throttle_last(client):
    """Kept last: failed attempts lock this test client's address for the throttle window."""
    codes = [client.post("/api/login", json={"username": "bob", "password": "x"}).status_code for _ in range(7)]
    assert codes[0] == 401 and codes[-1] == 429
