# AGENTS.md: Insider Threat Detection System (prototype)

Guide for AI coding agents and new team members. Facts here were read from the code and documents on 31 October 2026 (main at commit 86fdfc5, plus the Week 3 work on branch `november-1-tasks-fahim`). If code and this file disagree, the code wins; fix this file.

## 1. What this project is
- University capstone: ITE499A Capstone Project A, Abu Dhabi University, Group 7 (Ayyub Ishnazarov, Muhammad Fahim Zakkeer, Nawaf Khaled Hussein), supervisor Dr. Deepa Suresh. Term Fall 2026-2027.
- A batch research **prototype**, not a production app. Goal: score user work sessions (one user, one PC, logon to logoff) from 0 to 100 using CERT-layout logs, explain each flag, and show flagged sessions to a security analyst.
- A flag is a lead for a human, never proof of wrongdoing. Keep this wording in any UI or text.
- Data in use: generated CERT-layout data (`backend/scripts/generate_synthetic_cert.py`). Original CERT r4.2 and SPEDIA have not been run. Never quote synthetic results as research findings.
- Out of scope: real-time scoring, peer-group comparison, saving analyst decisions (the API may only write the access log), a user-administration screen, production hosting.

## 2. Repository map
| Path | What it is |
|---|---|
| `backend/itd/` | Python package: detection engine, API, security, assistant, SPEDIA tools |
| `backend/scripts/` | operator scripts: data generator, accounts, setup and connection checks, TLS cert, backup, demos |
| `backend/tests/` | pytest suite (in-memory database, no MongoDB needed) |
| `frontend/` | React 18 + Vite dashboard (`src/pages`, `src/components`, `api.js`, `router.js`, `format.js`) |
| `docs/` | CSV layout, API, database, requirements, architecture, security, demo script, weekly plans, Week 3 methodology and use cases |
| `mongo-init/init-users.js` | creates the restricted `itd_engine` and `itd_api` MongoDB users (secure compose only) |
| `docker-compose.yml`, `docker-compose.secure.yml` | MongoDB 7 (plain, or with authentication and separate accounts) |
| `start_all.ps1` | Windows: starts database, API and dashboard |
| `.env.example` | environment variables (set in the shell; no dotenv loader) |
| `mongo-data/`, `backend/data/`, `backend/reports/` | git-ignored: database volume, generated data, engine output |

