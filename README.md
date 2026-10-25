# Insider Threat Detection System (prototype)

Capstone Project A. Scores user work sessions 0 to 100 from CERT-layout logs, explains each flag, and shows flagged sessions to a security analyst.

```
Frontend  React (Vite)            frontend/
Backend   Python, FastAPI,        backend/itd/
          pandas, scikit-learn, XGBoost, SHAP, LLM API client
Database  MongoDB (PyMongo/GridFS) docker-compose.yml
```

## Project layout
| Path | What it is |
|---|---|
| `backend/itd/` | detection engine (`ingest`, `sessionize`, `features`, `baselines`, `models`, `risk`, `explain`, `engine`), REST API (`api`, `security`, `assistant`), SPEDIA tools (`spedia`, `cross_eval`) |
| `backend/scripts/` | sample-data generator, account creation, setup check, TLS certificate, backup, answer-file builder |
| `backend/tests/` | automated tests (no MongoDB needed) |
| `frontend/` | the three screens: Login, Flagged Sessions, Session Detail |
| `docs/` | CSV layout, API reference (`API.md`), database schema (`DATABASE.md`), requirements (`REQUIREMENTS.md`), architecture (`ARCHITECTURE.md`), security notes |

## Set up (Windows PowerShell; on macOS/Linux use `source .venv/bin/activate`)
Run each line separately from the project root.

```powershell
docker compose up -d                          # MongoDB (Docker Desktop must be running)
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\check_setup.py                 # every line should say OK
```

## Run
```powershell
# backend folder, virtual environment active
python scripts\generate_synthetic_cert.py data\cert_synthetic
python -m itd.engine --data data\cert_synthetic --retrain       # prints precision / recall / F1 / PR-AUC
python -m scripts.create_analyst alice "ChooseAStrongOne1!" analyst
$env:JWT_SECRET = python -c "import secrets; print(secrets.token_hex(32))"   # random 64-character secret
python -m itd.serve                                              # http://127.0.0.1:8000 (API docs at /docs)

# second terminal
cd frontend
npm install
npm run dev                                                      # http://localhost:5173
```

## Check the connections / one-command start
```powershell
.\start_all.ps1                                  # database + API + dashboard (Windows)
cd backend; python scripts\check_connection.py --user alice --password "ChooseAStrongOne1!"
```
See `docs/DEMO.md` for the demo checklist.

## Database rules and demo
```powershell
cd backend
python -m itd.schema apply                     # once, as administrator: validation rules and indexes
python -m itd.schema check                     # every stored document against the rules
python scripts\demo_schema.py                  # valid documents accepted, invalid ones rejected
```

## Demo the database
```powershell
cd backend
python scripts\demo_db.py                      # every collection plus a create/read/update/delete round trip
python -m scripts.analysts list                # manage analyst accounts: list, add, role, password, delete
```

## Demo the API
```powershell
cd backend
python scripts\demo_api.py --user alice --password "ChooseAStrongOne1!"      # calls every endpoint and prints the results
```
Interactive docs: http://127.0.0.1:8000/docs

## Test
```powershell
cd backend
pytest -q                                                        # 27 tests with an in-memory database; set ITD_TEST_MONGO=mongodb://localhost:27017 to add the real-server test
```

## Using real data
CERT r4.2: see `docs/CSV_LAYOUT.md` (and `scripts/build_answers.py` for the answer files).
SPEDIA: `python -m itd.spedia --inspect logs_SPEDIA.csv`, fill in `backend/spedia_mapping.example.json`, convert, then
`python -m itd.cross_eval --train <cert-folder> --test <converted-spedia-folder>`.

## Assistant
Set `LLM_API_KEY` to use a hosted LLM. Without a key it answers from a local template. It only receives the stored
evidence of one session (R, S1-S3, B1-B3), never user or PC names.

## Status
See `docs/SECURITY.md` for security controls. Not yet verified: the secure MongoDB accounts (`docker-compose.secure.yml`)
against a live server, real CERT/SPEDIA files, and the hosted-LLM call with a real key.
