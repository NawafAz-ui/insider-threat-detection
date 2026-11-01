@AGENTS.md

## Claude Code notes
- Everything about the project (architecture, commands, database, API, known gaps, course context) is in `AGENTS.md`, imported above. Keep it as the single source; edit it there, not here.
- The Python environment is `backend/.venv` (Python 3.14). `pytest` and `python -m itd...` run from `backend/`; `npm` commands run from `frontend/`.
- Before saying a change works, run `pytest -q` (backend) and `npm run build` (frontend). MongoDB is not needed for the tests; start the container (`docker start insider-threat-detection-mongo-1`) only for `itd.schema`, the demo scripts and `check_connection.py`, and stop it again afterwards.
- Leave these working-tree files alone unless asked: the local edit to `docs/ARCHITECTURE.md` and the untracked `LOCAL_RUN_MANUAL.pdf`, `docs/LOCAL_RUN_MANUAL.html`, `docs/LOCAL_RUN_MANUAL.pdf`.
- Do not commit or push without being asked. Weekly supervisor tasks go on a local branch (this week: `november-1-tasks-fahim`).
- The submission document is `Group7_Research_and_Methodology.docx` (repo root, untracked): the team's Word file with the Week 3 material merged in as new sections 12, 13, 21 and 22 plus small edits (the original copy is still in `~/Downloads`). `docs/METHODOLOGY.md`, `docs/USE_CASES.md` and `docs/WEEK3_PLAN.md` are the Markdown sources. Older standalone Word builds (`docs/Week3_Submission_Days_1_2_7.docx`, `~/Downloads/Week3_Submission_Fahim/`) are superseded and still contain day numbers. If you change the content, update the Word file and tell the user instead of leaving it stale.
- Never write "Day 1", "Day 7" or similar in files meant for the supervisor; use the official task names or section headings.
