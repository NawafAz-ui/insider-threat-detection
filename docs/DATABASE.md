# Database (MongoDB, database name `insider_threat`)

| Collection | One document is | Written by | Read by |
|---|---|---|---|
| `results` | one scored session: `session_id`, `user`, `pc`, `start`, `end`, `risk_score`, `flagged`, `model_scores`, `top_shap`, `baseline_deviations`, `label`, `split` | engine | API |
| `trained_models` | the current model set: GridFS file ids, SHA-256 of each file, risk weights and threshold, feature list, test metrics (models themselves are in GridFS: `fs.files`, `fs.chunks`) | engine | engine |
| `user_baselines` | one user's running mean and variance for the 10 baseline metrics (`n`, `mean`, `m2`) | engine | engine, API (user history page) |
| `analyst_accounts` | `_id` = username, `password_hash` (bcrypt), `role` | `scripts/analysts.py` | API |
| `access_log` | `at`, `user`, `action`, `ip`, extras: logins (ok and failed), sessions viewed, assistant questions | API | API (login throttling) |
| `runs` | one batch run: seconds, per-step seconds, sessions, flagged, threshold, weights, test metrics | engine | API (threshold, counts, latest run) |

Indexes on `results`: (`flagged`, `risk_score` descending) for the flagged list, and (`user`, `start`) for a user's history. Both are created by the engine.

## Basic operations
- Create, read, update, delete analysts: `python -m scripts.analysts list|add|role|password|delete`
- Show every collection and a CRUD round trip: `python scripts/demo_db.py`
- Back up and restore: `python scripts/backup_db.py` and `--restore <folder>`

## Look inside with mongosh
```powershell
docker exec -it itd-mongo-1 mongosh insider_threat
db.results.find({flagged:true}).sort({risk_score:-1}).limit(3)
db.analyst_accounts.find({}, {password_hash:0})
db.access_log.find().sort({at:-1}).limit(5)
```
