# Input data, preprocessing, expected outputs and validation rules

Source text for the Word file (a subsection at the end of Section 14, "Data provenance and session construction"). Written on 1 November 2026 after reading `ingest.py`, `sessionize.py`, `aggregate.py`, `features.py`, `baselines.py`, `risk.py`, `api.py`, `security.py` and `schema.py`. The input files themselves are described in `docs/CSV_LAYOUT.md`.

<!-- word:start -->
## Preprocessing steps, expected outputs and validation rules

The input files and the session rules are described above. This subsection lists the preprocessing steps in the order the engine applies them, the output that each stage is expected to produce, and the rules that check data in three places: when the logs are read, in the API and in the database. It records what the code does at the time of writing; where a check is missing, it says so.

<!-- widths 520,1700,5173,2500 -->
| # | Step | Rule and parameters | Code |
|---|---|---|---|
| 0 | Validate | The folder is checked before anything is read. Errors stop the run: V1 a required file is missing, V2 a required column is missing, V3 a date is not MM/DD/YYYY HH:MM:SS, V8 answers.csv has no id column. Warnings are reported and the run continues: V4 empty id, user or pc; V5 an event id used more than once (inside a file or across files); V6 unknown activity in logon or device; V7 email size or attachments is not a number; V9 answer ids that match no event; V10 no answers.csv or an empty one. The report is saved as validation.json and a summary is stored in the run document. | validate.py, engine.py |
| 1 | Read | Five CSV files are read in chunks of 500,000 rows. Only the listed columns are read, all as text. Extra columns are ignored. | ingest.py |
| 2 | Parse dates | The format is MM/DD/YYYY HH:MM:SS. Another format stops the run. | ingest.py |
| 3 | Pseudonymize (optional) | A user id becomes “U-” and the first 10 hexadecimal characters of an HMAC-SHA256 of the id with the key PSEUDONYM_KEY. | ingest.py |
| 4 | Build sessions | For each user and PC in time order, a Logon opens a session. A Logoff closes it. A missing Logoff ends it at the next Logon or after 12 hours, and a matched session is also cut at 12 hours. Midnight does not split a session. Sessions are sorted by start and get an id of S and seven digits. | sessionize.py |
| 5 | Attach events | An event goes to the session of the same user and PC that started at or before the event and had not ended. Other events are dropped. | sessionize.py |
| 6 | Label | A session is malicious if one of its events has an id in answers.csv. Without that file every label is 0. | ingest.py |
| 7 | Count events | Device: Connect events. File: archive endings .zip, .rar, .7z; executable endings .exe, .bat, .dll; a path that starts with a drive letter d to z counts as removable. Email: addresses other than @dtaa.com are external; attachment count and size are read as numbers (an invalid value becomes 0) and the size is in KB. Web: job sites monster.com, indeed.com, linkedin.com/jobs; leak sites wikileaks, dropbox, pastebin, mega.nz. Distinct files, URLs and domains are counted through hashed pairs. | aggregate.py |
| 8 | Session features | After hours means a logon at or after 19:00 or before 07:00. The rate per hour divides by at least 15 minutes. The two day counts cover only the sessions up to the current one. | features.py, config.py |
| 9 | Baseline deviations | The mean and standard deviation of each of ten metrics come from the same user’s earlier sessions only. The deviation is zero until five earlier sessions exist, divides by at least 0.5 and is limited to the range −10 to 10. Recency is the working time since the previous session start, with whole weekend days removed. | baselines.py |
| 10 | Split | Time order: 70% training, 15% validation, 15% test. Each part needs at least one malicious session when models are trained. When a saved model is reused without retraining, the sessions are labelled scored. | models.py, engine.py |
| 11 | Scale and score | Logistic Regression scales its inputs with the training data. Isolation Forest scores are scaled to 0 to 1 with the training minimum and maximum. | models.py |
| 12 | Calibrate | A sigmoid per model is fitted on the validation part only. | risk.py |
| 13 | Risk score | 100 times the weighted sum of the calibrated scores. The weights add up to 1. A session is flagged at or above the threshold. | risk.py |

