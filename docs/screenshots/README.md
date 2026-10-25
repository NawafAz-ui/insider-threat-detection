# Screenshots

Evidence for the Week 2 prototype demonstration. The steps are in `docs/DEMO.md`.

## Workflow 1: review a flagged session
- `02-signin-validation.png`: sign-in form validation
- `03-flagged-list.png`: flagged sessions with the summary cards and the last batch run
- `04-session-detail.png`: risk score and the reasons behind it
- `05-assistant-why-flagged.png`: the assistant's short answer, with the evidence it used
- `05b-assistant-zip-question.png`: a focused question gets only the matching evidence

## Workflow 2: investigate a user
- `06-user-page-U0027.png`: one user's session history
- `07-risk-timeline-U0027.png`: risk over time with the flag threshold
- `08-user-tables-U0027.png`: what is normal for the user, and their flagged sessions
- `08b-user-page-U0080.png` and `08c-risk-timeline-U0080.png`: the same page for a second user

## Error handling, database and tests
- `09-database-down.png`: clear message when MongoDB is stopped
- `12-demo-schema.png`: MongoDB rejects invalid documents (code 121)
- `13-tests-and-schema-check.png`: 27 automated tests pass, and every stored document follows the database rules

The data is synthetic sample data in the CERT r4.2 file layout, so the scores are not research results.
