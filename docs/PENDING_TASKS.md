# Pending tasks (internal working list, not for the supervisor)

Saved 7 November 2026 on branch `november-1-tasks-fahim`. Covers the 8 November
submission table (Days 1 to 7, research column and prototype column) plus housekeeping.
Tick a line when done.

## Status on 9 November 2026, after building on the 06.11.2026 version

- **Code:** every prototype row of the task table is done. A live functional run on 9 November passed all 12 cases, including a run with Train new models started from the dashboard (7,329 sessions, 70 flagged, threshold 8.2).
- **Report:** `Research & Methodology - Group 7 - 09.11.2026 Version.docx` is now built on `Research & Methodology - Group 7 - 06.11.2026 Version.docx` and covers every research row and submission item, including the functional test cases with expected and observed outcomes (Section 10.4) and the five redrawn figures. All changes: `docs/REPORT_CHANGE_LOG_NEXT_VERSION.md` (95.4% of the 06.11 words unchanged). A style pass on 9 November changed only the added text (`docs/REPORT_STYLE_FIXES.md`).

Still to do:
1. Owner: humanize the yellow text, then remove the highlights and run Word Compare against the 06.11.2026 version.
2. Owner: review the five redrawn figures.
3. Commit and push the branch, then merge into main.

Optional: evidence PDFs for Days 4, 6 and 7 like Nawaf's (group decision); the steps table in `docs/METHODOLOGY.md` still lacks step 0; the optional code items further down.

## Compared with main on 9 November 2026

Main (`be195a9`) has Nawaf's Days 1 to 3 and Day 5, with an evidence PDF for each of those days. Our branch has all of main plus the local work in part B, which is not on main yet.

| Day | Research and methodology | Prototype development |
|---|---|---|
| 1 | Done on main (`docs/DAY1_REVIEW.md`, Day 1 PDF) | Done on main |
| 2 | Done on main (Day 2 PDF) | Done on main |
| 3 | Done on main (Day 3 PDF) | Done on main |
| 4 | Open: no new test cases on main; locally TC22 to TC25, still without expected and observed outcomes (A1) | Done on main (live run in the Day 3 PDF); our 7 November re-check on the real MongoDB is local |
| 5 | Done on main (Day 5 PDF) | Done on main |
| 6 | On main in pieces (`docs/SECURITY.md`, limits in the PDFs); the local report gathers the new risks | Done on main: 74 tests pass (7 November); a written table of observed outcomes is A1 |
| 7 | Local only: report text updated (126 highlighted changes); A2 and A3 open | Local only: `docs/DEMO.md` Workflow 0, screenshots 14 to 17 |

| Submission item | Status |
|---|---|
| Updated methodology with detailed implementation steps | Local report only; A2 and A3 open |
| Data collection or preparation plan and preprocessing documentation | On main (Day 2 PDF, `docs/DATA_RULES.md`, `docs/CSV_LAYOUT.md`) |
| Fully integrated core system modules | On main |
| Functional test cases with expected and observed outcomes | Open (A1) |
| Initial testing results and documented technical issues | Test runs in the PDFs on main; issue list updated in the local report |
| Updated source code, screenshots and prototype demonstration | Code on main; demonstration and screenshots 14 to 17 local |
| Milestone: input, processing, storage and output end to end | Shown live on main (Day 3 PDF, 6 November) and locally (7 November) |

### A. Still to do
1. [done 9 Nov, Section 10.4] Test cases with expected and observed outcomes. Both report versions list each test only as "what it checks" and "Passed". Add expected and observed outcome columns, and add the end-to-end workflow steps as functional cases.
2. [done 9 Nov] Figures 1, 3, 4 and 5: add the worker, run requests and the validation step.
3. Owner: humanize the highlighted text, remove the highlights, then run Word Compare against the Humanized file.
4. Days 4, 6 and 7 have no evidence PDF. Nawaf made one each for Days 1, 2, 3 and 5. The group should decide whether these days need one too.
5. [done 9 Nov] Run "Train new models" once from the dashboard. It has never been run live.
6. [DATAFLOW.md done 9 Nov] Small wording fixes: `docs/DATAFLOW.md` said P5 writes only the access log, and the steps table in `docs/METHODOLOGY.md` has no validation step and no dashboard run.

