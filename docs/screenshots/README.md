# Screenshots

Evidence for the prototype demonstration, retaken on 16 November 2026 on SPEDIA (246 sessions, 111 flagged, flag threshold 35.5) from a copy of the main database with `docs/src/demo_screenshots.py`. Screenshots 2, 9 and 12 do not depend on the data and were not retaken. The steps are in `docs/DEMO.md`.

## Workflow 0: start a batch run from the dashboard
- `14-admin-run-panel.png`: the administrator's Run analysis card above the flagged list
- `15-run-requested.png`: the request filed, waiting for the worker
- `16-run-finished.png`: the run finished, the engine log, and the list reloaded with the new run
- `17-run-report.png`: the downloaded run report

## Workflow 1: review a flagged session
- `02-signin-validation.png`: sign-in form validation
- `03-flagged-list.png`: flagged sessions with the summary cards, the last batch run, user and computer
- `04-session-detail.png`: risk score, the computer and the reasons behind the score
- `05-assistant-why-flagged.png`: the assistant's short answer, with the evidence it used
- `05b-assistant-focused-question.png`: a focused question gets only the matching evidence (questions in `questions.txt`)

## Workflow 2: investigate a user
- `06-user-page.png`: one user's session history
- `07-risk-timeline.png`: risk over time with the flag threshold
- `08-user-tables.png`: what is normal for the user, and their flagged sessions

## Error handling, database and tests
- `01-connection-check.png`: every connection checked
- `09-database-down.png`: clear message when MongoDB is stopped
- `10-demo-api-results.md`: every API call with its status code
- `12-demo-schema.png`: MongoDB rejects invalid documents (code 121)
- `13-tests-and-schema-check.png`: the automated tests pass, and every stored document follows the database rules

SPEDIA is used for prototype purposes. These scores are not research results.
