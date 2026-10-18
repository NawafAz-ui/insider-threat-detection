"""REST API (FastAPI): login, session list, session detail, assistant chat. Run: uvicorn itd.api:app"""
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from . import assistant, config
from .db import get_db
from .security import (check_login_throttle, check_password, log_access, make_token, require_analyst,
                       valid_session_id)

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