### Code items found on 9 November (optional; no row of the task table needs them)
1. `test_sessionization_rules` passes with or without the 12-hour cap, because its assertion ends in `or end <= 22:00`. Asserting the end at 21:00 would make the cap tested; then update the cap status in the report.
2. No test covers file counts, the saved feature order, or the `login_ok` and `session_viewed` log entries.
3. The offline assistant never declines. A question that matches nothing, such as "Is this person a thief?", gets the standard summary. Only the hosted mode uses the "does not support an answer" reply.
4. `POST /api/run` saves the request before it writes the access log. If the log write fails, the admin sees error 500, but the worker still runs the request.
5. The dashboard has no automated tests.

### B. Done here, not on main yet
The new report version, the Humanized version (commit bf10648, not pushed), `docs/DEMO.md` Workflow 0 and screenshots 14 to 17, the documentation fixes and the lock file in UTF-8. They reach main only after a commit, a push and a merge. Leave out the old Word lock file `~$oup7_Research_and_Methodology.docx` (from 6 November; Word is not running).

### Watch
- The milestone asks for "input submission". The dashboard picks a dataset folder that is already on the server; it cannot upload files.
- Run numbers differ between documents: threshold 19.3 in the Day 3 PDF, 8.1 in the Steps 1 to 3 summary, 8.2 in `docs/DEMO.md`. The report should quote one run and say which.

The lists below are the earlier working list of 7 and 8 November.

## Dev work first

1. [x] Day 7 prototype: record one end-to-end demo. Admin starts a run from the
   dashboard, the worker finishes it, an analyst reviews a flagged session, asks the
   assistant, opens the user page. Update `docs/DEMO.md` and add screenshots.
2. [x] Day 4 prototype: test the full chain on a real MongoDB (`ITD_TEST_MONGO`), with
   a live worker and the dashboard in a browser.
3. [x] Run `python -m itd.schema apply` on the main database. The old rules reject the
   `run_requested` action, `log_access` has no error handling, so `POST /api/run`
   returns 500.
4. [x] Fix "API writes only the access log" in `AGENTS.md` (including its working rule),
   `docs/USE_CASES.md` and `docs/METHODOLOGY.md`.
5. [x] Test count 42 to 63 in `AGENTS.md`, `docs/DEMO.md` and `docs/DAY1_REVIEW.md`.
6. [x] Re-save `backend/requirements.lock.txt` as UTF-8 (currently UTF-16).
7. [x] Merge `origin/main` into this branch (done 7, 8 and 9 November: f4d36f5, 2dc1ad4, 51d8df0, the last one adds the Steps 1 to 3 summary PDF; comparison with `day1-3-tasks` in `docs/TASKS_VS_DAY1-3_BRANCH.md`). On 7 November it gained Days 1 to 3
   (d599a5a: validate.py, jobs.py, worker.py, run endpoints, RunControl.jsx,
   run_requests) and Day 5 (ebbee07: rules.py, report.py, comparison F, run report
   in RunPanel, tests). Dry-run merge was clean. Items 1 to 6 need that code here.

## Report work after that

The full change list for the report is `docs/REPORT_CHANGES_NEXT_VERSION.md` (8 November 2026). On 8 November the next version was built as `Group7_Research_and_Methodology.docx` with every change highlighted in yellow; `docs/REPORT_CHANGE_LOG_NEXT_VERSION.md` lists all 126 changes with their place. Still open for the report: the figures (group C) and the owner's humanizing pass over the highlighted text. The previous version stays untouched as `Group7_Research_and_Methodology_Humanized.docx`; the next version is saved as a new file.

8. [~] Day 7 research (text done 8 November, highlighted in the new file; figures still pending): review the code against the methodology and update the report
   for the new features (dashboard runs, admin-only endpoints, worker, `run_requests`):
   text, use-case table, Figures 1, 3, 4 and 5.
9. [x] Day 4 research: test cases with expected results for the 21 new tests
   (rules V1 to V10, run requests).
10. [x] Day 2 research: dataset sources (CERT r4.2, SPEDIA), how the data is obtained.
11. [x] Day 6 research: new risks. The worker must be running, only one worker is
    assumed, simultaneous requests can both queue, a crash midway leaves mixed results.
12. [x] Day 5: reference methods and run report now on main (ebbee07); reference
    them in the submission.
13. [-] Obsolete (the P1_NewTables file was deleted on purpose on 7 November). Apply `docs/FEEDBACK_P1_NEWTABLES.md` (17 find and replace pairs, 4 layout
    steps) to `Group7_Research_and_Methodology_Humanized-P1_NewTables.docx`.
14. [x] Choose the final report file name (project notes expect
    `Group7_Research_and_Methodology.docx`).

Open for Capstone B, not this list: real CERT r4.2 and SPEDIA runs, HTTPS in a browser,
the hosted assistant with a real key.
