# Action plan for the remaining rows 3 to 6 of the Week 3 table

Internal working plan, not for the supervisor. Rows 1, 2 and 7 are done (Sections 12, 13, 21 and 22 of the Word file). This plan covers rows 3 to 6, both columns. It was written on 1 November 2026 from the code on branch `november-1-tasks-fahim`. Nothing here is started. No commit or push.

## 1. Order of work and why
1. **Prototype first, then the matching text.** The code changes alter scores, metrics and test counts. The Word text must describe the finished code, so it is written after each code step.
2. **Row 3, 4, 5, 6 in that order.** Each row builds on the one before: calibration (3) changes the stored model data, logic fixes (4) change features, the database link (5) stores the result, the dashboard (6) shows it.
3. **Gate after every row:** `pytest -q` in `backend`, `npm run build` in `frontend`. At the end: the same tests with a real MongoDB (`ITD_TEST_MONGO=...`), `check_connection.py`, and the demo scripts.

## 2. Prototype column

| Row | Table task | What exists | What to do | Files | Check |
|---|---|---|---|---|---|
| 3 | Develop the main functional module | The detection engine runs end to end. The core module the proposal promises and the code lacks is score calibration (issue 1). | Add a two-parameter sigmoid per model, fitted on validation scores only. Combine the calibrated scores with the same F1 weights. Equal weights if every F1 is zero. Save the calibrators with the models. Report the Brier score next to raw. | `risk.py`, `engine.py`, `models.py` (save and load) | New tests: calibrated scores stay in 0 to 1, weights add to 1, fallback works, no test labels used. |
| 4 | Implement the selected algorithm, business logic or processing workflow | Three models and the risk rule work. Three logic faults are open. | (a) Issue 3: pick each single model's threshold on validation data and only apply it to the test set. (b) Issue 4: make `n_distinct_pcs_day` and `n_sessions_day` count only sessions up to the current one. (c) Issue 2: the hosted assistant returns statements with evidence ids; code drops a statement that cites no real id or states a number that is not in the cited evidence; if nothing is left, show an "unsupported" notice. | `risk.py`, `features.py`, `assistant.py` | Tests: a later session never changes an earlier value; threshold on test labels is never used; fake hosted replies (good, invented number, missing id) are kept or dropped correctly. The 39-feature count stays. |
| 5 | Connect the core processing module with the backend and the database | Engine writes, API reads, run ids link results to runs. Baseline state does not keep the time of the last session (issue 5). | Save the last-session time with each user baseline. When the engine runs without `--retrain`, use saved baselines only if the new data starts after that time; otherwise rebuild them from the batch, so data is not counted twice. Return the new run fields (calibration, per-model thresholds) from `GET /api/run/latest`. Rules in `schema.py` already allow extra fields, so they only need the new fields written down. | `baselines.py`, `engine.py`, `api.py`, `schema.py`, `docs/DATABASE.md`, `docs/API.md` | Test: run twice on the same data, results equal. Real-MongoDB test. `itd.schema check` shows 0 problems. |
| 6 | Implement result visualization, output display or reporting features | Flagged list, session page, user page with risk timeline, run panel with one line of test results. | (a) Run panel: a small table with precision, recall, F1, average precision and threshold for each model and the combined score, plus the Brier score. (b) A button on the flagged list that downloads the shown sessions as a CSV file, built in the browser from data already loaded, so the API still writes only the access log. Plain markup like `RiskTimeline.jsx`, no new library. | `FlaggedSessions.jsx`, one small component, `format.js` | `npm run build`; screenshots of the two changes. There are no frontend tests; say so. |

Open risks for this column:
- The validation part has few malicious sessions, so a two-parameter sigmoid can be noisy. Section 16 of the Word file already says so. Report it and keep raw scores visible.
- Calibration and the feature change alter every score. The main database must be rebuilt with `--retrain`: the 7,329 results, the demo screenshots and the numbers in `docs/DEMO.md` and `docs/screenshots/10-demo-api-results.md` (threshold 19.3 there, 19.54 stored) will change and must be refreshed.
- The hosted path cannot be tried for real: no API key is configured. Tests use fake replies only; the document must say so.

