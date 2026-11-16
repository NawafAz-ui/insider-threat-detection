# Style review: Research and Methodology report (09.11.2026 version)

> Written on 9 November 2026 by a subagent asked to read the report as a human capstone supervisor. It reviewed the 09.11.2026 version before three later fixes: every semicolon added in the new text was removed (the semicolon counts below are from before that; the new text now has none), "There are 4 missing checks" became "There are some missing checks" because the list after it is longer than four, and the straight quotation marks in the 10.4 table became curly ones. Later the same day, the points about the added text were fixed in that text only (`docs/REPORT_STYLE_FIXES.md`). The points about the group's own sentences are left for the humanizing pass.

A supervisor's reading of what makes the report sound AI-written. "New text" is the marked text, "group text" the students' reworded text. Counts are from a script unless marked as a hand count.

## Verdict

Yes, I would suspect AI help, though not from the vocabulary: the usual chatbot words ("delve", "robust", "moreover") are absent. The sentence shapes give it away: lists hung on colons, a limit closing about half the paragraphs, semicolons that tack on a second fact, and codes in place of words. The new text reads like a coding assistant's change notes ("now warns", "after the merge"), and the voice shifts mid-paragraph where it was inserted. The group's rewording made the words human, but the machine sentence frames survive.

## Patterns, strongest first

**1. Long sentences that hang a list on a colon (both, worst where new text was inserted).** A lead-in, a colon, then three to eight items.
- Count: 32 of 199 prose sentences (8 of 38 new, 22 of 144 group). Sentences that mix new and group words average 36 words (group: 23), the longest 68.
- Quote: (7) "First is a batch flow that the administrator runs ... checks the folder (0), stops on an input error..."
- Fix: split at the colon. Before: "The run requests add limits: a request waits until a worker is running, only one worker is assumed, ..." After: "The run requests have some limits. A request waits until a worker is running. Only one worker is assumed. ..."

**2. Change-log wording (new text).** It describes changes from a version the reader never saw.
- Count: 14 in new text (for example "now", "still", "again", "since", "after the merge"), almost none in group text.
- Quote: (12.1) "On 7 November 2026, after the merge of the input validation..."
- Fix: describe the system as it is. Before: "The engine now warns about duplicate event ids (V5) but still accepts them." After: "The engine warns about duplicate event ids (V5) but accepts them."

**3. Codes in place of words (mostly new text).** Labels carry the meaning. Rules V4 to V7, V9 and V10 are never explained one by one, and "comparison F" is used in 5.3 and 9.3 before 10.1 defines it. The new text also has no contractions and few "will"s (2, against 21 in group text), so it reads like a manual.
- Count: about 20 codes per 1,000 words of new prose, 4 in group prose (citations and section numbers not counted).
- Quotes: (8.2) "(V4 to V7, V9, V10)" / (5.3) "the reference methods of comparison F"
- Fix: words first, code in brackets. Before: "P2 can recover them from a backup and P3 only writes..." After: "The administration process (P2) can recover them from a backup, and the process that serves analysts (P3) only writes..."

**4. Semicolons, the group's question (mostly new text).** Honest view: a semicolon alone is not an AI sign. Formal reports use them, and some of the group's ("...not evidence of wrongdoing; and the system...") look human. The problem is how many the new text has and what they do.
- Count: 23.5 per 1,000 words in new text, 10.6 in group text (prose only: 10.4 and 4.8). One new sentence in five has one, one group sentence in ten. Of the 12 in new prose, 6 attach a limit to a finished sentence and 1 joins two unrelated facts.
- Quote: (10.2) "...for the combined score; the cause was not tested."
- Fix: in prose, use a full stop or "and", "but", "so". Short lists in table cells ("401; 401; 403") are fine. Before: "It is not in place at this time; issue 13 was partly fixed on 5 November 2026." After: "It is not in place yet. Issue 13 was partly fixed on 5 November 2026."

