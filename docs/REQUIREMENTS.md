# System requirements specification

Insider Threat Detection System (prototype). Requirements follow the approved proposal; items marked *Week 2* were added
while improving the prototype. Status reflects what has been run and tested, not what is planned.

## Functional requirements

| ID | The system shall | Priority | Status | Where / how checked |
|---|---|---|---|---|
| FR-1 | read logon, device, email, file and web logs from CSV files in the documented CERT layout | Must | Done on sample data; real CERT files not yet run | `itd/ingest.py`, `docs/CSV_LAYOUT.md` |
| FR-2 | group events into sessions (logon to logoff per user and PC; a missing logoff ends the session at the next logon or after 12 hours) | Must | Done | `itd/sessionize.py`, `test_sessionization_rules` |
| FR-3 | build 39 features per session (28 session, 10 deviation, 1 recency) | Must | Done | `itd/features.py`, `test_feature_count` |
| FR-4 | keep a baseline per user and compare each session with that user's earlier sessions only | Must | Done | `itd/baselines.py`, `test_baseline_uses_only_past_sessions` |
| FR-5 | score sessions with three models (Logistic Regression, XGBoost, Isolation Forest), trained once, saved, then loaded for scoring | Must | Done | `itd/models.py`, `itd/engine.py` |
| FR-6 | combine the model scores into a 0 to 100 risk score and flag sessions at or above a threshold chosen on validation data | Must | Done | `itd/risk.py` |
| FR-7 | explain each session with the top 3 SHAP behaviors and the top 3 differences from the user's normal, in plain words | Must | Done | `itd/explain.py`, `test_list_sorted_and_detail` |
| FR-8 | let an analyst ask questions about one session; answers use only the stored evidence, name the evidence used, and cannot change a score | Must | Done offline; hosted language-model call not tested with a real key | `itd/assistant.py`, assistant tests |
| FR-9 | require analysts to sign in and give them a time-limited token | Must | Done | `itd/security.py`, `test_login_and_auth` |
| FR-10 | provide a dashboard with login, a flagged-session list (user, date, score) and a session page (score, explanation, chat) | Must | Done | `frontend/src/pages/` |
| FR-11 | show one user's sessions over time and what is normal for that user (*Week 2*) | Must | Done | `GET /api/users/{id}`, `UserPage.jsx`, `test_user_history_endpoint` |
| FR-12 | show when the batch engine last ran and its test results (*Week 2*) | Should | Done | `GET /api/run/latest`, `test_latest_run_endpoint` |
| FR-13 | record every login, session view, user view and assistant question in an access log | Must | Done | `log_access`, `test_chat_names_fields_and_is_logged` |
| FR-14 | report precision, recall, F1 and PR-AUC on a held-out test set | Must | Done | engine output, `reports/metrics.json` |
| FR-15 | run an exploratory cross-dataset test on SPEDIA using only shared features | Should | Code done, tested on a stand-in file; real SPEDIA columns not yet mapped | `itd/spedia.py`, `itd/cross_eval.py` |

## Non-functional requirements

| ID | Requirement | Status | Evidence |
|---|---|---|---|
| NFR-1 | Log layout is documented and based on CERT | Done | `docs/CSV_LAYOUT.md` |
| NFR-2 | The full CERT r4.2 data can be processed in one batch run and the run time is recorded | Run time and per-step times are recorded; ingestion reads in chunks. **The full dataset has not been run yet** | `itd/ingest.py`, `runs` collection |
| NFR-3 | Dashboard pages load in under two seconds | The session list answers in under two seconds on the sample data (tested); full page timing not measured | `test_list_is_fast` |
| NFR-4 | Explanations are readable by a non-expert | Plain-words text and evidence tags; no user study done | dashboard, `test_offline_answer_is_short_and_focused` |
| NFR-5 | The assistant names the evidence fields it used | Done | `test_chat_names_fields_and_is_logged` |
| NFR-6 | Session data is protected from unauthorized access | Token, analyst role, strict input checks, bcrypt, access log, login throttling, optional HTTPS. Separate engine and API database accounts tested on a real MongoDB (the API can only add access-log entries). HTTPS not yet tried in a browser | `docs/SECURITY.md`, security tests |
| NFR-7 | Components are modular (three tiers, separate modules) | Done | project layout |
| NFR-8 | Stored data is consistent and protected from tampering | Database validation rules, model files checked by SHA-256 before use, backup script | `itd/schema.py`, `test_model_tamper_is_detected` |
| NFR-9 | The user sees a clear message when the API or database is down (*Week 2*) | Done | `/api/health`, `test_database_down_gives_a_clear_503` |
| NFR-10 | Privacy: the assistant never receives user or PC names; user ids can be pseudonymized; every flag is labelled as not proof | Done | `test_assistant_gets_no_identifiers`, dashboard notice |
| NFR-11 | The prototype can be set up and checked on a Windows computer | Done | `scripts/check_setup.py`, `scripts/check_connection.py` |
| NFR-12 | The system is covered by automated tests | 27 tests with an in-memory database, plus a test that needs a real MongoDB | `backend/tests/` |

## Out of scope for this prototype
Saving analyst decisions in the system (this would let the API write results, which the proposal does not allow),
real-time scoring of live logs, a user-administration screen, and production hosting.

## Known limits
The sample data is easier than real logs, so its scores are not research findings. A user's baseline is updated after
every session, so a slow, steady insider can raise their own "normal".
