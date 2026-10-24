# REST API (FastAPI)

Base URL `http://127.0.0.1:8000` (or `https://...:8443` with TLS). Interactive docs: `/docs`.
Every endpoint except login needs the header `Authorization: Bearer <token>`.

| Method and path | What it does | Success | Errors |
|---|---|---|---|
| `POST /api/login` | checks the password, returns a token that expires in 30 minutes | 200 `{token, username, expires_minutes}` | 401 wrong login, 422 invalid input, 429 too many failures |
| `GET /api/sessions?limit=50&offset=0` | flagged sessions, highest risk first | 200 `{threshold, total, scored, high, sessions[]}` | 401 no/expired token, 403 role not allowed |
| `GET /api/sessions/{session_id}` | score, model scores, top 3 SHAP behaviors, top 3 baseline differences, evidence ids | 200 | 401, 403, 404 not found, 422 bad id format |
| `GET /api/users/{user_id}?limit=500` | one user's sessions over time (oldest first), summary counts, and their normal behavior (10 baseline metrics with mean and standard deviation) | 200 `{user, threshold, summary, baseline[], sessions[]}` | 401, 403, 404 unknown user, 422 bad id format |
| `GET /api/run/latest` | when the batch engine last ran, run time per step, flag threshold, model weights, test results (precision, recall, F1, PR-AUC) | 200 | 401, 403, 404 no run yet |
| `POST /api/sessions/{session_id}/chat` body `{"question": "..."}` | assistant answer plus the evidence ids it used | 200 `{answer, fields_used, evidence, mode}` | 401, 403, 404, 422 (question empty or over 300 characters) |

## Security on every request
HTTPS (when enabled), token check, analyst role check, strict input validation, and an entry in the access log
(logins, sessions viewed, users viewed, assistant questions). The API's only database write is the access log.

## Try it
```powershell
python scripts\demo_api.py --user alice --password "ChooseAStrongOne1!"
```
