# System architecture (updated for Week 2)

Three tiers, as in the proposal, plus a batch detection engine that fills the database.

    ```mermaid
    flowchart LR
        subgraph Data["External data sources"]
            CERT["CERT r4.2 CSV logs"]
            SPEDIA["SPEDIA (exploratory)"]
        end
        subgraph Batch["Batch: detection engine (Python)"]
            I["1 Ingest in chunks"] --> S["2 Sessions"] --> F["3 39 features + baselines"] --> M["4 Three models"] --> R["5 Risk score + SHAP"]
        end
        subgraph DB["Database tier: MongoDB"]
            D1[("results")]
            D2[("user_baselines")]
            D3[("trained_models + GridFS")]
            D4[("runs")]
            D5[("analyst_accounts")]
            D6[("access_log")]
            D7[("run_requests")]    end
    subgraph API["Backend tier: FastAPI"]
        SEC["Security controls: HTTPS, token, role, validation, throttling, access log"]
        EP["Endpoints: login, sessions, session detail, users, run/latest, run request and status, chat, health"]
        AS["Evidence-grounded assistant"]
    end
    subgraph UI["Frontend tier: React"]
        P1["Login"] --> P2["Flagged list"] --> P3["Session detail + chat"]
        P2 --> P4["User page"]
        P3 --> P4
    end
    LLM["Hosted LLM API (evidence only)"]
    CERT --> I
    SPEDIA -.-> I
    R --> D1 & D2 & D3 & D4
    D7 -.->|new request| W["Run worker (engine account)"]
    W -->|starts| I
    W -->|progress| D7
    UI -->|requests| SEC --> EP
    EP --> D1 & D2 & D4 & D5
    EP -->|writes only| D6 & D7
    EP --> AS -.-> LLM
```

## What changed since the proposal figure
| Change | Why |
|---|---|
| `GET /api/users/{id}` and the user page | second workflow: investigate a user |
| `GET /api/run/latest` and the run panel | show when the engine last ran and its test results |
| `GET /api/health` and clear error messages | the user can tell whether the API or the database is down |
| Database validation rules, indexes and `run_id` links | consistent data; results are tied to the run that produced them |
| `POST /api/run`, `GET /api/run/status`, `python -m itd.worker` and the Run analysis panel | an administrator starts a batch run from the dashboard; the API files a request and the worker performs it |
| Input validation step (`itd/validate.py`) | bad data is named and stopped before the engine reads it |
| Login throttling and model integrity check | extra protection from the security section |

## Request flow (workflow 1 and 2)
1. The analyst signs in; the API checks the password hash and returns a token (30 minutes).
2. The dashboard asks for the flagged list; the API checks the token and role, reads `results`, writes an access-log entry.
3. The analyst opens a session (`results`) and may ask the assistant, which sees only the stored evidence.
4. The analyst opens the user page: sessions from `results`, normal behavior from `user_baselines`.

The API writes only the access log and run requests (an insert). The engine side (the engine and the run worker) writes results, baselines, models, run records and the progress of run requests.

## Request flow (workflow 3: run a batch from the dashboard)
1. An administrator chooses a dataset folder and clicks Start run. The API checks the role and the folder name, stores a request with status `requested` and writes a `run_requested` access-log entry.
2. The worker (`python -m itd.worker`, engine account) takes the oldest waiting request and sets it to `running`.
3. The worker runs the engine: validation, sessions, features, models, risk score and explanation. The engine output is kept as a log.
4. The worker records `done` or `failed`, the end time, the reason and the run id. The dashboard asks for the status every 3 seconds while a run is active and loads the flagged list again when it is done.
