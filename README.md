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
| `frontend/` | the four screens: Login, Flagged Sessions, Session Detail, User Page |
| `docs/` | CSV layout, API reference (`API.md`), database schema (`DATABASE.md`), requirements (`REQUIREMENTS.md`), architecture (`ARCHITECTURE.md`), security notes |
| `word-reports/` | the group's Word reports (Research and Methodology versions) |

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
The prototype's dataset is SPEDIA (a small public insider-threat dataset, CC BY 4.0), already converted to the CERT layout in
`backend/data/spedia_cert` (1.4 MB, gzip-compressed CSV files, see `SOURCE.md` there). Generated sample data can be made as well.
The data is split by time into 80% training and 20% test; thresholds and calibration come from cross-validation inside the training part.
```powershell
# backend folder, virtual environment active
python -m itd.engine --data data\spedia_cert --retrain          # prints precision / recall / F1 / PR-AUC on the test part
python scripts\generate_synthetic_cert.py data\cert_synthetic   # optional: generated sample data in the same layout
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
pytest -q                                                        # 91 tests with an in-memory database; set ITD_TEST_MONGO=mongodb://localhost:27017 to add the real-server test
```

## Datasets
SPEDIA (used by the prototype): download `logs_SPEDIA_annotated_en.csv` from https://doi.org/10.5281/zenodo.15525713, check its MD5
(e01e0baaf3b523a0b493fc9c52af2b1c), then `python -m itd.spedia --csv <file> --map spedia_mapping.json --out data\spedia_cert` and
`python scripts\prepare_split.py data\spedia_cert data\spedia\prepared` (input check, preprocessing and split without the database).
CERT r4.2 (the original research dataset, planned for Capstone B): see `docs/CSV_LAYOUT.md`; `scripts\extract_cert.py` unpacks an
official release keeping only the columns the engine reads, and `scripts\build_answers.py` builds the answer file.
Every data file may be stored as `name.csv` or `name.csv.gz`.

## Integrated test
`python scripts\integration_test.py` starts the API, the worker and the dashboard against a scratch database and runs the cases of
`docs/INTEGRATED_TESTING_PLAN.pdf` (needs MongoDB and Node; the page-load check also needs Chrome and `puppeteer-core`).
It stops and restarts the MongoDB container once to check recovery. Last result: 10 of 10 cases passed on 16 November 2026
(`docs/INTEGRATED_TEST_REPORT.pdf`).

## Assistant
Set `LLM_API_KEY` to use a hosted LLM. Without a key it answers from a local template. It only receives the stored
evidence of one session (R, S1-S3, B1-B3), never user or PC names.

## Status
See `docs/SECURITY.md` for security controls. Not yet verified: the secure MongoDB accounts (`docker-compose.secure.yml`)
against a live server, the original CERT r4.2 release, and the hosted-LLM call with a real key.
