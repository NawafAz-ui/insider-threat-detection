"""REST API (FastAPI): login, session list, session detail, assistant chat, user history, latest run.
Run: python -m itd.serve"""
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

import math
from datetime import datetime, timezone

from . import assistant, config
from .db import get_db
from .features import BASE_LABELS, BASE_METRICS
from .security import (check_login_throttle, check_password, log_access, make_token, require_analyst,
                       valid_session_id, valid_user_id)

app = FastAPI(title="Insider Threat Detection API", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["GET", "POST"],
                   allow_headers=["Authorization", "Content-Type"])


@app.middleware("http")
async def security_headers(request: Request, call_next):
    proto = request.headers.get("x-forwarded-proto", request.url.scheme)
    if config.REQUIRE_HTTPS and proto != "https":              # HTTPS/TLS control
        return JSONResponse({"detail": "HTTPS required"}, status_code=426)
    resp = await call_next(request)
    resp.headers["Strict-Transport-Security"] = "max-age=31536000"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "no-store"
    return resp


class LoginIn(BaseModel):          # strict types: a dict like {"$ne": ""} is rejected
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=1, max_length=128)


class ChatIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=config.MAX_QUESTION_CHARS)


@app.post("/api/login")
def login(body: LoginIn, request: Request):
    check_login_throttle(request, body.username)
    acc = get_db("api").analyst_accounts.find_one({"_id": body.username})
    ok = bool(acc) and check_password(body.password, acc["password_hash"])
    log_access(request, body.username, "login_ok" if ok else "login_failed")
    if not ok:
        raise HTTPException(401, "Wrong username or password")
    return {"token": make_token(acc["_id"], acc["role"]), "username": acc["_id"], "expires_minutes": config.JWT_MINUTES}


@app.get("/api/sessions")
def session_list(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0, le=100000),
                 user: dict = Depends(require_analyst)):
    """Flagged sessions (risk score at or above the threshold), highest risk first."""
    db = get_db("api")
    cur = db.results.find({"flagged": True}, {"top_shap": 0, "baseline_deviations": 0}).sort("risk_score", -1).skip(offset).limit(limit)
    run = db.runs.find_one(sort=[("at", -1)]) or {}
    return {"threshold": round(run.get("threshold", 0.0), 1), "total": db.results.count_documents({"flagged": True}),
            "scored": run.get("sessions", 0), "high": db.results.count_documents({"flagged": True, "risk_score": {"$gte": 80}}),
            "sessions": [{"session_id": d["session_id"], "user": d["user"], "start": d["start"].isoformat(),
                          "end": d["end"].isoformat(), "risk_score": d["risk_score"]} for d in cur]}


def _get_doc(session_id: str):
    doc = get_db("api").results.find_one({"_id": valid_session_id(session_id)})
    if not doc:
        raise HTTPException(404, "Session not found")
    return doc


@app.get("/api/sessions/{session_id}")
def session_detail(session_id: str, request: Request, user: dict = Depends(require_analyst)):
    d = _get_doc(session_id)
    log_access(request, user["username"], "session_viewed", session_id=session_id)
    return {"session_id": d["session_id"], "user": d["user"], "start": d["start"].isoformat(), "end": d["end"].isoformat(),
            "risk_score": d["risk_score"], "flagged": d["flagged"], "model_scores": d["model_scores"],
            "top_shap": d["top_shap"], "baseline_deviations": d["baseline_deviations"],
            "threshold": round((get_db("api").runs.find_one(sort=[("at", -1)]) or {}).get("threshold", 0.0), 1),
            "evidence": assistant.build_evidence(d)}


@app.post("/api/sessions/{session_id}/chat")
def chat(session_id: str, body: ChatIn, request: Request, user: dict = Depends(require_analyst)):
    d = _get_doc(session_id)
    log_access(request, user["username"], "assistant_question", session_id=session_id, question=body.question)
    res = assistant.answer(d, body.question)
    res.setdefault("evidence", assistant.build_evidence(d))
    return res


@app.get("/api/users/{user_id}")
def user_history(user_id: str, request: Request, limit: int = Query(500, ge=1, le=2000),
                 user: dict = Depends(require_analyst)):
    """One user's sessions over time plus their normal behavior (the baseline). Read-only."""
    uid = valid_user_id(user_id)
    db = get_db("api")
    total = db.results.count_documents({"user": uid})
    if not total:
        raise HTTPException(404, "User not found")
    cur = db.results.find({"user": uid}, {"session_id": 1, "start": 1, "end": 1, "risk_score": 1, "flagged": 1}) \
        .sort("start", -1).limit(limit)
    sessions = [{"session_id": d["session_id"], "start": d["start"].isoformat(), "end": d["end"].isoformat(),
                 "risk_score": d["risk_score"], "flagged": d["flagged"]} for d in reversed(list(cur))]
    top = db.results.find_one({"user": uid}, {"risk_score": 1}, sort=[("risk_score", -1)])
    base = db.user_baselines.find_one({"_id": uid})
    baseline = []
    if base and base.get("n"):
        n = base["n"]
        for m in BASE_METRICS:
            std = math.sqrt(base["m2"][m] / n) if n > 1 else 0.0
            baseline.append({"metric": m, "label": BASE_LABELS[m], "mean": round(base["mean"][m], 2), "std": round(std, 2)})
    log_access(request, user["username"], "user_viewed", viewed_user=uid)
    run = db.runs.find_one(sort=[("at", -1)]) or {}
    return {"user": uid, "threshold": round(run.get("threshold", 0.0), 1), "summary": {"sessions": total, "flagged": db.results.count_documents({"user": uid, "flagged": True}),
                                     "highest_risk": top["risk_score"], "shown": len(sessions)},
            "baseline": baseline, "sessions": sessions}


@app.get("/api/run/latest")
def latest_run(user: dict = Depends(require_analyst)):
    """When the batch engine last ran, how long it took, the flag threshold, model weights and test results."""
    run = get_db("api").runs.find_one(sort=[("at", -1)])
    if not run:
        raise HTTPException(404, "No batch run recorded yet. Run the detection engine first.")
    return {"at": datetime.fromtimestamp(run["at"], timezone.utc).isoformat(), "seconds": run["seconds"],
            "step_seconds": run.get("step_seconds", {}), "sessions": run["sessions"], "flagged": run["flagged"],
            "threshold": round(run["threshold"], 1), "weights": run["weights"], "metrics": run.get("metrics")}
