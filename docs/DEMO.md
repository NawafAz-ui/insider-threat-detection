# Demonstration of the connected user workflows (about 6 minutes, live)

The prototype runs on SPEDIA, a small public dataset converted to the CERT file layout (`backend/data/spedia_cert`). The workflows are connected: workflow 2 starts from the session opened in workflow 1. The screenshots in `docs/screenshots/` were taken on 16 November 2026 from a copy of the main database (`docs/src/demo_screenshots.py`), so a live demo shows the same screens.

## Before you start
1. Docker Desktop is running and MongoDB is up (`docker ps` shows the container, on this laptop `insider-threat-detection-mongo-1`).
2. API running (`python -m itd.serve` in `backend`), run worker running (`python -m itd.worker` in `backend`) and dashboard running (`npm run dev` in `frontend`).
3. An administrator account exists (`python -m scripts.analysts add admin "<password>" admin`) and `alice` is an analyst.
4. `python scripts/check_connection.py --user alice --password "<password>"` shows every line OK (246 sessions, 111 flagged). **Screenshot 1.**

## Workflow 0: start a batch run from the dashboard (administrator)
| Step | Do | Expect | Screenshot |
|---|---|---|---|
| A | Sign in as `admin` | the Run analysis card above the flagged list: dataset folder, a "Train new models" box and Start run. An analyst does not see this card | 14 |
| B | Choose `spedia_cert`, leave "Train new models" off, click Start run | the status line says "Waiting for the worker", then "Running". Start run is greyed out until the run ends | 15 |
| C | Wait a few seconds | "Finished" with the end time. Show details opens the engine log. The cards, the results table and the flagged list reload | 16 |
| D | Click Download run report | one HTML page: run summary, test results, the 10 highest-risk sessions with their reasons, limits | 17 |

Notes: the dashboard only files a request. The worker performs the run and writes its progress. A second Start run while one is waiting or running is refused (409). If no worker is running, after 20 seconds the card says so and names the command. The run gives 246 sessions, 111 flagged and flag threshold 35.5.

## Workflow 1: review a flagged session
| Step | Do | Expect | Screenshot |
|---|---|---|---|
| 1 | Open the dashboard, click Sign in with empty fields | red messages under both fields | 2 |
| 2 | Sign in as `alice` | the flagged list: cards (Flagged 111, Flag threshold 35.5, Review first), the last batch run with its results table per model, a CSV download button, sessions highest risk first with user and computer | 3 |
| 3 | Open the top session (user `irene`, score 96) | score ring, the computer, "What drove the XGBoost score" (S1 to S3), "Different from this user's normal" (B1 to B3), the notice that a flag is not proof | 4 |
| 4 | Ask the assistant "Why was this session flagged?" | a short answer ending with evidence tags | 5 |
| 5 | Ask "Why is the USB use a concern?" | only the removable-device evidence and its tag | 5b |

## Workflow 2: investigate that user (continues from workflow 1)
| Step | Do | Expect | Screenshot |
|---|---|---|---|
| 6 | Click the user name in the session title | the user page, address ends in `#/user/irene` | 6 |
| 7 | Look at "Risk over time" | grey dots for ordinary sessions, large coloured dots for flagged ones, the dashed threshold line | 7 |
| 8 | Look at "What is normal for this user" and "Flagged sessions of this user" | the 10 normal-behavior values and the flagged sessions with their levels and computers | 8 |
| 9 | Click a coloured dot or a flagged row | that session opens. Browser Back returns to the user page | |

## Error handling (30 seconds)
| Step | Do | Expect | Screenshot |
|---|---|---|---|
| 10 | Run `docker stop insider-threat-detection-mongo-1`, then sign in or click a session | a clear message such as "The database is not reachable. Start MongoDB and try again." with Try again | 9 |
| 11 | Run `docker start insider-threat-detection-mongo-1`, wait 5 seconds, click Try again | the session loads again | |

## Behind the screen (1 minute)
- `python scripts/demo_api.py --user alice --password "<password>"`: every API call with its status code (13 calls, all as expected). **Result 10** (`10-demo-api-results.md`).
- `python -m itd.schema check` and `python scripts/demo_schema.py`: the database rules, and bad documents rejected. **Screenshots 12 and 13.**
- `python -m pytest -q` in `backend`: 91 passed, 1 skipped. **Screenshot 13.**
- `python scripts/integration_test.py` in `backend`: the integrated test, 10 of 10 cases passed on 16 November 2026 (`docs/INTEGRATED_TEST_REPORT.pdf`).

## What to say about the limits
- SPEDIA is a small public dataset used for prototype purposes. CERT r4.2 is the original dataset of the research and has not been run through the models, so these scores are not research results.
- A flag is a lead for a human, never proof of wrongdoing.
- The assistant answered offline from the stored evidence. The hosted language-model call has not been tested with a key.
- Screenshots 2, 9 and 12 do not depend on the data and were not retaken.
