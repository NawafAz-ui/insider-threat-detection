# Is the yellow right? Humanized_FixedbyClaude compared with the 06.11.2026 version

This file checks whether the yellow in `Research_Methodology_Group7_09.11.2026_Humanized_FixedbyClaude.docx` marks exactly the words that differ from `Research & Methodology - Group 7 - 06.11.2026 Version.docx`.

## Status (9 November 2026, saved into the file)

At the owner's request the yellow now marks whole sentences only, not single words.

- A sentence is yellow when more than half of its words are new or changed compared with the 06.11 version. This covers new sentences, new table rows and sentences that were rewritten as a whole. 197 sentences are yellow.
- A sentence with only a few changed words stays plain, for example "six" becoming "seven collections" in 5.3 or the new test numbers in 12.1. 99 sentences are like this. Word Compare against the 06.11 file shows these small changes.
- Left plain on purpose, as before: the three changed figure captions and the header row of the new table in 10.4 (white text on black).
- Sentences that were only moved, such as the SHAP sentence in the Section 13 gap paragraph, count as changed and are yellow.
- Only the highlighting changed: the text and all other formatting are the same (checked character by character). A copy of the file before this step is kept in the scratchpad backups.

## Places where words of the 06.11 version were only removed (no yellow possible)

| Section | Where | Removed words |
|---|---|---|
| 3. Literature and research gap | paragraph | the years |
| 4. Requirements and acceptance status | table row 'FR8' | for statement check |
| 4. Requirements and acceptance status | table row 'NF4' | checks |
| 4. Requirements and acceptance status | table row 'AC1' | The |
| 5.1 Architecture | paragraph | the interfaces between them. |
| 5.2 Data flow | paragraph | using the Gane-Sarson notation: |
| 5.2 Data flow | paragraph | the |
| 5.2 Data flow | paragraph | the |
| 5.2 Data flow | paragraph | expands that |
| 5.2 Data flow | paragraph | baselines, P3 |
| 5.2 Data flow | paragraph | eight |
| 7. Workflow and processing stages | paragraph | the |
| 7. Workflow and processing stages | paragraph | workflow in |
| 7. Workflow and processing stages | paragraph | stages: |
| 8.2 Preprocessing, outputs and validatio | paragraph | silently |
| 9.3 Choices and tools | table row 'Imbalance and split' | S12, |
| 9.3 Choices and tools | table row 'Personal baseline' | lose |
| 9.3 Choices and tools | table row 'Explanation and assistant' | a |
| 9.3 Choices and tools | table row 'Explanation and assistant' | a |
| 9.3 Choices and tools | table row 'Explanation and assistant' | a |
| 9.3 Choices and tools | table row 'Explanation and assistant' | together |
| 9.3 Choices and tools | paragraph | contain |
| 10.2 Indicators and results | table row 'API response time' | repeated |
| 11. Explanations, assistant, security an | paragraph | on |
| 12.1 Where the prototype stands | paragraph | at commit ac8afa9, |
| 13. Review against objectives and gaps | table row 'O6 Evidence-grounded assi' | mechanically |
| 13. Review against objectives and gaps | paragraph | the user page displays the end-of-batch baseline. The split by time-ordered sessions, the  |

Method: both files were turned into words in document order (paragraphs and table cells), and the words were aligned with Python's difflib. A word is yellow when it is new or changed compared with the 06.11 version, and the space between two yellow words is yellow too. Short common words such as "the" can line up by chance inside rewritten sentences, so a few of them stay plain inside a yellow sentence.
