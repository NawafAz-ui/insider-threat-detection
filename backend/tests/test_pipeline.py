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


def _auth(client):
    return {"Authorization": "Bearer " + tok(client).json()["token"]}


def test_user_history_endpoint(client):
    from itd.db import get_db
    h = _auth(client)
    first = client.get("/api/sessions", headers=h).json()["sessions"][0]
    r = client.get(f"/api/users/{first['user']}", headers=h)
    assert r.status_code == 200
    d = r.json()
    starts = [x["start"] for x in d["sessions"]]
    assert starts == sorted(starts)                                    # oldest first, ready for a timeline
    assert d["summary"]["sessions"] >= len(d["sessions"]) and d["summary"]["flagged"] >= 1
    assert d["summary"]["highest_risk"] >= first["risk_score"] - 0.1
    assert len(d["baseline"]) == 10 and all({"label", "mean", "std"} <= set(b) for b in d["baseline"])
    assert d["threshold"] > 0
    assert get_db().access_log.count_documents({"action": "user_viewed"}) >= 1


def test_user_history_rejects_bad_input(client):
    h = _auth(client)
    assert client.get("/api/users/U9999999", headers=h).status_code == 404
    assert client.get("/api/users/%24ne", headers=h).status_code == 422
    assert client.get("/api/users/" + "A" * 65, headers=h).status_code == 422
    assert client.get("/api/users/U0001").status_code == 401           # no token


def test_latest_run_endpoint(client):
    h = _auth(client)
    d = client.get("/api/run/latest", headers=h).json()
    assert d["sessions"] > 0 and d["flagged"] > 0 and d["threshold"] > 0 and d["seconds"] >= 0
    assert set(d["weights"]) == {"lr", "xgb", "iforest"}
    assert "risk_engine" in d["metrics"]["test"] and "precision" in d["metrics"]["test"]["risk_engine"]
    assert client.get("/api/run/latest").status_code == 401


def test_offline_answer_is_short_and_focused():
    from itd import assistant
    doc = {"risk_score": 88.0,
           "top_shap": [{"text": "Handled 24 archive (.zip) files (usual 0.0).", "shap": 3.0, "strength": "strong"},
                        {"text": "Activity rate was 15.7 events per hour.", "shap": 2.0, "strength": "strong"},
                        {"text": "Session lasted 172 minutes (usual 480).", "shap": 0.2, "strength": "minor"}],
           "baseline_deviations": [{"text": "Logged on at 21.7h (usual 9.3h).", "z": 10.0}]}
    general = assistant._template_answer(doc, "Why was this flagged?")
    assert len(general["answer"]) < 700 and "SHAP" not in general["answer"]
    assert "S3" not in general["fields_used"] and "R" in general["fields_used"]      # minor reason left out
    assert "10 or more" in general["answer"]
    zip_q = assistant._template_answer(doc, "Were zip files involved?")
    assert zip_q["fields_used"] == ["R", "S1"]
    late_q = assistant._template_answer(doc, "What about the logon time?")
    assert "B1" in late_q["fields_used"] and "S1" not in late_q["fields_used"]


def test_offline_answer_merges_duplicates_and_ignores_generic_words():
    """Regression for what the dashboard showed: the zip fact appeared twice and 'files' pulled in an unrelated item."""
    from itd import assistant
    doc = {"risk_score": 100.0,
           "top_shap": [{"text": "Handled 24 archive (.zip) files (usual 0.0).", "shap": 3.7, "strength": "strong"},
                        {"text": "Activity rate was 15.7 events per hour.", "shap": 3.6, "strength": "strong"}],
           "baseline_deviations": [{"text": "Logged on at 21.7h (usual 9.3h).", "z": 10.0},
                                   {"text": "Touched 27 files (usual 4.6).", "z": 10.0},
                                   {"text": "Handled 24 archive (.zip) files (usual 0.0).", "z": 10.0}]}
    r = assistant._template_answer(doc, "Were zip files involved?")
    assert r["answer"].count("archive") == 1 and "Touched" not in r["answer"]
    assert set(r["fields_used"]) == {"R", "S1", "B3"}                   # both ids cited, one sentence
    g = assistant._template_answer(doc, "Why was this flagged?")
    assert g["answer"].count("archive") == 1


def test_stored_documents_follow_the_schema(client):
    """Every document the engine, the API and the scripts wrote must pass the database rules."""
    from itd import schema
    from itd.db import get_db
    for name, (n, bad) in schema.check(get_db()).items():
        assert not bad, f"{name}: {bad[:3]}"
    assert schema.check(get_db())["results"][0] > 0


def test_results_are_linked_to_their_run(client):
    from itd.db import get_db
    db = get_db()
    run = db.runs.find_one(sort=[("at", -1)])
    assert db.results.count_documents({"run_id": run["_id"]}) == db.results.count_documents({})


