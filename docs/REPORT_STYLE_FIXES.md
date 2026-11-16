# Style fixes to the added text (09.11.2026 version)

Applied to `Research & Methodology - Group 7 - 09.11.2026 Version.docx` on 9 November 2026, after the review in `docs/REPORT_STYLE_REVIEW.md`. Only added (highlighted) text changed: no word of the 06.11.2026 version was removed, and 8 of its words came back. 18 items were applied as proposed, 3 were reworked so that only added words change, and 2 were dropped because they needed your words. The report is 35 words longer than before this pass (10,159 to 10,194 words, tables included). No semicolons or dashes were added.

## 1. Section 5.1, key to Figure 1

Why: same sentence frame as the figure keys in 5.2 and 6.

Status: dropped, because the fix needed your 06.11 words. The text stays as it was.

- Text: The figure is a UML component diagram: each box with the small component icon is a component, the boxes with a tab are the tiers, and a dashed arrow shows that one component uses another.

## 2. Section 5.1, batch flow

Why: one 55-word sentence; only ", and the engine" becomes ". The engine".

Status: reworked so that your words and sentences stay as they are.

- Before: the administrator can start the engine from the command line or request a run from the dashboard, and the engine will check the folder, read the CSV logs and write
- After: the administrator can start the engine from the command line or the dashboard, which will check the folder, read the CSV logs and write

## 3. Section 5.2, Figure 3

Why: list after a colon.

Status: dropped, because the fix needed your 06.11 words. The text stays as it was.

- Text: Figure 3 expands that to four processes that are grouped around one data store, MongoDB: P1 read logs and score sessions, P2 administer the database, P3 serve analysts and P4 answer questions.

## 4. Section 7, workflow

Why: the longest sentence in the report (about 70 words).

Status: reworked so that your words and sentences stay as they are.

- Before: First is a batch flow that the administrator runs from the command line or through a dashboard request, which checks the folder (0), stops on an input error and otherwise loads the CSV files (1),
- After: First is a batch flow that the administrator runs from the command line or the dashboard, which loads the CSV files (1), [your words unchanged] adds the explanations (6) and stores the results (7). The input check (0) comes before step 1 and stops the batch flow on any error.

## 5. Section 8.1, data sources

Why: opening topic sentence, two lists after colons, and Section 10.1 points to an "input manifest (Section 8.1)" that 8.1 never names.

Status: applied.

- Before: Each source is obtained in a different way. The generated data comes from the repository's own script. CERT r4.2 is taken from the KiltHub release [D1]: the logon, device, email, file and http files are copied into one folder, answers.csv is built only from the release's own answer files (scripts/build_answers.py), and the release name, file hashes, row counts and time range are recorded. SPEDIA is taken from Zenodo [D2] as one CSV file and converted to the CERT layout with a checked column mapping (itd.spedia). Every source must meet the same input requirements: five event files with id, date, user and pc columns, dates in the format MM/DD/YYYY HH:MM:SS and event ids that are unique across files.
- After: The generated data comes from the repository's own script. CERT r4.2 is taken from the KiltHub release [D1]. Its logon, device, email, file and http files are copied into one folder, and answers.csv is built only from the release's own answer files (scripts/build_answers.py). The release name, file hashes, row counts and time range are recorded in an input manifest. SPEDIA is taken from Zenodo [D2] as one CSV file and converted to the CERT layout with a checked column mapping (itd.spedia). All three sources must meet the same input requirements. There must be five event files with id, date, user and pc columns, every date must have the format MM/DD/YYYY HH:MM:SS, and every event id must be unique across the files.

## 6. Section 8.2, table of steps, row 0 (Validate)

Why: rules V4 to V7, V9 and V10 are never explained.

Status: applied.

- Before: Errors stop the run: a missing file or column, a wrong date format or an answers file without an id column (V1 to V3, V8). Other problems, such as empty or duplicate ids, are reported as warnings (V4 to V7, V9, V10).
- After: A missing file or column, a wrong date format or an answers file without an id column stops the run (rules V1 to V3 and V8). Empty id, user or pc fields, repeated event ids, unknown activity values, email sizes or attachment counts that are not numbers, labels that match no event and a missing or empty answers file are reported as warnings (rules V4 to V7, V9 and V10).

