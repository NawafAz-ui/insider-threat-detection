# Security notes

| Control | How it is done | Where |
|---|---|---|
| HTTPS/TLS | `python scripts/make_cert.py`, then `python -m itd.serve`; set `REQUIRE_HTTPS=1` to reject plain HTTP | `itd/serve.py`, `itd/api.py` |
| Authentication | bcrypt password hashes, signed login token that expires (30 min) | `itd/security.py` |
| Authorization | read-only analyst role; the API's only write is the access log | `itd/security.py`, `mongo-init/` |
| Input validation | strict request models, session ids must match `S<digits>`, question length limit | `itd/api.py` |
| Access logging | logins (ok and failed), sessions viewed, assistant questions | `itd/security.py` |
| Login throttling | 5 failed logins in 15 minutes pauses sign-in | `itd/security.py` |
| Model integrity | SHA-256 saved with each model and checked before use | `itd/engine.py` |
| Write separation | separate engine and API database accounts: `docker-compose.secure.yml` (not yet tested against a live server) | `mongo-init/init-users.js` |
| Backups | `python scripts/backup_db.py` (schedule with Task Scheduler or cron) | `scripts/backup_db.py` |
| Pseudonymized users | `--pseudonymize` and `PSEUDONYM_KEY` | `itd/ingest.py` |

## Encrypted storage (AES-256) - done outside the code
Put the MongoDB data on an encrypted disk: BitLocker (Windows Pro), FileVault (macOS) or LUKS (Linux).
For the secure compose file, place the Docker volume on that disk.

## Still the operator's job
Use a strong `JWT_SECRET` and analyst passwords, restrict the log and data folders to the administrator account,
and use a real certificate (not self-signed) outside development.
