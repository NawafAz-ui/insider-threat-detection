# 8 November task table compared with branch `day1-3-tasks`

Internal working note, not for the supervisor. Checked 9 November 2026: `day1-3-tasks` is Nawaf's commit d599a5a (6 November); "our branch" is `november-1-tasks-fahim` at 51d8df0 plus the uncommitted work. Use it to see which rows that branch covers and what was added here.

**Short answer:** `day1-3-tasks` is already fully merged into our branch (through main); no commit is missing. It covers Days 1 to 3. Days 4 to 7 and all report work exist only here.

| Day | Column | Task | On `day1-3-tasks` | On our branch now |
|---|---|---|---|---|
| 1 | Research | Review methodology for missing technical details and implementation dependencies | Done: `docs/DAY1_REVIEW.md` (gaps M1 to M7) | Same; its check line now says 74 passed (uncommitted) |
| 1 | Prototype | Complete remaining essential frontend and backend components | Done: results replaced block by block, "scored" label, lock file saved as UTF-16 | Same code; lock file re-saved as UTF-8 (uncommitted) |
| 2 | Research | Document dataset sources, collection procedures or input-data requirements | Partly: input requirements and rules only; sources and collection steps only in the later Day 2 PDF | Done: two new paragraphs in report section 8.1 (highlighted) |
| 2 | Prototype | Implement data import, preprocessing and validation | Done: `validate.py`, rules V1 to V10, 9 tests | Same |
| 3 | Research | Describe data-processing steps, algorithm configuration and output generation | Partly in `docs/DATA_RULES.md` (step 0, split label); full text only in the later Day 3 PDF | Report: Validate step row and model settings sentence (highlighted) |
| 3 | Prototype | Integrate the main processing module with the system interface | Done: run requests, worker, Run analysis panel, three endpoints, 12 tests | Same; database rules applied on the main database (before that, Start run gave error 500) |
| 4 | Research | Prepare detailed functional test cases and expected results | No new test cases | Report: TC22 to TC25 (highlighted) |
| 4 | Prototype | Test integration between frontend, backend, database and processing module | Tests on the in-memory database, one full path through the engine | Full chain checked 7 November on the real MongoDB: 75 passed, live worker, dashboard in a browser |
| 5 | Research | Define baseline methods or comparison criteria | Not on this branch (it is on `day5-tasks`) | Merged: three simple rules, comparison F; report paragraphs (highlighted) |
| 5 | Prototype | Implement result storage, retrieval, visualization or report generation | Not on this branch (it is on `day5-tasks`) | Merged: run report and its download button, 11 tests, screenshot 17 |
| 6 | Research | Identify technical limitations, security considerations and risks | Partly: `docs/SECURITY.md` rows for run requests and validation | Report: security and limits paragraphs (highlighted) |
| 6 | Prototype | Conduct functional, input-validation and error-handling tests | 21 new tests; 63 passed, 1 skipped | 74 passed, 1 skipped (75 with the real MongoDB) |
| 7 | Research | Review implementation against the approved methodology | Not done | Report text updated (126 highlighted changes); Figures 1, 3, 4 and 5 still old |
| 7 | Prototype | Fix critical defects and demonstrate one complete end-to-end workflow | Not done | `docs/DEMO.md` Workflow 0, screenshots 14 to 17 |

## Differences on the files of that branch
- Nothing it added was undone. Later commits only added to its files: the run report endpoint and the `report_viewed` action (Day 5), and one unused import removed from `engine.py` (ac8afa9).
- Three uncommitted edits here: the lock file encoding, the `security.py` docstring (now names run requests), and the `DAY1_REVIEW.md` check line (the Day 1 PDF records 42 passed, the count on that day).

## Open on both branches
- "Train new models" from the dashboard was never run live, and the worker test runs with retrain off.
- Figures 1, 3, 4 and 5 do not show the worker or run requests yet.
- Real CERT r4.2 and SPEDIA have not been run.

## Watch out
- Do not switch to `day1-3-tasks` in this folder. It holds an old `Group7_Research_and_Methodology.docx` with the same name as the new report. Git refuses the switch; a forced switch would overwrite the new report. Read its files with `git show day1-3-tasks:<path>` instead.
- Nawaf's Steps 1 to 3 summary PDF (8 November) was merged here on 9 November (51d8df0); our branch now holds all of `origin/main`.
- Run numbers differ between computers: the Day 3 PDF shows 66 flagged at threshold 19.3, the Steps 1 to 3 summary shows threshold 8.1, and `docs/DEMO.md` shows 70 flagged at threshold 8.2. The report should quote one run and say which.
