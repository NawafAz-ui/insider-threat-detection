"""Starting a batch run from the dashboard: admin-only request, worker performs it, status is visible.
The API only files a request (status 'requested'); the worker is the only writer of progress."""
import os
import subprocess
import sys

os.environ.setdefault("MONGO_URI", "mock")
import pytest
from bson import ObjectId

ROOT = os.path.dirname(os.path.dirname(__file__))


@pytest.fixture
def env(tmp_path, monkeypatch):
    """A data folder with one dataset called cert_ok (only its logon.csv matters to the API) and no run requests."""
    from itd import config
    from itd.db import get_db
    root = tmp_path / "data"
    (root / "cert_ok").mkdir(parents=True)
    (root / "cert_ok" / "logon.csv").write_text("")
    (root / "no_logon").mkdir()
    monkeypatch.setattr(config, "DATA_ROOT", str(root))
    get_db().run_requests.delete_many({})
    return root


def _client():
    from fastapi.testclient import TestClient
    from itd.api import app
    return TestClient(app)


def _auth(role="admin", user="boss"):
    from itd import security
    return {"Authorization": "Bearer " + security.make_token(user, role)}


def _ask(c, retrain=False):
    return c.post("/api/run", json={"dataset": "cert_ok", "retrain": retrain}, headers=_auth())


def _work(runner):
    """What the worker does for one waiting request."""
    from itd import jobs
    from itd.db import get_db
    db = get_db("engine")
    return jobs.process(db, jobs.claim_next(db), runner)


def test_only_an_admin_can_start_a_run(env):
    from itd.db import get_db
    c = _client()
    assert c.post("/api/run", json={"dataset": "cert_ok"}).status_code == 401
    assert c.post("/api/run", json={"dataset": "cert_ok"}, headers=_auth("analyst", "alice")).status_code == 403
    assert get_db().run_requests.count_documents({}) == 0
    r = _ask(c)
    assert r.status_code == 202 and r.json()["status"] == "requested"


def test_request_is_stored_logged_and_visible_to_analysts(env):
    from itd.db import get_db
    c = _client()
    r = _ask(c, retrain=True).json()
    assert r["dataset"] == "cert_ok" and r["retrain"] is True and r["requested_by"] == "boss" and r["started_at"] is None
    assert get_db().run_requests.count_documents({}) == 1
    entry = get_db().access_log.find_one({"action": "run_requested", "user": "boss"})
    assert entry and entry["dataset"] == "cert_ok"
    seen = c.get("/api/run/status", headers=_auth("analyst", "alice")).json()["request"]
    assert seen["status"] == "requested" and "log" not in seen


def test_second_request_is_refused_while_one_is_active(env):
    from itd.db import get_db
    c = _client()
    assert _ask(c).status_code == 202
    assert _ask(c).status_code == 409
    assert get_db().run_requests.count_documents({}) == 1


def test_bad_dataset_names_are_refused(env):
    c = _client()
    for name in ("../x", "a/b", ".hidden", "x" * 80):
        assert c.post("/api/run", json={"dataset": name}, headers=_auth()).status_code == 422
    assert c.post("/api/run", json={"dataset": "cert_ok", "extra": 1}, headers=_auth()).status_code == 422
    assert c.post("/api/run", json={"dataset": "missing"}, headers=_auth()).status_code == 404
    assert c.post("/api/run", json={"dataset": "no_logon"}, headers=_auth()).status_code == 404


def test_dataset_list_is_for_admins_only(env):
    c = _client()
    assert c.get("/api/run/datasets", headers=_auth("analyst", "alice")).status_code == 403
    assert c.get("/api/run/datasets", headers=_auth()).json() == {"datasets": ["cert_ok"]}


def test_status_when_nothing_was_requested(env):
    assert _client().get("/api/run/status", headers=_auth()).json() == {"request": None}


def test_login_returns_the_role(env):
    from itd.db import get_db
    from itd.security import hash_password
    get_db().access_log.delete_many({"action": "login_failed"})        # earlier tests may have used up the throttle
    get_db().analyst_accounts.replace_one({"_id": "roleboss"}, {"_id": "roleboss", "password_hash": hash_password("Password1!"),
                                                                  "role": "admin"}, upsert=True)
    r = _client().post("/api/login", json={"username": "roleboss", "password": "Password1!"})
    assert r.status_code == 200 and r.json()["role"] == "admin"


