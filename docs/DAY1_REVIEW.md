# Day 1 review: methodology gaps and prototype completion

## A. Methodology: missing technical details found
| # | Gap | Action |
|---|---|---|
| M1 | Python dependencies have lower bounds only, no lock file | Saved backend/requirements.lock.txt |
| M2 | Python and MongoDB versions | Already stated in docs/TOOLS_AND_ALGORITHMS.md (Python 3.14.6, mongo:7). A second environment (Python 3.14.5, Docker 29.9.2) is now added there. This was first listed as a gap by mistake. |
| M3 | Missing column or bad date stops with a raw pandas error; duplicates and non-numeric email size accepted silently | Day 2: pre-flight validation report |
| M4 | No way to start or monitor a run from the dashboard | Done on Day 3: run request, worker and the Run analysis panel |
| M5 | Real CERT r4.2 and SPEDIA never run; all numbers from generated data | State as a limit in every result |
| M6 | SHAP explains the XGBoost model only | Keep this sentence in the methodology |
| M7 | Time split by position needs sessions sorted by start | sessionize.py sorts by start; state the assumption |

## B. Prototype: engine fixes made
| # | Problem | Fix |
|---|---|---|
| P1 | Engine deleted all results before writing new ones | Same-id results are replaced block by block; results of older runs are deleted after all new ones are saved |
| P2 | Without --retrain, sessions were tagged train/validation/test although the saved model never trained on them | Tagged "scored"; schema.py allows the value |
| P3 | "39 features" typed into a message | Uses len(FEATURES) |

Remaining limit of P1: a crash midway leaves a mix of old and new results until the next complete run.

## C. Check
pytest -q: 42 passed, 1 skipped (real-MongoDB test).