**5. A limit closing many paragraphs, and too much "only" (both, mostly group text).** The limits are honest, but ending so many paragraphs on one reads like a model's habit.
- Count: about 27 of 58 prose paragraphs end on what was not done or shown (hand count). "Only" (not "admin-only" or "read-only"): 8.4 per 1,000 words in new text, 5.1 in group text.
- Quote: (13) "None of them is a benchmark result."
- Fix: gather limits in one closing sentence per section, and use "only" once per sentence. Before: (11) "only an administrator can request a run, only for a folder name inside the data folder" After: "only an administrator can request a run, and the request must name a folder inside the data folder"

**6. "X, not Y" contrasts (group text).** About 12, 11 of them in group text. Keep the Section 1 flag sentence, which is needed.
- Quote: (8.1) "These are created records, not the original CERT release"
- Fix: state the point directly. Before: (2) "RQ2 to RQ5 are questions to be tested, not benefits already shown." After: "RQ2 to RQ5 are open questions that the evaluation still has to test."

**7. One figure-key sentence used three times (both).** "Figure N is a [notation]: symbol is meaning, symbol is meaning, and..." in 5.1 (new), 5.2 and 6. Fix: break it up. Before: "The figure is a UML component diagram: each box with the small component icon is a component, ..." After: "Figure 1 uses UML component notation. Boxes with the small component icon are components. ..."

**8. Straight quotation marks (new text).** The 10.4 table (FT1, FT5, FT12) uses straight marks. All 19 double quotation marks in group text are curly, as Word types them, so the straight ones look pasted. Fix: retype them in Word. Before: `"Wrong username or password"` After: `“Wrong username or password”`

## The ten most machine-like passages

1. 7: "First is a batch flow that the administrator runs..."
2. 12.1: "The run requests add limits: ..."
3. 11: "With the run requests the API still cannot write..."
4. 10.1: "Six comparisons are made..." and "Comparison F uses F1..."
5. 10.2: "On a second computer, where comparison F was run..."
6. 8.2: "The engine now warns about duplicate event ids (V5)..."
7. 8.1: "Each source is obtained in a different way..."
8. 12.2: "It is not in place at this time; issue 13..."
9. 12.1: "On 7 November 2026, after the merge of..."
10. 10.1: "It requires a checked mapping of the SPEDIA columns..." (group text: a colon, then three semicolons)

## What already sounds like the group (keep it)

- Plain sentences: (1) "Insider activity looks legitimate in the logs...", (5.3) "Dependencies only go one direction.", (9.2) "Seeds are fixed (42).", and the 10.2 results paragraph.
- Everyday phrasing and slips: (3) "They don't indicate...", (8.1) "It's enough to show...", (10.1) "set in stone", (11) "bogus answers", (6) "These are the 2 workflows for analysts." The new text has almost none of this, which is why it stands out.

Not a style point: 8.2 says "There are 4 missing checks" and then lists more than four.

## Punctuation counts (per 1,000 words)

| Text | Words | Semicolons | Colons | Parentheses |
|---|---|---|---|---|
| New text | 2,256 | 53 (23.5) | 19 (8.4) | 48 (21.3) |
| Group text, body | 6,869 | 73 (10.6) | 53 (7.7) | 154 (22.4) |
| Group text, with cover and references | 7,676 | 75 (9.8) | 91 (11.9) | 193 (25.1) |
| New text, prose only | 1,149 | 12 (10.4) | 11 (9.6) | 15 (13.1) |
| Group text, prose only | 3,713 | 18 (4.8) | 29 (7.8) | 68 (18.3) |

Method: markers removed, "|" and "##" ignored, a word is any token with a letter or digit, parentheses counted once per pair. Cover and references add 38 colons and 39 parentheses (links, years). Table cells: 37.4 semicolons per 1,000 words (new) against 18.0 (group). Only semicolons clearly differ, at about twice the rate in new text. Colons and parentheses are level, so the colon habit runs through the whole report.
