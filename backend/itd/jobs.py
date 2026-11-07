"""Run requests: the dashboard asks for a batch run, a worker (engine account) performs it.
Write authorization is kept: the API only INSERTS a request (status 'requested') and reads its status.
The worker (itd/worker.py) is the only writer of progress, so it can use the engine database account.
Statuses: requested -> running -> done | failed.  One run at a time."""
import contextlib
import io
import os
import re
import sys
import time
from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument

from . import config

NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")     # a folder NAME under the data root, never a path
ACTIVE = ["requested", "running"]
LOG_CHARS = 1500
MESSAGE_CHARS = 500


def dataset_path(name):
    """Folder of a named dataset under config.DATA_ROOT. Raises ValueError (bad name) or FileNotFoundError."""
    if not isinstance(name, str) or not NAME.match(name):
        raise ValueError("Invalid dataset name")
    path = os.path.join(config.DATA_ROOT, name)
    if not os.path.isfile(os.path.join(path, "logon.csv")):
        raise FileNotFoundError(f"Dataset '{name}' not found")
    return path


def list_datasets():
    root = config.DATA_ROOT
    if not os.path.isdir(root):
        return []
    return sorted(n for n in os.listdir(root) if NAME.match(n) and os.path.isfile(os.path.join(root, n, "logon.csv")))


# ---- API side (insert and read only) ---------------------------------------------------------------------
def request_run(db, username, dataset, retrain):
    """Insert a run request. Raises ValueError/FileNotFoundError (bad dataset) or RuntimeError (one is already active).
    The active check is best effort: two requests at the same instant may both queue, and the worker runs them one by one."""
    dataset_path(dataset)
    if db.run_requests.find_one({"status": {"$in": ACTIVE}}):
        raise RuntimeError("A run is already waiting or in progress")
    doc = {"_id": ObjectId(), "status": "requested", "dataset": dataset, "retrain": bool(retrain),
           "requested_by": username, "requested_at": time.time()}
    db.run_requests.insert_one(doc)
    return doc


def latest_request(db):
    return db.run_requests.find_one(sort=[("requested_at", -1)])


def _iso(t):
    return datetime.fromtimestamp(t, timezone.utc).isoformat() if t else None


def public(doc, admin=False):
    """What the API shows. The log text (it can name folders) is for the admin only."""
    out = {"id": str(doc["_id"]), "status": doc["status"], "dataset": doc["dataset"], "retrain": doc["retrain"],
           "requested_by": doc["requested_by"], "requested_at": _iso(doc["requested_at"]),
           "started_at": _iso(doc.get("started_at")), "finished_at": _iso(doc.get("finished_at")),
           "message": doc.get("message")}
    if admin:
        out["log"] = doc.get("log_tail")
    return out


# ---- worker side (engine account) ------------------------------------------------------------------------
def recover_stale(db):
    """Only one worker runs, so a request still 'running' when it starts belongs to a worker that stopped."""
    return db.run_requests.update_many(
        {"status": "running"},
        {"$set": {"status": "failed", "finished_at": time.time(), "message": "The worker stopped before this run finished"}}
    ).modified_count


def claim_next(db):
    """Atomically take the oldest waiting request and mark it running. None if nothing waits."""
    return db.run_requests.find_one_and_update(
        {"status": "requested"}, {"$set": {"status": "running", "started_at": time.time()}},
        sort=[("requested_at", 1)], return_document=ReturnDocument.AFTER)


class _Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)
        return len(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def process(db, doc, runner):
    """Run one claimed request with runner(path, retrain) and record how it ended. Never raises."""
    buf = io.StringIO()
    status, message, run_id = "done", None, None
    try:
        with contextlib.redirect_stdout(_Tee(sys.stdout, buf)):
            info = runner(dataset_path(doc["dataset"]), doc["retrain"])
        run_id = info.get("run_id") if isinstance(info, dict) else None
    except SystemExit as e:                                  # the engine stops this way on bad input
        status, message = "failed", str(e.code) if isinstance(e.code, str) else "The run stopped before it finished"
    except Exception as e:
        status, message = "failed", f"{type(e).__name__}: {e}"
    fields = {"status": status, "finished_at": time.time(), "log_tail": buf.getvalue()[-LOG_CHARS:]}
    if message:
        fields["message"] = message[:MESSAGE_CHARS]
    if isinstance(run_id, ObjectId):
        fields["run_id"] = run_id
    db.run_requests.update_one({"_id": doc["_id"]}, {"$set": fields})
    return status
