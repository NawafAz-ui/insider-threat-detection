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


def test_unknown_role_and_expired_token(client, monkeypatch):
    from itd import config
    from itd.security import make_token
    viewer = {"Authorization": "Bearer " + make_token("alice", "viewer")}
    assert client.get("/api/sessions", headers=viewer).status_code == 403            # role is neither analyst nor admin
    monkeypatch.setattr(config, "JWT_MINUTES", -1)                                  # token already expired when issued
    old = {"Authorization": "Bearer " + make_token("alice", "analyst")}
    assert client.get("/api/sessions", headers=old).status_code == 401


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
    """A (mocked) LLM reply may only cite evidence ids that exist; bad ids are dropped. The reply is a list of statements."""
    from itd import assistant, config
    from itd.db import get_db
    doc = get_db().results.find_one({"flagged": True})

    class R:
        def raise_for_status(self): pass
        def json(self): return {"content": [{"type": "text", "text": '{"statements": [{"text": "Because of S1.", "evidence": ["S1", "X9", "R"]}]}'}]}
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


def test_offline_answer_for_session_below_threshold():
    """User history lists sessions under the threshold too: the answer must not call them flagged."""
    from itd import assistant
    doc = {"risk_score": 12.0, "flagged": False, "top_shap": [], "baseline_deviations": []}
    answer = assistant._template_answer(doc, "Why was this flagged?")["answer"]
    assert "below the flag threshold" in answer and "above" not in answer


def test_risk_engine_weights_and_threshold():
    import numpy as np
    from itd.risk import calibrate, combine, fit_risk_engine
    y = np.array([0, 0, 0, 0, 1, 1])
    val = {"lr": np.array([.1, .2, .1, .3, .9, .8]), "xgb": np.array([0, .1, .2, .1, .8, .9]),
           "iforest": np.array([.5, .4, .6, .5, .5, .6])}
    cfg = fit_risk_engine(val, y)
    assert abs(sum(cfg["weights"].values()) - 1) < 1e-9
    risk = combine(calibrate(val, cfg["calibrators"]), cfg["weights"])
    assert risk.min() >= 0 and risk.max() <= 100
    assert (risk[y == 1] >= cfg["threshold"]).all() and (risk[y == 0] < cfg["threshold"]).all()


def test_aggregator_counts_per_session():
    import pandas as pd
    from itd.aggregate import Aggregator
    agg = Aggregator()
    agg.add("device", pd.DataFrame({"sid": [0, 0, 1], "activity": ["Connect", "Disconnect", "Connect"]}))
    agg.add("email", pd.DataFrame({"sid": [0, 0], "to": ["a@dtaa.com", "b@gmail.com"], "size": ["2048", "1024"], "attachments": ["1", "0"]}))
    agg.add("http", pd.DataFrame({"sid": [0, 0, 1], "url": ["http://monster.com/x", "http://monster.com/x", "http://dropbox.com/y"]}))
    out = agg.result(2)
    assert out.loc[0, "n_device_connect"] == 1 and out.loc[1, "n_device_connect"] == 1     # Disconnect is not counted
    assert out.loc[0, "n_email_sent"] == 2 and out.loc[0, "n_email_external"] == 1 and out.loc[0, "email_size_kb"] == 3
    assert out.loc[0, "n_http_job"] == 2 and out.loc[0, "n_distinct_urls"] == 1 and out.loc[1, "n_http_leak"] == 1


def test_top_shap_is_positive_and_at_most_three():
    import numpy as np
    from itd.explain import top_shap
    from itd.features import FEATURES
    sv, x = np.zeros(len(FEATURES)), np.ones(len(FEATURES))
    sv[:5] = [0.5, 0.4, 0.3, 0.2, -1.0]
    out = top_shap(sv, x, {})
    assert [o["feature"] for o in out] == FEATURES[:3] and all(o["shap"] > 0 for o in out)
    assert top_shap(-np.ones(len(FEATURES)), x, {}) == []