## 3. Research and methodology column

All four pieces reuse the existing sections and add only what is missing. Each one gets a Markdown source in `docs/` first (a new file, so your local edit of `docs/ARCHITECTURE.md` is not touched), then goes into the Word file.

| Row | Table task | Already in the Word file | New work | Output |
|---|---|---|---|---|
| 3 | System architecture, data-flow diagrams, component descriptions | Section 11 (three tiers, Figure 1), Section 13 (stages, Figure 3) | A context diagram and a level-1 data-flow diagram (people and systems outside, processes, the six collections plus GridFS as data stores). A component table for each module in `backend/itd` and each dashboard page: job, input, output, depends on, test. | New subsections in Section 11, two figures, `docs/DATAFLOW.md` |
| 4 | Algorithms, frameworks, tools, libraries and their justification | Section 9 (design choices), Section 16 (model settings), references S1, S19, M2 to M6 | One table: layer, choice, version, reason, alternative not chosen and why. Versions are read from `requirements.txt` and `package.json` (they list lower bounds, such as `scikit-learn>=1.4` and `react ^18.3.1`; the installed versions come from the environment). Covers pandas, scikit-learn, XGBoost, SHAP, FastAPI, pymongo, bcrypt, PyJWT, httpx, React, Vite, MongoDB. Update the calibration and threshold text after row 3 and 4 code. | New subsection in Section 16, `docs/TOOLS_AND_ALGORITHMS.md` |
| 5 | Input data, preprocessing, expected outputs, validation rules | Section 14 (input files, session rules), Section 15 (features) | Three tables: preprocessing steps in order with their parameters; expected output of each stage with fields and ranges; validation rules in three places (log reading, API request checks, MongoDB rules) with the real error messages. Read `ingest.py`, `sessionize.py`, `api.py` and `schema.py` before writing; do not rely on memory. | New subsection in Section 14, `docs/DATA_RULES.md` |
| 6 | Evaluation criteria, test cases, measurable indicators | Section 17 (metrics, experiments A to E), Section 19 (resource plan), NF1 to NF5, Section 21 (test record) | An indicator table (definition, formula, target, how measured, current value). A test-case table (id, requirement, steps, expected result, recorded result). Run experiments A to D on generated data with a small script and measure batch time, peak memory and API time on this laptop. Every number marked as generated data and laptop-specific. | New subsection in Section 17, `docs/EVALUATION_CRITERIA.md` |

Placement: add these as subsections inside Sections 11, 14, 16 and 17, so no section is renumbered. The alternative is four new sections after Section 13, which renumbers Sections 14 to 23 again and means updating every cross-reference a second time. Recommended: subsections.

## 4. Closing steps after row 6
1. Section 21: close issues 1 to 5, update the test count and the test record. Section 22: update the objective and gap rows (O3, O4, G3 and the inconsistency row on promised features).
2. Update the test count in `README.md`, `docs/REQUIREMENTS.md`, `docs/DEMO.md` and `AGENTS.md`; refresh the known-gaps list in `AGENTS.md`.
3. Rebuild `Group7_Research_and_Methodology.docx` with the same layout, run the validity check, and run this document check again.
4. No row number or "Day" wording in the Word file.

## 5. Decisions needed
1. The deadline for rows 3 to 6, so the order can be cut if time is short. If time is short, the smallest useful set is: row 3 and 4 code (calibration, thresholds, leakage, answer check), then the research text for all four rows.
2. Permission to run `python -m itd.engine --retrain` on the main database and to apply the schema again. This replaces the stored results and models.
3. Whether the CSV download in row 6 is in scope. Analyst decisions are out of scope; a read-only download does not save any.
4. Placement of the new Word text: subsections (recommended) or new sections.
