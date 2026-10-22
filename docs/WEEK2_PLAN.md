# Week 2 prototype plan: review, issues and prioritized features

Insider Threat Detection System, Capstone Project A. Prototype track, Oct 19 to 25.
Days 1 and 2 were completed on Oct 21 (catch-up), together with Day 3.

## Day 1: review of the existing prototype

### Where the prototype stands (end of Week 1, approved by the supervisor)
- **Detection engine:** reads CERT-layout CSV logs (sample data), builds sessions and 39 features, scores with three models, explains with SHAP and baseline differences.
- **REST API:** login, flagged session list, session detail, assistant chat.
- **Dashboard:** Login, Flagged Sessions, Session Detail with chat panel.
- **Database:** MongoDB with results, trained models (GridFS), user baselines, analyst accounts, access log and run records.
- **Security basics:** hashed passwords, expiring token, read-only role, input validation, access log, login throttling.
- **Checks:** 15 automated tests pass; the connection check reports all links working.

Only one user workflow was demonstrated: review a flagged session.

### Incomplete features and technical issues

| # | Issue | Type | Priority | Planned fix | Status |
|---|---|---|---|---|---|
| 1 | Only one user workflow works end to end; two are required | Missing feature | High | Day 4, Day 7 | Open |
| 2 | No way to see a user's session history or baseline, although the data is in the database | Missing feature | High | Day 4 | Open |
| 3 | No URL navigation: the Back button leaves the app and a session cannot be opened by link | Interface | Medium | Day 3 | Done |
| 4 | Login form validation is minimal; an expired token reloads the page without a message | Interface | Medium | Day 3 | Done |
| 5 | Baseline differences show "10.0 std" when the value is capped at 10 (really "10 or more") | Accuracy | Low | Day 3 | Done |
| 6 | Without a language-model key the assistant lists every evidence item (long and technical) | Usability | Medium | Day 4 | Open |
| 7 | Engine runs only from the command line; the dashboard cannot show the last run or model results | Missing feature | Medium | Day 4 | Open |
| 8 | Database schema is documented in prose only: no validation rules, no relationship diagram, no index for access-log queries or results by user | Database | High | Day 5 | Open |
| 9 | Server errors show a generic "Request failed" | Error handling | Medium | Day 3 | Done |
| 10 | Assistant with a real language-model key has never been tested | Verification | Medium | Day 6 if a key is available | Open |
| 11 | Not yet tested: real CERT files, real SPEDIA columns, separate database accounts on a live server, the start script on Windows, HTTPS in a browser | Verification | Medium | Day 6 and 7 as time allows | Open |
| 12 | The dashboard has no automated tests (the backend has 15) | Testing | Low | Day 7 | Open |
| 13 | Sample data is too easy (near-perfect scores); its results must not be quoted as findings | Data | Low | Note in report | Open |

## Day 2: prioritized feature list (MoSCoW)

**Must have**
- Workflow 1 polished: flagged list, session detail, assistant.
- Workflow 2 new: investigate a user (session history, risk over time, normal-behavior summary, links to each session).
- URL navigation and deep links, form validation, clear error messages.
- Database schema with indexes, validation rules and a relationship diagram.
- API error handling and tests for every new endpoint.

**Should have**
- Run status and model results endpoint, with a small "last batch run" panel.
- Shorter, plainer assistant answer without a language-model key.
- "10 or more" display for capped values.
- Frontend tests for the main components.

**Could have**
- Level filter and user search on the flagged list.
- Export of the flagged list to CSV.
- Harder sample data.

**Will not do this week**
- Full real CERT run and real SPEDIA mapping.
- Analyst review decisions saved by the API. This would let the API write results, which changes the proposal's rule that the API only writes the access log, so it needs supervisor approval first.
- A user-administration screen.

### The two workflows for the demonstration
1. **Review a flagged session:** sign in, open the flagged list, open a session, read the explanation, ask the assistant.
2. **Investigate a user:** from a session open the user, see their sessions over time and normal behavior, open another of their sessions, ask the assistant.

Both are read-only, so they stay within the approved proposal design.

## Day plan

| Day | Date | Task | Output | Status |
|---|---|---|---|---|
| 1 | Oct 19 | Review prototype, list issues | This document | Done |
| 2 | Oct 20 | Finalize MVP, prioritize features | This document | Done |
| 3 | Oct 21 | Interface: navigation, form validation, error states | Updated dashboard | Done |
| 4 | Oct 22 | Backend: user history endpoint, run status endpoint, shorter assistant answer | New endpoints with tests | Planned |
| 5 | Oct 23 | Database: schema, relationships, indexes, validation rules, CRUD | Schema document and diagram | Planned |
| 6 | Oct 24 | Integrate and handle errors; update connection check | Retested system | Planned |
| 7 | Oct 25 | Test and demonstrate two workflows; screenshots | Demo script and screenshots | Planned |

## Submission checklist for Oct 25 (prototype items)
- Updated system architecture and database schema.
- Functional and non-functional requirements.
- GitHub repository with meaningful commits.
- Screenshots and demonstration of at least two working workflows.
