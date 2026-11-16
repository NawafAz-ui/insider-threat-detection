# Research and Methodology report compared with the literature review

This file checks where the report (`Research_Methodology_Group7_09.11.2026_Humanized_FixedbyClaude.docx`, as saved at 20:04 on 9 November 2026) uses the literature review (`Literature_Review_Group7-Updated2.docx`), and whether the two agree. The 09.11.2026 version has the same text in these places. Status, 9 November 2026: fixes 1 to 4 were applied to the humanized file, without the humanizer step, at the owner's decision. The gap labels were taken word for word from the review. Fix 5 was not applied: the report's "Muñoz, A. M." matches the publisher's record (Crossref lists the family name Muñoz and the given names Alberto Mateo), so it is the literature review that differs. The optional points were not applied.

## Short answer

Mostly yes. The facts the report takes from the studies match the review: S1 found XGBoost best for sessions, S5 works per day, S8 per event, S7 uses session graphs, S11 is an LSTM on event sequences, S19 uses unsupervised ensembles, and the datasets and the three models are described the same way. The reference details for S1 to S20 also match. Five places do not match, because the review was updated after the report was written: it now has 27 studies and a new gap table.

## Places that do not match

| # | Where in the report | Report says | Literature review says | Suggested change (keeps your wording where possible) |
|---|---|---|---|---|
| 1 | 3, first paragraph | 20 studies kept (S1 to S20), 4 reviews or concept papers (S9, S10, S15, S18), 16 with experiments | 27 included studies: S1 to S9, S11 to S14, S16 to S20, plus C1, C2, C6 and O1 to O6. S10 is background, S15 is excluded. The reviews among them are S9, S18, C1 and C6 | "During the literature review, 27 studies published between 2021 and 2026 were kept, 18 of the 20 studies of the first search (S1 to S9, S11 to S14 and S16 to S20) and 9 found later, which are listed in the literature review report. S10 and S15 are used only as background." Keep your next sentence about the search strings, and add "They are in the literature review report." |
| 2 | 13, gap paragraph | G1 alerts not explained, G2 sessions against a personal baseline, G3 results hard to compare, G4 little testing beyond CERT, G5 models far from analyst tools | Gap 1 per-session detection against the user's own behaviour, gap 2 only synthetic CERT data, gap 3 unfair testing, gap 4 alerts not explained, gap 5 few studies compare supervised and unsupervised models | Use the review's order and its gap 5. Proposed paragraph below. |
| 3 | 9.3, row "Imbalance and split", column "Why" | "Held-out data is not changed and no future information is used (S16, S20)." | S20 is named for a random split and S16 for synthetic attack samples (review 10.3), so they are examples of the problem, not support for the choice | "Held-out data is not changed and no future information is used, unlike the synthetic samples in S16 and the random split in S20." |
| 4 | 9.3, same row, column "Not chosen" | "Oversampling (SMOTE, S2, S12, S16) alters the training data." | S12's best method was undersampling (NearMiss-2), not oversampling | "Resampling alters the training data (oversampling in S2 and S16, undersampling in S12)." |
| 5 | References, S1 | "Muñoz, A. M., ..." | "Mateo-Muñoz, A., ..." (the same author appears as "Mateo-Muñoz, A." in O6) | Use one spelling in both documents. Check it on the publisher page first. |

## Proposed gap paragraph for Section 13 (fix 2)

This keeps your sentences and both of your semicolons, changes the gap labels to the review's, and adds one sentence for the review's gap 5:

"Of the gaps identified in the literature review, the session unit and the ten deviation features cover most of G1 (few studies score single sessions and compare them with the user's own normal behaviour); there are still some cases where some sessions overlap (issue 14); and the user page displays the end-of-batch baseline. G2 (most studies use only the synthetic CERT data) is not closed: only a stand-in file has been used, and SPEDIA contains events derived from CERT. The split by time-ordered sessions, the validation thresholds and the five data sets address most of the issues of G3 (testing is often not fair, so results are hard to compare and may be too optimistic), though each part of the test contains only 13 to 16 malicious sessions. The simple reference methods give a floor to compare with. G4 (few studies explain why an alert happened) is addressed with the SHAP and baseline reasons in plain words, but these have not been tested for their usefulness. G5 (few studies compare supervised and unsupervised models on the same data) is addressed by comparing Logistic Regression, XGBoost and Isolation Forest on the same sessions (objective O3). The dashboard, the user page, the assistant and the run report bring the models closer to the tools analysts use, as a prototype without an analyst study."

## Optional

- **Research question names.** The review's RQ1 to RQ3 are review questions, and the report's RQ1 to RQ5 are the project's questions. A reader of both documents sees two different RQ1s. One sentence in Section 2 would fix it: "RQ1 to RQ5 are the project's research questions, separate from the three questions of the literature review."
- **New studies the report could cite.** C1 says results across CERT studies are hard to compare (gap G3), and C6 says there is no standard way to judge explanations (gap G4). Their references would need to be added. Do not cite the review's O-studies in the report under their own names: the report already uses O1 to O7 for its objectives.
- **Future work in Section 3.** The list of sequence and graph models left for later (S3 to S8, S11, S14) could also name C2, which uses graphs and a Bi-LSTM.

Not checked: whether either document's reference details match the publisher pages, beyond comparing the two documents with each other.