def test_calibration_keeps_the_order_and_is_fitted_on_validation_scores():
    import numpy as np
    from itd.risk import calibrate, fit_calibrators
    y = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 1])
    s = {"m": np.array([.1, .2, .1, .3, .2, .4, .6, .8, .7, .9])}
    cal = fit_calibrators(s, y)
    p = calibrate(s, cal)["m"]
    assert cal["m"]["a"] > 0 and ((p > 0) & (p < 1)).all()
    assert (np.argsort(p, kind="stable") == np.argsort(s["m"], kind="stable")).all()      # same order, only the scale changes
    assert p[y == 1].mean() > p[y == 0].mean()


def test_evaluate_model_uses_the_given_threshold_not_the_test_labels():
    import numpy as np
    from itd.risk import evaluate_model
    y, s = np.array([0, 0, 1, 1]), np.array([.1, .4, .35, .9])
    m = evaluate_model(y, s, 0.5)                              # the best threshold on these labels would be 0.35
    assert m["validation_threshold"] == 0.5 and m["flagged"] == 1 and m["precision"] == 1.0 and m["recall"] == 0.5


def test_stored_models_keep_calibrators_and_validation_thresholds(client):
    from itd.db import get_db
    doc = get_db().trained_models.find_one({"_id": "current"})
    assert set(doc["risk"]["calibrators"]) == {"lr", "xgb", "iforest"}
    for k, m in doc["metrics"]["test"].items():
        if k == "risk_engine":
            assert 0 <= m["brier"] <= 1
            continue
        assert m["validation_threshold"] == doc["risk"]["val_thresholds"][k] and "best_threshold" not in m
        assert 0 <= m["brier"] <= 1 and 0 <= m["brier_raw"] <= 1


def _same_day_sessions():
    import pandas as pd
    from itd.aggregate import Aggregator
    day = pd.Timestamp("2010-03-02")
    rows = [("a", "PC1", 8), ("a", "PC2", 10), ("a", "PC1", 13), ("b", "PC9", 9), ("a", "PC1", 24 + 9)]
    sessions = pd.DataFrame({"session_id": [f"S{i}" for i in range(len(rows))], "sid": range(len(rows)),
                             "user": [r[0] for r in rows], "pc": [r[1] for r in rows],
                             "start": [day + pd.Timedelta(hours=r[2]) for r in rows]})
    sessions["end"] = sessions["start"] + pd.Timedelta(hours=1)
    return sessions, Aggregator().result(len(rows))


def test_day_counts_use_only_the_sessions_up_to_the_current_one():
    from itd.features import session_features
    sessions, agg = _same_day_sessions()
    full = session_features(sessions, agg)
    assert full["n_sessions_day"].tolist() == [1, 2, 3, 1, 1]            # the next day starts again at 1
    assert full["n_distinct_pcs_day"].tolist() == [1, 2, 2, 1, 1]
    part = session_features(sessions.iloc[:3], agg)                      # dropping later sessions changes nothing earlier
    cols = ["n_sessions_day", "n_distinct_pcs_day"]
    assert (full[cols].iloc[:3].to_numpy() == part[cols].to_numpy()).all()


def _user_frame(start, n, user="u"):
    import pandas as pd
    from itd.features import BASE_METRICS
    f = pd.DataFrame({m: [1.0] * n for m in BASE_METRICS})
    f["user"], f["start"] = user, pd.date_range(start, periods=n, freq="D")
    f.index = [f"S{start}{i}" for i in range(n)]
    return f


def test_running_the_same_data_again_does_not_count_it_twice():
    from itd.baselines import add_deviations
    f = _user_frame("2010-01-04 09:00", 12)
    out1, final = add_deviations(f)
    saved = {u: {"_id": u, **v} for u, v in final.items()}
    out2, final2 = add_deviations(f, saved)
    assert final["u"]["n"] == final2["u"]["n"] == 12 and "last" in final["u"]
    assert out1["hours_since_prev_session"].equals(out2["hours_since_prev_session"])
    old = {u: {k: v for k, v in d.items() if k != "last"} for u, d in saved.items()}          # saved before the last time was kept
    assert add_deviations(f, old)[1]["u"]["n"] == 12