## 7. Section 8.2, missing checks

Why: change-log words "now" and "still"; the second sentence goes back to your wording without "silently".

Status: applied.

- Before: The engine now warns about duplicate event ids (V5) but still accepts them, and it does not test for duplicate rows, time zones, orphan logoffs, file hashes or the time range of a release. If the email size or attachment count is not numeric, it is still set to 0, now with a warning (V7).
- After: The engine warns about duplicate event ids (V5) but accepts them, and it does not test for duplicate rows, time zones, logoffs without a logon, file hashes or the time range of a release. If the email size or attachment count is not numeric, it will be set to 0 with a warning (V7).

## 8. Section 5.3, table of components, rules.py

Why: "comparison F" is used before 10.1 defines it, and the report calls A to E experiments.

Status: applied.

- Before: They are the reference methods of comparison F.
- After: Experiment F (Section 10.1) compares the models with them.

## 9. Section 9.3, table of choices, reference methods

Why: same as above.

Status: applied.

- Before: Shows whether the models beat rules an analyst could write (comparison F).
- After: Shows whether the models beat rules an analyst could write (experiment F, Section 10.1).

## 10. Section 10.1, list of experiments

Why: your wording back ("Five experiments will be conducted"), with only Five changed to Six.

Status: applied.

- Before: Six comparisons are made: A compares
- After: Six experiments will be conducted: A compares

## 11. Section 10.1, criteria of experiment F

Why: long list in one sentence.

Status: applied.

- Before: Comparison F uses F1 with precision and recall on the same test part, average precision and false alarms per 1,000 benign sessions over the five data sets. A method counts as better only when its lowest F1 is above the other's highest.
- After: Experiment F uses the same test part and the same five data sets as A to D. It reports F1 with precision and recall, average precision and false alarms per 1,000 benign sessions. A method counts as better only when its lowest F1 is above the highest F1 of the other method.

## 12. Section 10.2, second computer

Why: clause inside a clause, then a list after a colon.

Status: applied.

- Before: On a second computer, where comparison F was run, only the values that depend on XGBoost changed: 0.94 instead of 0.98 for XGBoost and 0.91 instead of 0.95 for the combined score.
- After: Experiment F was run on a second computer, where A to D were repeated. Only the results that depend on XGBoost differed. XGBoost reached 0.94 instead of 0.98, and the combined score 0.91 instead of 0.95.

## 13. Section 10.2, result of experiment F

Why: one 45-word sentence with a list inside.

Status: applied.

- Before: In comparison F the combined score reached a mean F1 of 0.91 (0.82 to 1.00) against 0.49 (0.38 to 0.61) for the best rule, after hours with a removable device or leak site, and 0.03 for the no-skill line, so it beat every rule.
- After: In experiment F the combined score reached a mean F1 of 0.91 (0.82 to 1.00). The best rule, after hours with a removable device or leak site, reached 0.49 (0.38 to 0.61), and the no-skill line 0.03. The combined score therefore beat every rule.

## 14. Section 10.4, opening paragraph

Why: list after a colon.

Status: applied.

- Before: The functional test cases follow the use cases through the running prototype: the API, the worker and the dashboard on a real MongoDB server with the generated data. The observed outcomes were recorded on 9 November 2026, and all twelve cases behaved as expected.
- After: The functional test cases follow the use cases through the running prototype. The API, the worker and the dashboard were used with a real MongoDB server that holds the generated data. The observed outcomes were recorded on 9 November 2026. All twelve cases behaved as expected.

## 15. Section 11, run requests

Why: list after a colon, "still", and "only" twice in one sentence.

Status: applied.

