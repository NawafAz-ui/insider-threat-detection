# Check of the humanized 09.11.2026 report

This file checks `Research_Methodology_Group7_09.11.2026_Humanized.docx`, which is not yet confirmed, against `Research & Methodology - Group 7 - 09.11.2026 Version.docx`. The humanized file was made from the latest 09.11 version, the one that already has the style fixes. Use this check to decide which spots to correct before you confirm it. Checked on 9 November 2026.

Update, 9 November 2026: at the owner's request the 12 meaning fixes below were applied to the humanized file itself, and the small slips were kept on purpose. Each fix is in yellow, and some sit inside text that was already yellow. Nothing else changed: 12 paragraphs or rows differ, the file is 7 words longer, and it still has 75 semicolons. The file before the fixes is kept in the scratchpad backups (`Humanized_before_12_fixes.docx`).

## Short answer

Most of the meaning is the same, with different words. 65 of the 301 paragraphs and table rows were reworded, and 95.4% of the words of the 09.11 version are still there. The section structure, the five figures and their picture descriptions, the tables, and all numbers, codes and statuses (Met, Partially Met, Deferred) are unchanged. 12 of the rewordings change the meaning or make a sentence wrong. They are listed below, each with the smallest fix to the humanized words.

## Meaning changes to fix

| # | Where | Humanized text | Problem | Smallest fix |
|---|---|---|---|---|
| 1 | 10.3, TC6 | "If data is rerun later, it will not be double counted, but rather will continue from the saved baseline." | It mixes two checks into one wrong statement. A re-run of the same data rebuilds the baseline. A later batch of new data is what continues from the saved baseline. | "If data is rerun later, it will not be double counted, and a later batch will continue from the saved baseline." |
| 2 | 2, after RQ5 | "There is literature to support the design decisions, but there is no evidence that the combination of these is better than simpler ones" | The old text said only that the literature does not show it. "There is no evidence" is a much stronger claim. | "...but it does not show that the combination of these is better than simpler ones" |
| 3 | 5.1 | "the REST API, which include security controls and the assistant" | "include" now refers to all four parts of the tier. Only the REST API holds the security controls and the assistant (Figure 1). | "the REST API, which includes the security controls and the assistant" |
| 4 | 7 | "The input check (0) is placed in front of step 1, and the batch flow is halted if an error occurs." | It no longer says that the input check is what stops the run. It reads as if any error anywhere stops the flow. | "The input check (0) is placed in front of step 1 and halts the batch flow if it finds an error." |
| 5 | 10.4, first paragraph | "A real MongoDB server was used with the API, the worker and the dashboard, containing the generated data." | It says the dashboard contains the data. The database does. | "A real MongoDB server containing the generated data was used with the API, the worker and the dashboard." |
| 6 | 10.4, FT9 | "A second run when another one is running" | A second request is refused (409) while another run is waiting or running, not only while it runs. | "A second run when another one is waiting or running" |
| 7 | 11 | "The session page will show the top 3 positive XGBoost SHAP contributions" | Future tense for something the page already does. | "The session page shows the top 3..." |
| 8 | 13, O2 | "they are still listed in the order of their start time" | "listed" sounds like the order on screen. Issue 14 is about the order in which sessions are added to the baseline. | "they are still processed in the order of their start time" |
| 9 | 5.3, api.py | "and admin-only dataset list, run request)" | The "and" is gone, so the run request no longer reads as admin-only. | "and the admin-only dataset list and run request)" |
| 10 | 10.2, API response time | "for repeated requests to a live MongoDB server that were authenticated" | "that were authenticated" now points to the server. | "for repeated authenticated requests to a live MongoDB server" |
| 11 | 4, FR5 | "the code fits on the validation data" | It no longer says what is fitted (the weights, the threshold and the calibration). | "the code fits them on the validation data" |
| 12 | 10.3, TC7 | "If the hash of a saved model is not the same" | It does not say what the hash is compared with. | "If the hash of a saved model no longer matches the stored hash" |

## Small wording slips (meaning kept, optional)

- 7: "the 3 models". In 10.4, FT4 says "3 model scores, up to 3 reasons" in the expected column, while the observed column says "three". The report writes "three" everywhere else.
- 8.1: "The data generated is from the repository's own script" reads oddly. "The generated data comes from the repository's own script."
- 8.2, row 0: "The folder is scanned" can sound like a virus scan. "checked" is the exact word.
- 10.1: "set in stone" became "fixed". The style review named "set in stone" as one of the phrases that sound like the group.
- 10.2: "The mean F1 score for the combined score" repeats "score".
- 12.1: "again gave the same" says the same thing twice.
- 13, O3: "scored well below the others (mean F1 0.75) against Logistic Regression" mixes two ways of comparing.
- 13, G5: "are addressing G5" reads oddly. "address G5."
- 9.3: "hand picked" lost its hyphen.

## Checks on your rules

- Semicolons: 10 of the 85 semicolons of the 06.11 version were removed (FR4 2, FR13 1, NF5 2, TC6 1, TC8 3, O6 1), and 75 remain. Your rule in CLAUDE.md says to keep the 85. No semicolons were added.
- Highlights: the new wording is not highlighted, and 13 paragraphs or rows lost part or all of their yellow (FR4, FR13, NF1, AC5, TC6, O3, O7, FT4, issue 13 in 12.1, and parts of 5.1, 7, 8.2 and the gap paragraph in 13). The yellow no longer shows every change against the 06.11 version. Word Compare against the 06.11 file is now the reliable way to see all changes.
- No "we" or "our", no week or day references, no dashes, no straight quotation marks. Contractions went from 24 to 26, including a new "doesn't" in TC5.
- The figures, picture descriptions, code-font text (51 runs) and table layout are unchanged. The file has no tracked changes and was saved by Word.

Method: both files were turned into text, compared paragraph by paragraph and word by word, and every changed paragraph was read by hand. Numbers, codes and words such as "not", "only", "all" and "Met" were compared automatically for each paragraph. Not checked: the page layout in Word.