def test_a_later_batch_continues_the_saved_baseline_and_recency():
    from itd.baselines import add_deviations
    _, final = add_deviations(_user_frame("2010-01-04 09:00", 12))
    saved = {u: {"_id": u, **v} for u, v in final.items()}
    out, final2 = add_deviations(_user_frame("2010-02-01 09:00", 3), saved)
    assert final2["u"]["n"] == 15
    assert out["hours_since_prev_session"].iloc[0] > 24 * 7              # gap counted from the last session of the first batch


def _hosted_reply(monkeypatch, text):
    from itd import assistant, config

    class R:
        def raise_for_status(self): pass
        def json(self): return {"content": [{"type": "text", "text": text}]}
    monkeypatch.setattr(config, "LLM_API_KEY", "test")
    monkeypatch.setattr(assistant.httpx, "post", lambda *a, **k: R())
    return assistant


_DOC = {"risk_score": 84.3, "flagged": True, "baseline_deviations": [],
        "top_shap": [{"text": "Connected 5 removable device(s) (usual 0.2).", "shap": 0.62, "feature": "n_device_connect"}]}


def test_hosted_statements_are_checked_one_by_one(monkeypatch):
    import json
    reply = json.dumps({"statements": [
        {"text": "The session scored 84 out of 100.", "evidence": ["R"]},                 # rounded number, supported
        {"text": "It connected 5 removable devices.", "evidence": ["S1"]},                # supported
        {"text": "It connected 9 removable devices.", "evidence": ["S1"]},                # number not in the evidence
        {"text": "The user is guilty.", "evidence": []},                                  # no evidence cited
        {"text": "The score is 84.", "evidence": ["X9"]}]})                               # cites an id that does not exist
    res = _hosted_reply(monkeypatch, reply).answer(_DOC, "Why was this flagged?")
    assert res["mode"] == "llm" and res["withheld"] == 3 and res["fields_used"] == ["R", "S1"]
    assert "84 out of 100" in res["answer"] and "9 removable" not in res["answer"] and "guilty" not in res["answer"]


def test_hosted_answer_says_so_when_no_statement_is_supported(monkeypatch):
    for reply in ('{"statements": []}', '{"statements": [{"text": "Score 99.", "evidence": ["R"]}]}'):
        res = _hosted_reply(monkeypatch, reply).answer(_DOC, "Is this user a thief?")
        assert res["answer"].startswith("The stored evidence for this session does not support") and res["fields_used"] == []


def test_hosted_reply_in_the_old_format_uses_the_offline_answer(monkeypatch):
    res = _hosted_reply(monkeypatch, '{"answer": "Because of S1.", "fields_used": ["S1"]}').answer(_DOC, "why?")
    assert res["mode"] == "template"


def test_missing_log_file_and_wrong_date_format_stop_the_run(tmp_path):
    import pytest
    from itd.ingest import load_dataset
    quiet = dict(pseudonymize=False, log=lambda *a, **k: None)
    with pytest.raises(FileNotFoundError, match="Missing in .*logon.csv"):
        load_dataset(str(tmp_path), **quiet)
    for name in ("logon", "device", "email", "file", "http"):
        (tmp_path / f"{name}.csv").write_text("id,date,user,pc,activity,to,size,attachments,filename,url\nE1,2010-01-04 09:00,u,pc,Logon,,,,,\n")
    with pytest.raises(ValueError):                           # dates must be MM/DD/YYYY HH:MM:SS
        load_dataset(str(tmp_path), **quiet)


def test_login_throttle_last(client):
    """Kept last: failed attempts lock this test client's address for the throttle window."""
    codes = [client.post("/api/login", json={"username": "bob", "password": "x"}).status_code for _ in range(7)]
    assert codes[0] == 401 and codes[-1] == 429