def test_schema_rejects_bad_documents():
    from datetime import datetime
    from itd import schema
    S = schema.SCHEMAS
    good = {"_id": "alice", "password_hash": "$2b$12$" + "a" * 53, "role": "analyst"}
    assert schema.validate(S["analyst_accounts"], good) == []
    assert schema.validate(S["analyst_accounts"], {**good, "role": "superuser"})
    assert schema.validate(S["analyst_accounts"], {**good, "password_hash": "plain-text"})
    assert schema.validate(S["analyst_accounts"], {"_id": "x", "role": "analyst"})                      # missing hash
    assert schema.validate(S["access_log"], {"at": 1.0, "user": "u", "action": "deleted_everything"})
    assert schema.validate(S["access_log"], {"at": 1.0, "user": "u", "action": "assistant_question", "question": "x" * 301})
    assert schema.validate(S["access_log"], {"at": 1.0, "user": "u", "action": "login_ok", "ip": None}) == []
    assert schema.validate(S["runs"], {"_id": 1})                                                      # wrong type and missing fields


def test_real_mongo_enforces_the_schema():
    """Needs a real server: set ITD_TEST_MONGO=mongodb://127.0.0.1:27017 (skipped otherwise)."""
    import pytest
    uri = os.environ.get("ITD_TEST_MONGO")
    if not uri:
        pytest.skip("ITD_TEST_MONGO not set")
    from pymongo import MongoClient
    from pymongo.errors import WriteError
    from itd import schema
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    client.drop_database("itd_schema_test")
    db = client["itd_schema_test"]
    schema.apply(db)
    assert all(schema.server_status(db).values())
    good = {"_id": "alice", "password_hash": "$2b$12$" + "a" * 53, "role": "analyst"}
    db.analyst_accounts.insert_one(dict(good))
    with pytest.raises(WriteError):
        db.analyst_accounts.insert_one({**good, "_id": "bob", "role": "superuser"})
    with pytest.raises(WriteError):
        db.analyst_accounts.update_one({"_id": "alice"}, {"$set": {"role": "root"}})
    client.drop_database("itd_schema_test")


def test_health_endpoint(client):
    r = client.get("/api/health")
    assert r.status_code == 200 and r.json() == {"status": "ok", "database": "up"}


def test_database_down_gives_a_clear_503(client, monkeypatch):
    from pymongo.errors import ServerSelectionTimeoutError
    h = _auth(client)                                                # log in while the database still works

    def down(*a, **k):
        raise ServerSelectionTimeoutError("localhost:27017: connection refused")
    monkeypatch.setattr("itd.api.get_db", down)
    monkeypatch.setattr("itd.security.get_db", down)
    r = client.get("/api/sessions", headers=h)
    assert r.status_code == 503 and "database is not reachable" in r.json()["detail"]
    assert "27017" not in r.text                                     # no internal details
    assert client.get("/api/health").status_code == 503


def test_unexpected_error_hides_internal_details(client, monkeypatch):
    from fastapi.testclient import TestClient
    from itd.api import app
    h = _auth(client)

    def boom(*a, **k):
        raise RuntimeError("secret internal detail")
    monkeypatch.setattr("itd.api.get_db", boom)
    quiet = TestClient(app, raise_server_exceptions=False)
    r = quiet.get("/api/sessions", headers=h)
    assert r.status_code == 500 and "secret internal detail" not in r.text and "Traceback" not in r.text


def test_both_workflows_end_to_end(client):
    """Workflow 1: review a flagged session. Workflow 2: from that session, investigate the user."""
    h = _auth(client)
    top = client.get("/api/sessions?limit=1", headers=h).json()["sessions"][0]                # list
    detail = client.get(f"/api/sessions/{top['session_id']}", headers=h).json()                # detail
    assert detail["user"] == top["user"] and detail["top_shap"]
    answer = client.post(f"/api/sessions/{top['session_id']}/chat", headers=h, json={"question": "Why was this flagged?"}).json()
    assert set(answer["fields_used"]) <= set(detail["evidence"])                              # assistant names real evidence
    history = client.get(f"/api/users/{detail['user']}", headers=h).json()                     # workflow 2
    assert top["session_id"] in [x["session_id"] for x in history["sessions"]]                # same session is in the history
    assert history["threshold"] == detail["threshold"]
    run = client.get("/api/run/latest", headers=h).json()
    assert run["threshold"] == detail["threshold"]                                             # one threshold everywhere


def test_login_throttle_last(client):
    """Kept last: failed attempts lock this test client's address for the throttle window."""
    codes = [client.post("/api/login", json={"username": "bob", "password": "x"}).status_code for _ in range(7)]
    assert codes[0] == 401 and codes[-1] == 429
