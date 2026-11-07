# Feedback on Group7_Research_and_Methodology_Humanized-P1_NewTables.docx

Checked on 6 November 2026 against the earlier humanized file, the fix list and the code. Each fix below gives the exact text to find (it appears once in the file) and a short replacement in the same plain style.

## Good
- All 61 fixes from REPORT_FIX_LIST.md are in.
- The heading "8.1 Data in use" is back.
- The new Figures 1, 3, 4 and 5 are in. Figure 2 and the logo are unchanged.
- The tables keep their content and the black header row.

## 1. Text still describes the old figures (fix first)

- [ ] **1. 5.1, how to read Figure 1.** The new Figure 1 has no balls or sockets.
  Find: `The figure is a UML component diagram: a ball is a symbol for an interface that a component provides, and a socket is a symbol for a component that requires an interface.`
  Replace with: `The figure is a UML component diagram: each box with the small component icon is a component, the boxes with a tab are the tiers, and a dashed arrow shows that one component uses another.`

- [ ] **2. Figure 1 caption.**
  Find: `their components and the interfaces between them.`
  Replace with: `their components and how they use each other.`

- [ ] **3. 5.2, what Figure 3 shows.** The new Figure 3 has four processes and the administrator only once.
  Find: `Figure 3 expands that to eight processes that are grouped around one data store, MongoDB: P1 read logs, P2 build features and baselines, P3 score sessions, P4 explain and store results, P5 serve analysts, P6 answer questions, P7 show the dashboard and P8 administer the database. The administrator is drawn twice in Figure 3 (marked *) so that flow lines do not cross.`
  Replace with: `Figure 3 expands that to four processes that are grouped around one data store, MongoDB: P1 read logs and score sessions, P2 administer the database, P3 serve analysts and P4 answer questions.`

- [ ] **4. Figure 3 caption.**
  Find: `data-flow diagram: eight processes and the database.`
  Replace with: `data-flow diagram: four processes and the database.`

- [ ] **5. 5.2, process numbers.**
  Find: `Only the engine (P1 to P4) writes new results, baselines, models and runs. P8 can recover them from a backup and P5 only writes the access log.`
  Replace with: `Only the engine (P1) writes new results, baselines, models and runs. P2 can recover them from a backup and P3 only writes the access log.`

- [ ] **6. 6, the extend arrows.** The new Figure 4 has only UC4 extending UC3, because the user page also opens from the flagged list.
  Find: `UC4 and UC5 are extensions of UC3, where the analyst can ask the assistant to open a new session from the session page, or open a new session from the user page.`
  Replace with: `UC4 is an extension of UC3, since the assistant can only be asked from the session page. The user page (UC5) opens from the flagged list or from the session page, and another session can be opened from the user page.`

## 2. Meaning changed in the reworded tables

- [ ] **7. Requirements table, AC5.** This is the supervisor's point that a stand-in test is not a SPEDIA evaluation.
  Find: `and is not a SPEDIA test.`
  Replace with: `and is not a SPEDIA evaluation.`

- [ ] **8. Validation table, "API data" row.** The order was swapped, so 404, 503 and 500 no longer line up with their causes.
  Find: `MongoDB stopped or some other fault; unknown session, user or run.`
  Replace with: `Unknown session, user or run; MongoDB stopped or some other fault.`

- [ ] **9. Steps table, row 7.** The count is divided by the session length, which is taken as at least 15 minutes.
  Find: `The hourly rate is divided by at least 15 minutes.`
  Replace with: `The hourly rate uses a session length of at least 15 minutes.`

- [ ] **10. Validation table, missing column or wrong date.**
  Find: `The pandas error text will end the run.`
  Replace with: `The run ends with the pandas error text.`

- [ ] **11. Choices table, the assistant.** It works without a key but can also use one.
  Find: `The assistant is a read-only and key-less assistant.`
  Replace with: `The assistant is read-only and also works without a key.`

- [ ] **12. Test table, TC5.** Tests "assert"; "claimed" changes the meaning.
  Find: `That a baseline excludes the scored session is not claimed,`
  Replace with: `That a baseline excludes the scored session is not asserted,`

- [ ] **13. Requirements table, AC3.** As written it sounds done, but the status is Deferred.
  Find: `The hosted model is provided with a real API key.`
  Replace with: `The hosted model is tested with a real API key.`

- [ ] **14. Test table, TC6.**
  Find: `the saved baseline is maintained.`
  Replace with: `a later batch continues from the saved baseline.`

- [ ] **15. Requirements table, FR8 evidence.** It reads like an instruction.
  Find: `Use fake hosted replies for statement check (TC12).`
  Replace with: `Statement check tested with fake hosted replies (TC12).`

- [ ] **16. Requirements table, FR4.**
  Find: `save their setting.`
  Replace with: `save their settings.`

- [ ] **17. Choices table, LSTM.**
  Find: `Event sequences are required for an LSTM (S11) that session counts do not keep.`
  Replace with: `An LSTM (S11) needs event sequences, which session counts do not keep.`

## 3. Cover page

- [ ] **18. The date is missing.** Add the line "November 2026" under "Dr. Deepa Suresh", as before.

## 4. Layout (from the Google Docs export; do these by hand)

- [ ] **19. Space in table cells.** Every table cell has 10 pt of space above and below its text, so all tables are about twice as tall. Select each table and set the space before and after to 0 (Format > Line and paragraph spacing).
- [ ] **20. Space between paragraphs.** Body paragraphs have 10 pt above and 10 pt below, which leaves about 20 pt between paragraphs. Set the space before to 0 and keep about 6 to 10 pt after.
- [ ] **21. ID column.** The ID column of the requirements and use-case tables is about 0.43 in wide, so FR10 to FR13 and UC10 to UC12 may break onto two lines in Word. Drag that column a little wider.
- [ ] **22. Picture descriptions.** The alternative text of all pictures was lost in the export. Optional: add it back (right-click a picture > Alt text).

Also noticed, no action needed: the export left two small technical errors in the file (a margin setting and one line-spacing value). Word opens such files without trouble.

Not checked: the real Word page count, and the AI score.
