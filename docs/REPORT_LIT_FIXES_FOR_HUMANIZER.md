# Literature fixes for the report: what to humanize and what not

Most of the new text below is copied from the group's own literature review (`Literature_Review_Group7-Updated2.docx`) or from your own report sentences, so it is already human-written. Only part B is new wording. Send part B to your humanizer, paste the result back in the chat, and Claude will insert everything into the report in yellow. The facts behind each fix are in `docs/REPORT_VS_LITERATURE_REVIEW.md`.

Status, 9 November 2026: parts A1 to A3 and both part B sentences were inserted as written, without the humanizer, because the owner judged two sentences too short to matter. A4 was not changed, because the report's spelling matches the publisher's record. The optional Section 2 sentence was not added.

## A. Your own words, inserted as they are

1. **Section 3, first paragraph.** Replace the first two sentences ("During the literature review, 20 studies ... and 16 report experiments.") with the review's own sentence, from its Section 5.5 and 5.6:
   > The review includes 27 studies published between 2021 and 2026: S1 to S9, S11 to S14 and S16 to S20 from the literature search, plus 9 new papers. S10 and S15 are used as background only.

   The 9 new papers are not named, because their IDs O1 to O6 would clash with the report's objectives O1 to O7.

2. **Section 13, gap labels.** The labels come word for word from the review's gap table. Only "behaviour" is changed to "behavior", the spelling the report uses.
   - G1: (few papers detect per session and compare it with the user's own normal behavior)
   - G2: (most papers use only the synthetic CERT dataset)
   - G3: (testing is often not fair)
   - G4: (few papers explain why an alert happened)
   - G5: (few papers compare supervised and unsupervised models together)

   Your sentences in that paragraph keep their words and both semicolons. They are only put in the review's order: G1 is now the session sentence, G2 the CERT sentence, G3 the time-split sentence and G4 the SHAP sentence.

3. **Section 9.3, row "Imbalance and split".** This uses the review's own phrases "fake attack samples" and "split the data randomly".
   - "Why" column: "Held-out data is not changed and no future information is used (S16, S20)." becomes "Held-out data is not changed and no future information is used. S16 uses fake attack samples and S20 splits the data randomly."
   - "Not chosen" column: "Oversampling (SMOTE, S2, S12, S16) alters the training data." becomes "Oversampling (SMOTE, S2, S16) and undersampling (S12) alter the training data."

4. **References, S1.** The first author is written the same way in both documents. Check the spelling on the publisher page first.

## B. Send these to the humanizer

Two sentences for Section 13, in this order, after the SHAP sentence:

> G5 (few papers compare supervised and unsupervised models together) is addressed by comparing Logistic Regression, XGBoost and Isolation Forest on the same data.
>
> The dashboard, the user page, the assistant and the run report are addressing the gap between research models and the tools analysts use, as a prototype without an analyst study.

The first sentence reuses the review's "What our project does" column. The second is your old G5 sentence without its label, because G5 now means a different gap.

Optional, for Section 2, after the RQ2 to RQ5 paragraph:

> RQ1 to RQ5 are the project's research questions and are separate from the three questions of the literature review.

## C. What Claude checks when you bring the text back

- The facts did not change: the gap labels G1 to G5, Logistic Regression, XGBoost and Isolation Forest, and "without an analyst study".
- Your humanized wording goes in unchanged, unless a fact is wrong. Then Claude tells you before changing it.
- Everything new is highlighted in yellow, as in the rest of the report.
