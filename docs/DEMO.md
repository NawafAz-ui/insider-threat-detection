# Day 7: demonstration of two connected user workflows (about 6 minutes)

The two workflows are connected: workflow 2 starts from the session opened in workflow 1.

## Before you start
1. Docker Desktop is running and MongoDB is up (`docker ps` shows `itd-mongo-1`).
2. API running (`python -m itd.serve` in `backend`) and dashboard running (`npm run dev` in `frontend`).
3. `python scripts\check_connection.py --user alice --password "<password>"` shows every line OK. **Screenshot 1.**

## Workflow 1: review a flagged session
| Step | Do | Expect | Screenshot |
|---|---|---|---|
| 1 | Open the dashboard, click Sign in with empty fields | red messages under both fields | 2 |
| 2 | Sign in as `alice` | the flagged list: cards (Flagged, Flag threshold, Review first), the "Last batch run" line, sessions highest risk first | 3 |
| 3 | Open the top session | score ring, "What drove the score" (S1 to S3), "Different from this user's normal" (B1 to B3), the notice that a flag is not proof | 4 |
| 4 | Ask the assistant "Why was this flagged?" | a short answer ending with evidence tags | 5 |
| 5 | Ask "Were zip files involved?" | only the zip evidence, tags R, S1, B3 | |

## Workflow 2: investigate that user (continues from workflow 1)
| Step | Do | Expect | Screenshot |
|---|---|---|---|
| 6 | Click the user name in the session title | the user page, address ends in `#/user/U....` | 6 |
| 7 | Look at "Risk over time" | grey dots for ordinary sessions, large coloured dots for flagged ones, the dashed threshold line | 7 |
| 8 | Look at "What is normal for this user" and "Flagged sessions of this user" | the 10 normal-behavior values and the flagged sessions with their levels | 8 |
| 9 | Click a coloured dot or a flagged row | that session opens; browser Back returns to the user page | |

## Error handling (30 seconds)
| Step | Do | Expect | Screenshot |
|---|---|---|---|
| 10 | Run `docker stop itd-mongo-1`, then sign in or click a session | a clear message such as "The database is not reachable. Start MongoDB and try again." with Try again | 9 |
| 11 | Run `docker start itd-mongo-1`, wait 5 seconds, click Try again | the session loads again | |

## Behind the screen (1 minute)
- `python scripts\demo_api.py --user alice --password "<password>"`: every API call with its status code. **Screenshot 10.**
- `python -m itd.schema check` and `python scripts\demo_schema.py`: the database rules, and bad documents rejected. **Screenshots 11 and 12.**
- `python -m pytest -q` in `backend`: 27 passed, 1 skipped. **Screenshot 13.**

## Oct 25 submission pack: what each item points to
| Item | Where it is |
|---|---|
| Updated system architecture | `docs/ARCHITECTURE.md` (GitHub draws the diagram), plus the diagram from the chat |
| Database schema | `docs/DATABASE.md` (fields, relationships, rules, indexes), plus the diagram from the chat |
| Functional and non-functional requirements | `docs/REQUIREMENTS.md` |
| GitHub repository with meaningful commits | the repository's commit list: one commit per day of work |
| Screenshots and demonstration of two workflows | screenshots 1 to 13 above and this script |

## What to say about the limits
- The data is synthetic sample data in the CERT file layout, so its scores are not research results.
- The assistant answered offline from the stored evidence; the hosted language-model call has not been tested with a key.
- The real CERT r4.2 and SPEDIA files have not been run yet.