- Before: With the run requests the API still cannot write results, baselines or models: only an administrator can request a run, only for a folder name inside the data folder, and the worker performs it under the engine database account. The run report escapes all database values and contains no scripts, and requests and downloads are logged.
- After: Run requests do not let the API write results, baselines or models. Only an administrator can request a run, the request must name a folder inside the data folder, and the worker performs the run under the engine database account. The run report escapes all database values and contains no scripts. Every run request and report download is logged.

## 16. Section 12.1, test results

Why: "after the merge of" describes a change the reader never saw; the sentence goes back to your shape.

Status: applied.

- Before: On 7 November 2026, after the merge of the input validation, the run requests and the reference methods, pytest -q
- After: On 7 November 2026, pytest -q

## 17. Section 12.1, functional tests

Why: one 50-word sentence and "again".

Status: applied.

- Before: Issue 13 was partly fixed on 5 November 2026 (Section 12.2), and on 9 November 2026 the twelve functional test cases of Section 10.4 passed on a real MongoDB server, including a dashboard run with new models that again gave 7,329 sessions, 70 flagged and threshold 8.2.
- After: Issue 13 was partly fixed on 5 November 2026 (Section 12.2). On 9 November 2026 the twelve functional test cases of Section 10.4 passed on a real MongoDB server. One of them was a dashboard run that trained new models and gave the same 7,329 sessions, 70 flagged and threshold 8.2.

## 18. Section 12.1, table of issues, row 13

Why: "still".

Status: applied.

- Before: and a crash midway still leaves a mix until the next complete run.
- After: and a crash midway can leave a mix until the next complete run.

## 19. Section 12.1, limits of run requests

Why: list after a colon.

Status: applied.

- Before: The run requests add limits: a request waits until a worker is running, only one worker is assumed, two requests sent at the same moment can both queue, and the dashboard polls for the status instead of receiving updates. The duplicate-id check needs an estimated 0.3 GB of memory for CERT r4.2, which has not been measured.
- After: Run requests have some limits. A request waits until a worker is running, and the design assumes a single worker. Two requests sent at the same moment can both be queued. The dashboard asks for the run status at fixed intervals instead of receiving updates. For CERT r4.2, the duplicate-id check is estimated to need about 0.3 GB of memory.

## 20. Section 12.2, opening paragraph

Why: the date of the issue 13 fix is given three times.

Status: applied.

- Before: It is not in place at this time. Issue 13 was partly fixed on 5 November 2026.
- After: It is not in place at this time.

## 21. Section 12.2, issue 13

Why: change-log words "Since" and "still" (twice).

Status: applied.

- Before: Since 5 November 2026 the results with the same session ids are replaced block by block, the results of older runs are deleted only after all new ones are saved, and the dashboard shows a failed run. A crash midway can still leave a mix of old and new results until the next complete run, and the baselines are still replaced as a whole.
- After: With the partial fix of 5 November 2026, results with the same session ids are replaced block by block, the results of older runs are deleted only after all new ones are saved, and the dashboard shows a failed run. A crash midway can leave a mix of old and new results until the next complete run, and the baselines are replaced as a whole.

## 22. Section 13, objectives table, O7

Why: same naming as 10.1.

Status: applied.

- Before: with comparison F against simple rules.
- After: with experiment F against simple rules.

## 23. Section 13, gap G3

Why: the new clause hangs after your closing limit; this puts the reference methods into your own list and gives you your ending back (touches your sentence).

Status: reworked so that your words and sentences stay as they are.

- Before: The split by time-ordered sessions, the validation thresholds and the five data sets address most of the issues of G3 (results are hard to compare and may be too optimistic), though each part of the test contains only 13 to 16 malicious sessions, and the simple reference methods give a floor to compare with.
- After: though each part of the test contains only 13 to 16 malicious sessions. The simple reference methods give a floor to compare with.

## Left as it is

- Your own sentences, including their colons, "X, not Y" contrasts and the limits at the end of paragraphs. These are for your humanizing pass.
- The new tables (use cases UC13 to UC15, test cases TC22 to TC25, functional tests FT1 to FT12), where short cells and codes are normal.
- The FR, NF and AC sentence in Section 4, which you asked for.
