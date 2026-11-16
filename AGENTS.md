# AGENTS.md: Insider Threat Detection System (prototype)

Guide for AI coding agents and new team members. Facts here were read from the code and documents on 31 October 2026 (main at commit 86fdfc5, plus the Week 3 work on branch `november-1-tasks-fahim`). If code and this file disagree, the code wins; fix this file.

## 1. What this project is
- University capstone: ITE499A Capstone Project A, Abu Dhabi University, Group 7 (Ayyub Ishnazarov, Muhammad Fahim Zakkeer, Nawaf Khaled Hussein), supervisor Dr. Deepa Suresh. Term Fall 2026-2027.
- A batch research **prototype**, not a production app. Goal: score user work sessions (one user, one PC, logon to logoff) from 0 to 100 using CERT-layout logs, explain each flag, and show flagged sessions to a security analyst.
- A flag is a lead for a human, never proof of wrongdoing. Keep this wording in any UI or text.
- Data in use: since 16 November 2026 the prototype runs on SPEDIA (`backend/data/spedia_cert`, the owner's choice for prototype purposes); generated CERT-layout data (`backend/scripts/generate_synthetic_cert.py`) is still used by the tests and experiments. CERT r4.2 is the original dataset of the research and has not been run through the models. Never quote these results as research findings.
- Out of scope: real-time scoring, peer-group comparison, saving analyst decisions (the API may only write the access log), a user-administration screen, production hosting.

## 2. Repository map
| Path | What it is |
|---|---|
| `backend/itd/` | Python package: detection engine, API, security, assistant, SPEDIA tools |
| `backend/scripts/` | operator scripts: data generator, accounts, setup and connection checks, TLS cert, backup, demos |
| `backend/tests/` | pytest suite (in-memory database, no MongoDB needed) |
| `frontend/` | React 18 + Vite dashboard (`src/pages`, `src/components`, `api.js`, `router.js`, `format.js`) |
| `docs/` | CSV layout, API, database, requirements, architecture, security, demo script, weekly plans, Week 3 methodology, use cases, data flow, tools, data rules, evaluation criteria; `docs/figures/` holds the diagrams |
| `word-reports/` | the group's Word reports: the Research and Methodology base (`Research & Methodology - Group 7 - 06.11.2026 Version.docx`, never edited) the previous version (`Research & Methodology Group 7 09.11.2026 Version.docx`) and the current version (`Research & Methodology - Group 7 - 16.11.2026 Version.docx`) |
| `mongo-init/init-users.js` | creates the restricted `itd_engine` and `itd_api` MongoDB users (secure compose only) |
| `docker-compose.yml`, `docker-compose.secure.yml` | MongoDB 7 (plain, or with authentication and separate accounts) |
| `start_all.ps1` | Windows: starts database, API and dashboard |
| `.env.example` | environment variables (set in the shell; no dotenv loader) |
| `mongo-data/`, `backend/data/`, `backend/reports/` | git-ignored: database volume, generated data and the prepared SPEDIA data (`backend/data/spedia/`), stored as .csv.gz, engine output |

## 3. Commands
Backend (Python venv at `backend/.venv`; on Windows use `.venv\Scripts\Activate.ps1`):
```
cd backend
pip install -r requirements.txt
python scripts/check_setup.py                              # environment check
python scripts/generate_synthetic_cert.py data/cert_synthetic   # defaults: 120 users, 90 days, 12 insiders, seed 7
python -m itd.engine --data data/cert_synthetic --retrain       # batch run; prints precision/recall/F1/PR-AUC/Brier
python scripts/run_experiments.py --seeds 5                # matched experiments A to D on generated data (no database)
python -m scripts.create_analyst alice "ChooseAStrongOne1!" analyst
python -m itd.serve                                        # API on http://127.0.0.1:8000 (docs at /docs); HTTPS on 8443 if certs/ exists
pytest -q                                                  # 91 pass, 1 skipped
ITD_TEST_MONGO=mongodb://127.0.0.1:27017 pytest -q         # 92 pass: adds the real-MongoDB schema test (uses its own temporary database)
python scripts/integration_test.py                         # integrated test IT1 to IT9 + IT4b: real MongoDB (scratch db itd_integration, dropped after), API, HTTPS API, worker, dashboard; stops and restarts the MongoDB container in IT7; page load needs Chrome and puppeteer-core on NODE_PATH; 10 of 10 passed on 16 November 2026, report docs/INTEGRATED_TEST_REPORT.pdf (source docs/src/integrated_test_report.html, results copy docs/evidence/integration_results.json)
backend/.venv/bin/python docs/src/demo_screenshots.py     # from the repo root: retakes the data screenshots and 10-demo-api-results.md from a copy of the main db (itd_demo), same NODE_PATH need
```
Frontend: `cd frontend && npm install && npm run dev` (http://localhost:5173, proxies `/api` to port 8000) and `npm run build` (must pass; 42 modules).
Database: `docker compose up -d`. On this laptop the container is named `insider-threat-detection-mongo-1` (older docs say `itd-mongo-1`).
Database admin: `python -m itd.schema apply|check`, `python -m scripts.analysts list|add|role|password|delete`, `python scripts/backup_db.py [--restore <dir>]`.
Checks and demos: `python scripts/check_connection.py --user alice --password ...` (needs API and dashboard running), `scripts/demo_api.py`, `scripts/demo_db.py`, `scripts/demo_schema.py`.
Evaluation (Milestone 5): `python scripts/assistant_eval.py` (30 fixed questions, offline), `python scripts/measure_latency.py --user ... --password ...` (API running), `python scripts/measure_resources.py` (needs psutil and MongoDB, scratch database `itd_perf`). Results are in `docs/evidence/` (Test_Case_Matrix, Preliminary_Evaluation_Results, Limitations_Analysis, Refined_Methodology).
SPEDIA: `python -m itd.spedia --inspect <csv>`, `--csv ... --map ... --out ...`, then `python -m itd.cross_eval --train <cert dir> --test <converted dir>`.
Smaller dataset for the prototype (owner's choice on 15 November 2026: no full-size real data in the prototype): SPEDIA v2 from Zenodo (https://doi.org/10.5281/zenodo.15525713, CC BY 4.0, 45.7 MB, MD5 e01e0baaf3b523a0b493fc9c52af2b1c), source and records in `backend/data/spedia/` (git-ignored), the converted dataset in `backend/data/spedia_cert` (listed by the dashboard run panel): `python -m itd.spedia --csv data/spedia/download/logs_SPEDIA_annotated_en.csv.xz --map spedia_mapping.json --out data/spedia_cert`, `python scripts/prepare_split.py data/spedia_cert data/spedia/prepared` (input check, preprocessing and the split, no database, no models), then `python -m itd.engine --data data/spedia_cert --retrain` (done on 16 November 2026 after a backup to `backend/backups/2026-11-16_1647`: 246 sessions, 111 flagged, threshold 35.2, test F1 0.94; run again the same day after the issue 14 fix, after a backup to `backend/backups/2026-11-16_1707`: threshold 35.5, 111 flagged, test F1 0.94, Logistic Regression 0.83). The converted files in `backend/data/spedia_cert` are tracked in git as sample data (`.gitignore` exception, `SOURCE.md` has the attribution). Report source: `docs/src/make_spedia_report.py`. The checked mapping builds sessions from 30-minute activity gaps because SPEDIA's own login records rarely frame its other events. Report: `docs/DATA_PREPARATION_SPEDIA.pdf`. For an official CERT release later: `python scripts/extract_cert.py <release.tar.bz2> <dataset dir> <reference dir>` keeps only the engine's columns, then `scripts/build_answers.py` with only that release's answer folders. The engine reads `name.csv` or `name.csv.gz` (`ingest.data_file`); the data folders are stored gzip-compressed.

## 4. How it works (data flow and connections)
```
CERT-layout CSV files
  -> ingest.py + aggregate.py   read in 500,000-row chunks, count events per session, optional HMAC pseudonyms
  -> sessionize.py              Logon opens, Logoff closes; missing logoff ends at next Logon or 12 h
  -> features.py + baselines.py 28 session + 10 deviation + 1 recency = 39 features; per-user running mean/std (Welford), trusted after 5 sessions, z capped at 10
  -> models.py                  LogisticRegression, XGBoost, IsolationForest; time split 80/20 (train/test, no validation part); oof_scores = 5-fold out-of-fold scores of the training part
  -> risk.py                    sigmoid (Platt) calibration per model on the out-of-fold training scores; weights = their F1 share; score 0-100; threshold = best out-of-fold F1 (keys still named val_*)
  -> explain.py                 SHAP (XGBoost only) top 3 + top 3 baseline deviations, in plain words
  -> engine.py                  writes results, user_baselines, trained_models (+GridFS), runs to MongoDB
MongoDB <- api.py (FastAPI) <- security.py (bcrypt, JWT, roles, throttling, access log)
                            <- assistant.py (evidence only; hosted LLM or local template)
Browser (React) -> Vite proxy /api -> FastAPI
```
- Only the engine writes results, baselines, models and runs. The API reads them and writes only `access_log` and `run_requests` (an admin's request for a batch run; the worker, `python -m itd.worker`, picks it up and runs the engine). `engine.run` deletes and replaces `results` and `user_baselines` on every run; `--retrain` also deletes saved models.
- Models are saved to GridFS with SHA-256 hashes; `load_models` raises `ModelIntegrityError` if a hash does not match.
- Assistant: builds evidence ids R, S1 to S3, B1 to B3 from one stored session (no user or PC names). A keyword guard (`GUARDS`, `_decline_reason`, merged from Nawaf's branch `docs/milestone-5-evaluation` on 16 November 2026) first refuses questions about guilt, names, other sessions or rule changes, and any question that is neither general nor about a stored reason, before any model call. If `LLM_API_KEY` is set it calls the Anthropic Messages API (`LLM_URL`, model `LLM_MODEL`, default `claude-sonnet-5-5`) and keeps only statements that cite existing evidence ids and use numbers found in the cited items; on any failure, a reply in the wrong format, or with no key, it answers from a local template (`mode: "template"`).
- `db.py`: `MONGO_URI=mock` switches to mongomock for tests. `get_db("engine")` and `get_db("api")` can use different MongoDB accounts (`MONGO_URI_ENGINE`, `MONGO_URI_API`).
- Frontend does no calculation. Hash routes: `#/`, `#/session/S0000123`, `#/user/U0027`. `api.js` keeps the token in `sessionStorage` and dispatches `auth-expired` on a 401.

## 5. Database (MongoDB, database `insider_threat`)
Seven collections plus GridFS: `results` (one scored session, `_id` = session id like `S0000123`), `user_baselines`, `trained_models` (`_id` = `current`), `runs`, `analyst_accounts` (roles `analyst` or `admin`), `access_log` (actions: login_ok, login_failed, session_viewed, user_viewed, assistant_question, demo_entry, run_requested, report_viewed), `run_requests` (status requested, running, done or failed). Rules and indexes live in `backend/itd/schema.py`; they are only enforced by MongoDB after `python -m itd.schema apply` (applied on this laptop's main database on 31 October 2026). Details: `docs/DATABASE.md`.

## 6. API (`docs/API.md`)
`GET /api/health` (no login), `POST /api/login`, `GET /api/sessions`, `GET /api/sessions/{id}`, `POST /api/sessions/{id}/chat`, `GET /api/users/{id}`, `GET /api/run/latest`, `GET /api/run/status`, `GET /api/run/report` (HTML download), and admin-only `GET /api/run/datasets` and `POST /api/run` (files a run request; 404 unknown dataset, 409 a run is already waiting or running). All but health and login need `Authorization: Bearer <token>`. Analyst and admin have the same read rights; only admin can request a run; unknown roles get 403. Ids are validated by pattern (`S` + digits, user ids up to 64 safe characters); login bodies reject extra fields.

## 7. Configuration (`backend/itd/config.py`, environment variables)
`MONGO_URI`, `MONGO_URI_ENGINE`, `MONGO_URI_API`, `DB_NAME`, `JWT_SECRET`, `JWT_MINUTES` (30), `REQUIRE_HTTPS` (0), `LOGIN_MAX_FAILURES` (5), `LOGIN_WINDOW_SECONDS` (900), `LLM_API_KEY`, `LLM_MODEL`, `LLM_URL`, `CORS_ORIGINS`, `PSEUDONYMIZE`, `PSEUDONYM_KEY`. Development defaults to change before any real use: built-in `JWT_SECRET`, HTTP instead of HTTPS, plain (no-login) MongoDB.

## 8. Tests (`backend/tests/test_pipeline.py`)
- One module-scoped `client` fixture generates data (60 users, 80 days, 8 insiders), runs the engine with `retrain=True` into the mock database, creates user `alice` (password `pw123`), and returns a FastAPI `TestClient`.
- `test_login_throttle_last` must stay last: failed logins lock the test client's address.
- `pytest.ini` sets `--basetemp=.pytest_tmp` and disables the cache provider.

## 9. Known gaps between the proposal and the code (open as of 1 November 2026)
1. Calibration is a two-parameter sigmoid per model, fitted on out-of-fold training scores with few malicious sessions per fold, so the curve can be noisy (`risk.py`, `CALIBRATION_C`). Isolation Forest is still min-max scaled before it is calibrated.
2. Hosted assistant statements are checked mechanically (`assistant.check_statements`): each must cite an existing evidence id and every number in it must appear in the cited items. The check cannot judge whether a plausible sentence is a sensible reading. It was tested with fake replies only; the hosted call has never been tried with a real key.
3. The user page baseline is the end-of-batch state, not the state used to score older sessions.
4. `metrics` key `pr_auc` is average precision (`sklearn.average_precision_score`).
5. The main database (`insider_threat`) holds SPEDIA since 16 November 2026 (246 sessions, 111 flagged, threshold 35.5; the generated-data state is in `backend/backups/2026-11-16_1647`). `docs/DEMO.md` (live demo) and `docs/screenshots/` show SPEDIA since 16 November 2026 (screenshots 2, 9 and 12 are data-independent and were not retaken; the terminal screenshots 1 and 13 are real command output rendered as images). SPEDIA computer names are long hashes (some start with `attacker_`, which is the dataset's own host name, not a model input); the dashboard shortens them with the full name on hover.
6. SPEDIA was converted, checked and preprocessed on 15 November 2026 (55,649 events, 246 sessions, 110 malicious; the adapter was fixed for the real file) and run through the models on 16 November 2026. Real CERT r4.2 was downloaded and preprocessed once on 15 November 2026 (32,770,222 events, 470,591 sessions) and then deleted at the owner's request. Not yet run at all: the secure compose start-up script, HTTPS in a browser, the hosted model with a real key. No frontend unit tests; the integrated test loads the sign-in page and the flagged list in headless Chrome, and the screenshots drive every page. Memory use of model training at full CERT size is unmeasured (preprocessing of CERT r4.2 peaked at about 4.0 GB, the whole generated 7,329-session run at about 308 MiB).
7. Sign out only removes the browser token; there is no server-side revocation.
8. Results are replaced on every run (delete, then insert): an interrupted run leaves the results incomplete.
9. `test_sessionization_rules` (`backend/tests/test_pipeline.py:112`) asserts the 12-hour cap since 16 November 2026 (it used to pass with or without it); the 16.11 Word report says so in TC2. No test covers file counts, the saved feature order, or successful-login and session-view log entries either. `docs/EVALUATION_CRITERIA.md` still says the 12-hour cap, file counts and "another session" are tested; the Word document has the corrected wording (checked against the test bodies on 6 November 2026).
Fixed on 16 November 2026: issue 14 (`baselines.add_deviations` adds a session to the user's baseline only after it has ended; 40 of 246 SPEDIA sessions overlap, none in generated data), the API writes the `run_requested` log entry before it stores the request (`jobs.request_run(log=...)`), the worker waits out a database outage (`PyMongoError` around `claim_next`), and the API, list, session page, user page and CSV now include the computer (`pc`). Changed on 16 November 2026 (owner): the split is training and test only (80/20); calibration, weights and thresholds come from 5-fold cross-validation inside the training part (`models.oof_scores`); the reference rules take their threshold from the training part. Fixed in Week 3: offline answer said "above the flag threshold" for sessions under the threshold; heading now says "What drove the XGBoost score"; per-model thresholds are chosen on validation data (also in `cross_eval.py`); `n_distinct_pcs_day` and `n_sessions_day` count only the sessions up to the current one; saved baselines keep the last-session time, and a re-run on the same data rebuilds the baseline instead of counting it twice; calibration added; hosted statements checked.

## 10. Course context (not visible in the code)
- The supervisor gives weekly task tables; the group splits the work. Prototype and research-and-methodology are handled by Fahim and one teammate; review-paper work by the third member.
- Week 1 and 2 prototype work is recorded in `docs/WEEK2_PLAN.md`, `docs/DEMO.md`, `docs/REQUIREMENTS.md`.
- Week 3 (submission 1 November 2026) is a 7-day table with two tracks per day (research and methodology, prototype development). Fahim first owned Days 1, 2 and 7; on 1 November the group decided to do the whole table. Output: `docs/METHODOLOGY.md`, `docs/USE_CASES.md`, `docs/WEEK3_PLAN.md`, `docs/ACTION_PLAN_REMAINING_ROWS.md` and the sources `docs/DATAFLOW.md`, `docs/TOOLS_AND_ALGORITHMS.md`, `docs/DATA_RULES.md`, `docs/EVALUATION_CRITERIA.md` (figures in `docs/figures/`), merged into the team's Word document `Group7_Research_and_Methodology.docx` (repo root at the time; the Word reports are in `word-reports/` since 15 November 2026). On 4 November 2026 that Word document was rewritten shorter and in plainer wording at the owner's request: 13 numbered sections (introduction, research questions, literature and gap, requirements with acceptance status, system design, use cases and roles, workflow, data and preprocessing, features, models and tools, evaluation, explanations, assistant, security and privacy, prototype status and issues, review against objectives and gaps) and References; a 14th section, remaining work and schedule for Capstone B, was removed on 6 November 2026 at the owner's request. On 5 November 2026 it was cut again (20 pages in a preview that ignored page margins, about 24 with margins and about 27 once the five figures were in, then about 22 after the 6 November cut to 10 tables and about 7,400 body words): the pseudocode appendix, the existing-products paragraph, the database, API and security-boundary tables and the threats-to-validity paragraph were removed because no row of the Week 3 table or supervisor feedback point asks for them. An independent review the same day corrected evidence claims that the tests do not support (the 12-hour cap, file counts, the saved feature order), the dashboard being listed as four pages (not five views), FR10 (now Partially Met), the RQ3 reading (XGBoost alone scored higher than the combination) and O3. On 6 November 2026 the text was put into a formal impersonal voice (no "we" or "our", no references to weeks or weekly tasks). The diagrams were first removed on purpose. On 6 November 2026 all five were drawn in formal notation and inserted: Figure 1 a UML component diagram, Figures 2 and 3 Gane-Sarson data-flow diagrams, Figure 4 a UML use-case diagram, Figure 5 a UML activity diagram (all five come from the small scripts in `docs/figures/src/`; Figures 1 and 3 were redrawn simpler the same day because the owner found them confusing, Figure 3 now has four processes); see `docs/FIGURES.md`. The previous long version (sections 1 to 23, Appendices A to D, old figures) is saved as `~/Downloads/Group7_Research_and_Methodology_long_version.docx`; the original team copy is also still in the Downloads folder. The Markdown files in `docs/` still follow the long version's section numbers.
- A separate weekly literature task (understand the topic and collect papers) has no prototype work.
- Related Word documents (outside the repo, in the owner's Downloads folder): the Initial Project Proposal (Round 3), the Week 2 Literature Search and Research Foundation (20 studies S1-S20, search strings, research gap) and Research and Methodology (research questions RQ1-RQ5, evaluation plan, repository audit). The methodology document is the most careful about claims; prefer its wording.
- Known document inconsistencies: two different sets of literature search strings; proposal says five collections and three API functions (code has six and seven); "no study combines..." wording in the proposal is stronger than the evidence.

## 11. Working rules for agents
- Keep changes small and in the existing style (short functions, comments only for the why). Read a file before editing it.
- Do not commit or push unless asked. Weekly task work is done on a local branch; the remote `origin` is `NawafAz-ui/insider-threat-detection`.
- Run `pytest -q` in `backend` and `npm run build` in `frontend` after changes. Update the test count in `README.md`, `docs/REQUIREMENTS.md` and `docs/DEMO.md` if it changes.
- Documents for the supervisor use short everyday English, no emojis, no em-dashes, and state what was not checked. Never write "Day 1", "Day 7" or similar in them; use the official task names or section headings. The Research and Methodology report is a formal report: impersonal voice, no "we" or "our", no references to weeks or weekly tasks.
- Never claim a result on real CERT or SPEDIA data; none exists yet.
- Do not write secrets into the repo. Keep the API's database writes to `access_log` and `run_requests`.
