"""Security Controls: bcrypt passwords, signed expiring JWT, read-only analyst role, access log."""
import re
import time
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import config
from .db import get_db

bearer = HTTPBearer(auto_error=False)
SESSION_ID = re.compile(r"^S[0-9]{1,12}$")      # strict format: cannot carry a Mongo operator
USER_ID = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def check_password(pw: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except ValueError:
        return False


def make_token(username: str, role: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=config.JWT_MINUTES)
    return jwt.encode({"sub": username, "role": role, "exp": exp}, config.JWT_SECRET, algorithm="HS256")


def current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> dict:
    """Authentication: every endpoint except login requires a valid, unexpired token."""
    if creds is None:
        raise HTTPException(401, "Login required")
    try:
        data = jwt.decode(creds.credentials, config.JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired token")
    return {"username": data["sub"], "role": data.get("role")}


def require_analyst(user: dict = Depends(current_user)) -> dict:
    """Authorization: analysts have read-only access."""
    if user["role"] not in ("analyst", "admin"):
        raise HTTPException(403, "Not allowed")
    return user


def valid_session_id(session_id: str) -> str:
    if not SESSION_ID.match(session_id):
        raise HTTPException(422, "Invalid session id")
    return session_id


def valid_user_id(user_id: str) -> str:
    if not USER_ID.match(user_id):
        raise HTTPException(422, "Invalid user id")
    return user_id


def log_access(request: Request, username: str, action: str, **extra):
    """Access logging: login, session viewed, assistant question (the only write the API makes)."""
    get_db("api").access_log.insert_one({"at": time.time(), "user": username, "action": action,
                                    "ip": request.client.host if request.client else None, **extra})


def check_login_throttle(request: Request, username: str):
    """Too many failed logins for this username or address in the window -> 429 (guessed-password risk)."""
    since = time.time() - config.LOGIN_WINDOW_SECONDS
    ip = request.client.host if request.client else None
    log = get_db("api").access_log
    n = max(log.count_documents({"action": "login_failed", "user": username, "at": {"$gt": since}}),
            log.count_documents({"action": "login_failed", "ip": ip, "at": {"$gt": since}}) if ip else 0)
    if n >= config.LOGIN_MAX_FAILURES:
        raise HTTPException(429, "Too many failed logins. Try again later.")