## 3. Commands
Backend (Python venv at `backend/.venv`; on Windows use `.venv\Scripts\Activate.ps1`):
```
cd backend
pip install -r requirements.txt
python scripts/check_setup.py                              # environment check
python scripts/generate_synthetic_cert.py data/cert_synthetic   # defaults: 120 users, 90 days, 12 insiders, seed 7
python -m itd.engine --data data/cert_synthetic --retrain       # batch run; prints precision/recall/F1/PR-AUC
python -m scripts.create_analyst alice "ChooseAStrongOne1!" analyst
python -m itd.serve                                        # API on http://127.0.0.1:8000 (docs at /docs); HTTPS on 8443 if certs/ exists
pytest -q                                                  # 32 pass, 1 skipped
ITD_TEST_MONGO=mongodb://127.0.0.1:27017 pytest -q         # 33 pass: adds the real-MongoDB schema test (uses its own temporary database)
```
Frontend: `cd frontend && npm install && npm run dev` (http://localhost:5173, proxies `/api` to port 8000) and `npm run build` (must pass; 40 modules).
Database: `docker compose up -d`. On this laptop the container is named `insider-threat-detection-mongo-1` (older docs say `itd-mongo-1`).
Database admin: `python -m itd.schema apply|check`, `python -m scripts.analysts list|add|role|password|delete`, `python scripts/backup_db.py [--restore <dir>]`.
Checks and demos: `python scripts/check_connection.py --user alice --password ...` (needs API and dashboard running), `scripts/demo_api.py`, `scripts/demo_db.py`, `scripts/demo_schema.py`.
SPEDIA: `python -m itd.spedia --inspect <csv>`, `--csv ... --map ... --out ...`, then `python -m itd.cross_eval --train <cert dir> --test <converted dir>`.

## 4. How it works (data flow and connections)
```
CERT-layout CSV files
  -> ingest.py + aggregate.py   read in 500,000-row chunks, count events per session, optional HMAC pseudonyms
  -> sessionize.py              Logon opens, Logoff closes; missing logoff ends at next Logon or 12 h
  -> features.py + baselines.py 28 session + 10 deviation + 1 recency = 39 features; per-user running mean/std (Welford), trusted after 5 sessions, z capped at 10
  -> models.py                  LogisticRegression, XGBoost, IsolationForest; time split 70/15/15
  -> risk.py                    weights = validation F1 share; score 0-100; threshold = best validation F1
  -> explain.py                 SHAP (XGBoost only) top 3 + top 3 baseline deviations, in plain words
  -> engine.py                  writes results, user_baselines, trained_models (+GridFS), runs to MongoDB
MongoDB <- api.py (FastAPI) <- security.py (bcrypt, JWT, roles, throttling, access log)
                            <- assistant.py (evidence only; hosted LLM or local template)
Browser (React) -> Vite proxy /api -> FastAPI
```
- Only the engine writes results, baselines, models and runs. The API reads them and writes only `access_log`. `engine.run` deletes and replaces `results` and `user_baselines` on every run; `--retrain` also deletes saved models.
- Models are saved to GridFS with SHA-256 hashes; `load_models` raises `ModelIntegrityError` if a hash does not match.
- Assistant: builds evidence ids R, S1 to S3, B1 to B3 from one stored session (no user or PC names). If `LLM_API_KEY` is set it calls the Anthropic Messages API (`LLM_URL`, model `LLM_MODEL`, default `claude-sonnet-5-5`) and keeps only evidence ids that exist; on any failure, or with no key, it answers from a local template (`mode: "template"`).
- `db.py`: `MONGO_URI=mock` switches to mongomock for tests. `get_db("engine")` and `get_db("api")` can use different MongoDB accounts (`MONGO_URI_ENGINE`, `MONGO_URI_API`).
- Frontend does no calculation. Hash routes: `#/`, `#/session/S0000123`, `#/user/U0027`. `api.js` keeps the token in `sessionStorage` and dispatches `auth-expired` on a 401.

## 5. Database (MongoDB, database `insider_threat`)
Six collections plus GridFS: `results` (one scored session, `_id` = session id like `S0000123`), `user_baselines`, `trained_models` (`_id` = `current`), `runs`, `analyst_accounts` (roles `analyst` or `admin`), `access_log` (actions: login_ok, login_failed, session_viewed, user_viewed, assistant_question, demo_entry). Rules and indexes live in `backend/itd/schema.py`; they are only enforced by MongoDB after `python -m itd.schema apply` (applied on this laptop's main database on 31 October 2026). Details: `docs/DATABASE.md`.

## 6. API (`docs/API.md`)
`GET /api/health` (no login), `POST /api/login`, `GET /api/sessions`, `GET /api/sessions/{id}`, `POST /api/sessions/{id}/chat`, `GET /api/users/{id}`, `GET /api/run/latest`. All but health and login need `Authorization: Bearer <token>`. Analyst and admin have the same API rights; unknown roles get 403. Ids are validated by pattern (`S` + digits, user ids up to 64 safe characters); login bodies reject extra fields.

## 7. Configuration (`backend/itd/config.py`, environment variables)
`MONGO_URI`, `MONGO_URI_ENGINE`, `MONGO_URI_API`, `DB_NAME`, `JWT_SECRET`, `JWT_MINUTES` (30), `REQUIRE_HTTPS` (0), `LOGIN_MAX_FAILURES` (5), `LOGIN_WINDOW_SECONDS` (900), `LLM_API_KEY`, `LLM_MODEL`, `LLM_URL`, `CORS_ORIGINS`, `PSEUDONYMIZE`, `PSEUDONYM_KEY`. Development defaults to change before any real use: built-in `JWT_SECRET`, HTTP instead of HTTPS, plain (no-login) MongoDB.

## 8. Tests (`backend/tests/test_pipeline.py`)
- One module-scoped `client` fixture generates data (60 users, 80 days, 8 insiders), runs the engine with `retrain=True` into the mock database, creates user `alice` (password `pw123`), and returns a FastAPI `TestClient`.
- `test_login_throttle_last` must stay last: failed logins lock the test client's address.
- `pytest.ini` sets `--basetemp=.pytest_tmp` and disables the cache provider.

## 9. Known gaps between the proposal and the code (open as of 31 October 2026)
1. No Platt calibration (`risk.py`); the proposal promises it. Isolation Forest is only min-max scaled.
2. Hosted assistant answers are not checked statement by statement (`assistant.py`, `_call_llm`); the proposal promises this. Only unknown evidence ids are dropped.
3. Per-model thresholds in the reported test metrics are picked on test labels (`risk.evaluate_model`, called from `engine.py`). The combined score uses a validation threshold (correct).
4. `n_distinct_pcs_day` and `n_sessions_day` use the whole day (`features.py`), so later sessions leak into earlier ones.
5. Re-running the engine without `--retrain` loads saved baselines and replays the data onto them (`engine.py`); last-session time is not saved, so recency breaks across runs.
6. The user page baseline is the end-of-batch state, not the state used to score older sessions.
7. `metrics` key `pr_auc` is average precision (`sklearn.average_precision_score`).
8. Not yet run: real CERT r4.2 or SPEDIA (the SPEDIA adapter was tested on a stand-in file only), the secure compose start-up script, HTTPS in a browser, the hosted model with a real key. No frontend tests. Memory use at full CERT size is unmeasured.
9. Sign out only removes the browser token; there is no server-side revocation.
Fixed in Week 3: offline answer said "above the flag threshold" for sessions under the threshold; heading now says "What drove the XGBoost score".

## 10. Course context (not visible in the code)
- The supervisor gives weekly task tables; the group splits the work. Prototype and research-and-methodology are handled by Fahim and one teammate; review-paper work by the third member.
- Week 1 and 2 prototype work is recorded in `docs/WEEK2_PLAN.md`, `docs/DEMO.md`, `docs/REQUIREMENTS.md`.
- Week 3 (submission 1 November 2026) is a 7-day table with two tracks per day (research and methodology, prototype development). Fahim owns Days 1, 2 and 7. Output: `docs/METHODOLOGY.md`, `docs/USE_CASES.md`, `docs/WEEK3_PLAN.md`, merged into the team's Word document `Group7_Research_and_Methodology.docx` (repo root, untracked) as sections 12 (use cases, roles, access control), 13 (workflow and processing stages), 21 (prototype status, issues, test record) and 22 (review against objectives and research gaps). Later sections were renumbered (old 12 to 19 became 14 to 20 and 23) and a few statements that went stale after revision 86fdfc5 were updated.
- A separate weekly literature task (understand the topic and collect papers) has no prototype work.
- Related Word documents (outside the repo, in the owner's Downloads folder): the Initial Project Proposal (Round 3), the Week 2 Literature Search and Research Foundation (20 studies S1-S20, search strings, research gap) and Research and Methodology (research questions RQ1-RQ5, evaluation plan, repository audit). The methodology document is the most careful about claims; prefer its wording.
- Known document inconsistencies: two different sets of literature search strings; proposal says five collections and three API functions (code has six and seven); "no study combines..." wording in the proposal is stronger than the evidence.

## 11. Working rules for agents
- Keep changes small and in the existing style (short functions, comments only for the why). Read a file before editing it.
- Do not commit or push unless asked. Weekly task work is done on a local branch; the remote `origin` is `NawafAz-ui/insider-threat-detection`.
- Run `pytest -q` in `backend` and `npm run build` in `frontend` after changes. Update the test count in `README.md`, `docs/REQUIREMENTS.md` and `docs/DEMO.md` if it changes.
- Documents for the supervisor use short everyday English, no emojis, no em-dashes, and state what was not checked. Never write "Day 1", "Day 7" or similar in them; use the official task names or section headings.
- Never claim a result on real CERT or SPEDIA data; none exists yet.
- Do not write secrets into the repo. Keep the API's only database write to `access_log`.
