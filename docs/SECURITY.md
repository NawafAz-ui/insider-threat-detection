# Security notes

| Control | How it is done | Where |
|---|---|---|
| HTTPS/TLS | `python scripts/make_cert.py`, then `python -m itd.serve`; set `REQUIRE_HTTPS=1` to reject plain HTTP | `itd/serve.py`, `itd/api.py` |
| Authentication | bcrypt password hashes, signed login token that expires (30 min) | `itd/security.py` |
| Authorization | the analyst role is read-only; only an admin can ask for a batch run (a request, never a result); the API writes only the access log and run requests | `itd/security.py`, `mongo-init/` |
| Input validation | strict request models, session ids must match `S<digits>`, question length limit | `itd/api.py` |
| Access logging | logins (ok and failed), sessions viewed, assistant questions | `itd/security.py` |
| Login throttling | 5 failed logins in 15 minutes pauses sign-in | `itd/security.py` |
| Model integrity | SHA-256 saved with each model and checked before use | `itd/engine.py` |
| Write separation | separate engine and API database accounts (`docker-compose.secure.yml`). Tested on a real MongoDB with the same roles: the API account is denied writes to results, accounts and models, and may only add access-log entries. The Docker start-up script itself has not been run | `mongo-init/init-users.js` |
| Run requests | admin-only `POST /api/run`; the dataset is a folder NAME that must match a strict pattern and contain logon.csv inside the data folder, never a path; the API only inserts a request and a separate worker with the engine account performs it; the log text is shown to admins only; one run at a time | `itd/jobs.py`, `itd/worker.py`, `itd/api.py` |
| Data validation | the data folder is checked before every run: a missing file or column or a wrong date format stops the run with a clear message; duplicates, empty fields and other problems are reported | `itd/validate.py` |
| Run report | a read-only endpoint for analysts and admins; every value from the database is escaped before it goes into the HTML; the page has no scripts and no external files; it is sent as a download with no caching; each download is logged as `report_viewed` | `itd/report.py`, `itd/api.py` |
| Backups | `python scripts/backup_db.py` (schedule with Task Scheduler or cron) | `scripts/backup_db.py` |
| Pseudonymized users | `--pseudonymize` and `PSEUDONYM_KEY` | `itd/ingest.py` |

## Encrypted storage (AES-256) - done outside the code
Put the MongoDB data on an encrypted disk: BitLocker (Windows Pro), FileVault (macOS) or LUKS (Linux).
For the secure compose file, place the Docker volume on that disk.

## Still the operator's job
Use a strong `JWT_SECRET` and analyst passwords, restrict the log and data folders to the administrator account,
and use a real certificate (not self-signed) outside development.

## After upgrading an existing secure database
The API account now also needs `find` and `insert` on `run_requests` (see `mongo-init/init-users.js`). The init script runs only when the database volume is empty, so an existing secure database needs its API role updated with `db.updateRole`, and `python -m itd.schema apply` must be run once for the new collection and the new log action.