<!-- widths 1800,2900,5193 -->
| Stage | Output | Fields and expected ranges |
|---|---|---|
| Sessions | One row per session | user, pc, start, end, logoff_missing (0 or 1), session id, label (0 or 1) |
| Counts | 16 count columns per session | Each is zero or more |
| Features | 39 columns, saved in a fixed order with the models | Finite numbers; the ten deviation features lie between −10 and 10 |
| Model scores | lr, xgb, iforest | Raw scores and calibrated scores, each from 0 to 1 |
| Risk | Score and flag | Risk score and threshold from 0 to 100; flagged is true or false |
| Result document | One per session in results | session id, run_id, user, pc, start, end, risk_score, flagged, model_scores, top_shap (at most 3 items with feature, value, shap, strength strong or minor, text), baseline_deviations (at most 3 items with metric, value, user_mean, user_std, z from 0 to 10, text), label, split (train, validation or test) |
| Baseline document | One per user in user_baselines | n (at least 1), mean and m2 for the ten metrics (m2 is zero or more), last (start of the last session) |
| Model document | One in trained_models, id current | Three GridFS file ids, three SHA-256 values of 64 hexadecimal characters, risk (calibrators, weights, threshold from 0 to 100, validation thresholds and F1), the 39 feature names, metrics, trained_at |
| Run document | One per batch run in runs | run id, time, seconds, seconds per step, sessions, flagged, threshold, weights, metrics, validation summary (status, errors, warnings, rows per file) |
| Run request document | One per dashboard run request in run_requests | status (requested, running, done or failed), dataset folder name, retrain, requested_by, requested_at, started_at, finished_at, message (the reason when it failed), log_tail (at most 1,500 characters), run_id |

<!-- widths 1700,5100,3093 -->
| Where | Rule | Response |
|---|---|---|
| Reading logs | A CSV file is missing. | The run stops at the validation step with rule V1, for example "[V1 error] device.csv: a required CSV file is missing: device.csv - 1". |
| Reading logs | A listed column is missing or a date has another format. | The run stops before anything is read, with a message that names the rule (V2 or V3), the file, the count and the first line numbers. |
| Reading logs | Training, validation or test part has no malicious session. | The run stops: “Each of train/validation/test needs at least one malicious session.” |
| Reading logs | A saved model no longer matches its SHA-256 value. | The run stops: “Saved model '<name>' failed its integrity check; it may have been changed. Retrain with --retrain.” |
| API request | Login: username of 1 to 64 characters from A to Z, a to z, 0 to 9, underscore, dot and hyphen; password of 1 to 128 characters; no other field. | 422 |
| API request | Question of 1 to 300 characters. | 422 |
| API request | Session id of S and 1 to 12 digits; user id of 1 to 64 characters from the set above. | 422 “Invalid session id” or “Invalid user id” |
| API request | Paging: session list limit 1 to 200 and offset 0 to 100,000; user history limit 1 to 2,000. | 422 |
| API access | No token; invalid or expired token; a role other than analyst or admin. | 401 “Login required”; 401 “Invalid or expired token”; 403 “Not allowed” |
| API access | Wrong password; five failed logins for a username or address within 15 minutes. | 401 “Wrong username or password”; 429 “Too many failed logins. Try again later.” |
| API access | Plain HTTP while REQUIRE_HTTPS is 1. | 426 “HTTPS required” |
| API data | Unknown session, user or run. | 404 “Session not found”, “User not found” or “No batch run recorded yet. Run the detection engine first.” |
| API data | MongoDB stopped or another unexpected fault. | 503 “The database is not reachable. Start MongoDB and try again.”; 500 “The server had a problem. It has been logged.” |
| Database | After python -m itd.schema apply, MongoDB refuses a document that breaks the rules of its collection: results (ranges and enumerations above), user_baselines, trained_models, runs, run_requests (status requested, running, done or failed; dataset folder-name pattern; message of at most 500 characters), analyst_accounts (id pattern, bcrypt hash pattern, role analyst or admin), access_log (action from a fixed list of seven, question of at most 300 characters). | The write is rejected (error code 121 in the recorded demonstration, Section 21). |

Checks that are still missing: the validator does not check time zones, orphan logoffs, file hashes or the time range of a release, and it cannot tell whether the labels are correct. Duplicate event ids, empty id, user or pc values, unknown activities and non-numeric email sizes are now reported as warnings (rules V4 to V7) but the data is still accepted exactly as the ingestion code reads it. The database rules cannot check links between collections, which is why the tests check the run link separately.
<!-- word:end -->
