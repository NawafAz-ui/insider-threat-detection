# Week 3 prototype plan: review of the current implementation and remaining core modules

Insider Threat Detection System, Capstone Project A. Prototype track, submission 1 November 2026.
Day 1 (review). Written on 31 October 2026 from the code on branch `main` (commit 86fdfc5) and the Week 2 documents.

## Where the prototype stands
- **Detection engine:** reads CERT-layout CSV logs, builds sessions, 39 features and per-user baselines, trains three models (Logistic Regression, XGBoost, Isolation Forest), combines them into a 0 to 100 risk score, and explains each session with SHAP and baseline differences.
- **REST API:** login, flagged session list, session detail, assistant chat, user history, latest run, health check.
- **Dashboard:** four views (Login, Flagged Sessions, Session Detail with chat, User Page with risk timeline).
- **Database:** MongoDB with six collections, validation rules, indexes and `run_id` links.
- **Security:** bcrypt, expiring token, analyst and admin roles, input checks, throttling, access log, model hash check.
- **Checks:** 27 automated tests passed at the start of Week 3; 32 pass now, plus one that needs a real MongoDB and is skipped by default. The frontend production build passes (40 modules).
- **Data:** generated CERT-layout data only. Original CERT r4.2 and SPEDIA have not been run.

## Issues and remaining core modules
Each row was checked in the code.

| # | Issue | Where | Type | Priority | Suggested day | Status |
|---|---|---|---|---|---|---|
| 1 | No score calibration. The proposal promises Platt scaling; the code combines raw scores and only rescales Isolation Forest | `risk.py` | Missing module | High | Day 4 (algorithm and logic) | Open |
| 2 | Hosted assistant answers are not checked statement by statement; only unknown evidence ids are removed | `assistant.py:111` | Missing module | High | Day 4 | Open |
| 3 | Thresholds for single models are picked on the test labels, so their test numbers are too optimistic. The combined score is correct (validation only) | `risk.py:38-40`, `engine.py:97-98` | Evaluation | High | Day 4 | Open |
| 4 | `n_distinct_pcs_day` and `n_sessions_day` use the whole day, so later sessions leak into earlier ones | `features.py:87-88` | Method | Medium | Day 4 | Open |
| 5 | Re-running the engine without `--retrain` loads saved baselines and replays the same data on top; last-session time is not saved, so recency breaks between runs | `engine.py:72-73`, `baselines.py` | Method | Medium | Day 5 (connect to database) | Open |
| 6 | Offline answer always says the score is "above the flag threshold", which is wrong for below-threshold sessions reachable from the user page | `assistant.py:46` | Functional error | Medium | Day 7 | Done: answer says "below" when the session is not flagged; test added |
| 7 | Heading "What drove the score" does not say that SHAP explains the XGBoost model only | `SessionDetail.jsx:46` | Accuracy of wording | Low | Day 7 (one line) | Done: heading now reads "What drove the XGBoost score" |
| 8 | Not yet run: original CERT r4.2, SPEDIA, secure MongoDB start-up script, HTTPS in a browser, hosted model with a real key | environment | Verification | Medium | After this week | Open |
| 9 | The dashboard has no automated tests | `frontend/` | Testing | Low | After this week | Open |
| 10 | README said three screens; the code has four | `README.md:18` | Documentation | Low | Day 1 | Done |
| 11 | Some modules have no direct test: risk score, aggregation, SHAP selection. Role and expired-token cases are not tested | `backend/tests/` | Testing | Medium | Day 2 and Day 7 | Done: 5 tests added (unknown role and expired token, below-threshold answer, risk score, aggregation, SHAP selection) |

## Day 7 test record (31 October 2026)
| Check | Result |
|---|---|
| `pytest -q` in `backend` | 32 passed, 1 skipped (real-MongoDB test, no test server configured) |
| `ITD_TEST_MONGO=mongodb://127.0.0.1:27017 pytest -q` | 33 passed, including the real-MongoDB schema test (it uses its own temporary database) |
| `npm run build` in `frontend` | passed, 40 modules |
| `python -m itd.schema apply`, then `check` | Validation rules switched ON for all six collections of the main database. 7,329 results, 120 baselines, 1 account, 37 access-log entries, 2 runs, 1 model record: 0 problems |
| `scripts/demo_schema.py` | valid documents accepted; unknown role, plain-text password, unknown log action, over-long question and a role update to "root" all rejected by MongoDB (code 121); demo documents removed |
| `scripts/demo_db.py` | every collection shown; create, read, update, delete on a temporary account worked; temporary data removed |
| `scripts/check_connection.py` | every line OK: database, results (7,329 sessions, 66 flagged), accounts, models, API, health, login, session list, dashboard proxy |
| `scripts/demo_api.py` | all 13 calls returned the expected status (401, 401, 422, 200, 200, 200, 200, 200, 200, 422, 422, 404, 422) |
| Live check of issue 6 | a session scored 5 (threshold 19.5) now gets "which is below the flag threshold" from the offline assistant |

Not planned for the prototype: peer-group comparison, real-time scoring, saving analyst decisions, a user-administration screen.

## Day plan for this submission (days owned by Fahim)

| Day | Research and methodology | Prototype development |
|---|---|---|
| 1 | `docs/METHODOLOGY.md`: approach, workflow, processing stages | This file: review and issue list |
| 2 | `docs/USE_CASES.md`: use-case diagram and descriptions | Roles and access matrix; tests for unknown role (403) and expired token (401) |
| 7 | Review of the methodology against objectives and research gaps (`docs/METHODOLOGY.md`, section 6) | Run all tests and the build; fix issue 6 and 7; add module tests for issue 11 |

Days 3 to 6 are owned by teammates. The issues marked Day 4, Day 5 are suggestions for them and need their agreement.
