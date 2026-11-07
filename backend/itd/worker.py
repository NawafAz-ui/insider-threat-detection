"""Run worker. Performs the batch runs that the dashboard requests. Start it next to the API:
    python -m itd.worker              keep running, check for requests every 3 seconds
    python -m itd.worker --once       handle the waiting requests, then stop
Uses the engine database account (MONGO_URI_ENGINE), so the API account never needs write rights to results."""
import argparse
import time

from . import jobs
from .db import get_db


def serve(poll=3.0, once=False, runner=None):
    if runner is None:
        from . import engine                                    # heavy imports only when a real run is needed
        runner = lambda path, retrain: engine.run(path, retrain=retrain)
    db = get_db("engine")
    stale = jobs.recover_stale(db)
    if stale:
        print(f"Marked {stale} unfinished request(s) from an earlier worker as failed.")
    print(f"Worker ready (data root: {jobs.config.DATA_ROOT}). Waiting for run requests ...")
    while True:
        doc = jobs.claim_next(db)
        if doc:
            print(f"Run requested by {doc['requested_by']}: dataset '{doc['dataset']}', retrain={doc['retrain']}")
            print("Finished:", jobs.process(db, doc, runner))
        elif once:
            return
        else:
            time.sleep(poll)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--poll", type=float, default=3.0)
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args()
    try:
        serve(a.poll, a.once)
    except KeyboardInterrupt:
        print("Worker stopped.")
