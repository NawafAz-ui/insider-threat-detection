"""Run report: the HTML builder (itd/report.py) and the download endpoint."""
import os
from datetime import datetime, timedelta

os.environ.setdefault("MONGO_URI", "mock")
import pytest
from bson import ObjectId

from itd import report

NOW = datetime(2026, 11, 7, 9, 0)


def _metrics(refs=True):
    test = {"risk_engine": {"precision": .89, "recall": 1.0, "f1": .94, "pr_auc": 1.0, "brier": .001},
            "lr": {"precision": 1.0, "recall": 1.0, "f1": 1.0, "pr_auc": 1.0, "brier": .001, "validation_threshold": .5}}
    if refs:
        test["rule_after_hours"] = {"precision": .2, "recall": .3, "f1": .26, "pr_auc": .08, "threshold": 1.0}
        test["rule_deviation"] = {"precision": .4, "recall": .44, "f1": .42, "pr_auc": .36, "threshold": 5.1}
        test["no_skill"] = {"precision": .01, "recall": 1.0, "f1": .03, "pr_auc": .01}
    return {"test": test}


def _run(refs=True):
    return {"_id": ObjectId(), "at": 1794033000.0, "seconds": 9.9, "sessions": 7329, "flagged": 66, "threshold": 19.3,
            "weights": {"lr": .5, "xgb": .5}, "validation": {"status": "ok", "errors": 0, "warnings": 0}, "metrics": _metrics(refs)}


def _top(user="U0001", text="Logged on at 22.0h (usual 9.1h)."):
    return {"user": user, "start": NOW, "end": NOW + timedelta(minutes=172), "risk_score": 99.6,
            "top_shap": [{"text": text}, {"text": text}],
            "baseline_deviations": [{"text": "Sent 9 emails (usual 1.0)."}, {"text": "Never printed third line."}]}


def test_report_shows_the_run_the_comparison_and_the_top_sessions():
    h = report.render(_run(), [_top()], NOW)
    for needle in ("Combined risk score", "Logistic Regression", "Rule: after-hours session", "No skill: flag every session",
                   "7,329", "66 (0.9% of sessions)", "19.3", "172", "U0001", "Sent 9 emails", "not research findings",
                   "The combined risk score reaches F1 0.94. The best simple rule reaches 0.42 and flagging every session reaches 0.03"):
        assert needle in h, needle
    assert h.count("Logged on at 22.0h") == 1                      # the same sentence twice is printed once
    assert "Never printed third line" not in h                      # at most 2 explanation lines and 1 deviation per session


def test_report_escapes_text_that_comes_from_the_database():
    h = report.render(_run(), [_top(user="<script>alert(1)</script>", text="<img src=x onerror=alert(2)>")], NOW)
    assert "<script>" not in h and "<img" not in h
    assert "&lt;script&gt;" in h and "&lt;img" in h


def test_report_handles_old_runs_empty_lists_and_missing_metrics():
    assert "trained before the simple reference methods" in report.render(_run(refs=False), [], NOW)
    assert "No flagged sessions" in report.render(_run(), [], NOW)
    assert "no stored test results" in report.render({"at": 1794033000.0}, [], NOW)


def _client():
    from fastapi.testclient import TestClient
    from itd.api import app
    return TestClient(app)


def _auth(role="analyst", user="alice"):
    from itd import security
    return {"Authorization": "Bearer " + security.make_token(user, role)}


@pytest.fixture
def stored():
    from itd.db import get_db
    db = get_db()
    db.runs.delete_many({})
    db.results.delete_many({})
    db.access_log.delete_many({"action": "report_viewed"})
    return db


def test_report_needs_a_login_and_a_run(stored):
    c = _client()
    assert c.get("/api/run/report").status_code == 401
    assert c.get("/api/run/report", headers=_auth()).status_code == 404


def test_report_download_is_html_logged_not_cached_and_lists_only_this_runs_top_sessions(stored):
    run = _run()
    stored.runs.insert_one(run)

    def result(user, risk, run_id, flagged=True):
        stored.results.insert_one({"_id": user, "session_id": user, "run_id": run_id, "user": user, "start": NOW,
                                   "end": NOW + timedelta(minutes=60), "risk_score": risk, "flagged": flagged,
                                   "top_shap": [], "baseline_deviations": []})
    for i in range(12):
        result(f"UTOP{i:02d}", 50.0 + i, run["_id"])                 # 12 flagged sessions: only the 10 highest are printed
    result("UOTHERRUN", 100.0, ObjectId())                           # another run
    result("UNOTFLAGGED", 99.0, run["_id"], flagged=False)
    r = _client().get("/api/run/report", headers=_auth())
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/html")
    assert "attachment" in r.headers["content-disposition"] and r.headers["cache-control"] == "no-store"
    body = r.text
    assert "UTOP11" in body and "UTOP02" in body
    assert "UTOP00" not in body and "UTOP01" not in body            # below the top 10
    assert "UOTHERRUN" not in body and "UNOTFLAGGED" not in body
    assert body.index("UTOP11") < body.index("UTOP10")              # highest risk first
    entry = stored.access_log.find_one({"action": "report_viewed", "user": "alice"})
    assert entry is not None


def test_numbers_round_like_the_dashboard():
    assert report._f(0.625) == "0.63" and report._f(0.375) == "0.38"       # ties go up, as JavaScript toFixed does
    assert report._f(1.005) == "1.00"                                       # 1.005 is a little below 1.005 in binary, like in JavaScript
    assert report._f(19.25, 1) == "19.3" and report._f(99.6, 0) == "100" and report._f(None) == "-"
    assert "0.63" in report.render({"at": 1794033000.0, "sessions": 1, "flagged": 0, "threshold": 1.0,
                                    "metrics": {"test": {"risk_engine": {"f1": .5}, "iforest": {"recall": 0.625}}}}, [], NOW)