def test_worker_records_done_and_the_api_shows_it(env):
    from itd.db import get_db
    c = _client()
    _ask(c)
    rid = ObjectId()

    def runner(path, retrain):
        print("0/5 Input validation ...")
        assert path.endswith("cert_ok") and retrain is False
        return {"run_id": rid}

    from itd import jobs
    claimed = jobs.claim_next(get_db("engine"))
    assert claimed["status"] == "running"
    assert c.get("/api/run/status", headers=_auth()).json()["request"]["status"] == "running"
    assert jobs.process(get_db("engine"), claimed, runner) == "done"
    admin_view = c.get("/api/run/status", headers=_auth()).json()["request"]
    assert admin_view["status"] == "done" and admin_view["finished_at"] and "Input validation" in admin_view["log"]
    assert "log" not in c.get("/api/run/status", headers=_auth("analyst", "alice")).json()["request"]
    assert get_db().run_requests.find_one()["run_id"] == rid


def test_failed_runs_keep_the_reason_and_a_new_request_is_allowed(env):
    c = _client()

    def stops(path, retrain):
        print("    [V1 error] device.csv: a required CSV file is missing: device.csv - 1")
        raise SystemExit("Input validation failed; fix the errors above and run again.")

    def breaks(path, retrain):
        raise ValueError("x" * 900)

    _ask(c)
    assert _work(stops) == "failed"
    st = c.get("/api/run/status", headers=_auth()).json()["request"]
    assert st["status"] == "failed" and st["message"].startswith("Input validation failed") and "[V1 error]" in st["log"]
    assert _ask(c).status_code == 202                                   # a finished request no longer blocks
    assert _work(breaks) == "failed"
    st = c.get("/api/run/status", headers=_auth()).json()["request"]
    assert st["message"].startswith("ValueError: xxx") and len(st["message"]) == 500


def test_worker_loop_handles_waiting_requests_and_clears_stale_ones(env):
    import time
    from itd import worker
    from itd.db import get_db
    c = _client()
    stale = {"_id": ObjectId(), "status": "running", "dataset": "cert_ok", "retrain": False, "requested_by": "boss",
             "requested_at": time.time() - 100, "started_at": time.time() - 90}
    get_db().run_requests.insert_one(stale)
    worker.serve(poll=0, once=True, runner=lambda p, r: {})              # only the stale request exists
    assert get_db().run_requests.find_one({"_id": stale["_id"]})["status"] == "failed"
    assert "worker stopped" in get_db().run_requests.find_one({"_id": stale["_id"]})["message"]
    assert _ask(c).status_code == 202
    worker.serve(poll=0, once=True, runner=lambda p, r: {})
    assert c.get("/api/run/status", headers=_auth()).json()["request"]["status"] == "done"


def test_request_documents_follow_the_schema(env):
    from itd import schema
    from itd.db import get_db
    c = _client()

    def stops(path, retrain):
        raise SystemExit("Input validation failed")

    _ask(c)
    _work(lambda p, r: {"run_id": ObjectId()})
    _ask(c)
    _work(stops)
    docs = list(get_db().run_requests.find())
    assert len(docs) == 2
    for d in docs:
        assert schema.validate(schema.SCHEMAS["run_requests"], d) == []


def test_request_to_result_through_the_real_engine(env, tmp_path):
    """Dashboard request -> worker -> engine -> results visible through the API (test database, real engine code)."""
    from itd import engine, worker
    from itd.db import get_db
    c = _client()
    subprocess.check_call([sys.executable, os.path.join(ROOT, "scripts/generate_synthetic_cert.py"), str(env / "cert_demo"),
                           "--users", "60", "--days", "80", "--insiders", "8"])
    r = c.post("/api/run", json={"dataset": "cert_demo", "retrain": True}, headers=_auth())
    assert r.status_code == 202
    worker.serve(poll=0, once=True,
                 runner=lambda path, retrain: engine.run(path, retrain=retrain, report_dir=str(tmp_path / "rep")))
    st = c.get("/api/run/status", headers=_auth()).json()["request"]
    assert st["status"] == "done", st
    assert "Done in" in st["log"]                                       # the log keeps the end of the engine output
    doc = get_db().run_requests.find_one()
    assert get_db().runs.find_one({"_id": doc["run_id"]})["validation"]["status"] in ("ok", "warnings")
    assert get_db().results.count_documents({"run_id": doc["run_id"]}) > 0
    assert c.get("/api/sessions", headers=_auth("analyst", "alice")).status_code == 200
