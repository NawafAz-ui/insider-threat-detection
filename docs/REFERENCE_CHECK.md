# Reference check: Research and Methodology report

This file checks the 29 references of `Research_Methodology_Group7_09.11.2026_Humanized_FixedbyClaude.docx` (S1 to S20, M1 to M7, D1 and D2) against the official records, on 9 November 2026. Use it to see which references are confirmed and which small details are still missing.

## Short answer

All 29 references are real. None was invented: every DOI resolves to a record whose title, authors and year match the report. Journals, volumes, issues and pages also match. Two article numbers are missing, and five references shorten their author lists to "et al.". Every reference in the list is cited in the text, and every citation in the text is in the list.

## How it was checked

- 27 DOIs were looked up in the official registries: Crossref for journal and conference papers, and DataCite for the two datasets.
- M7 (arXiv) was checked through its arXiv DOI in DataCite.
- M4 (NeurIPS) was checked on the archived copy of the exact link (June 2026), because the NeurIPS site refused connections that day.
- D2's version was checked in the Zenodo record.
- S14's LNCS volume was checked through a search result that cites DBLP and Springer, because the Springer page needs a login.

## Results

| ID | Result | Note |
|---|---|---|
| S1 | Correct | Crossref gives the family name Muñoz and the given names Alberto Mateo, so "Muñoz, A. M." matches. The literature review writes "Mateo-Muñoz, A.". |
| S2 | Correct, incomplete | Article number 24715 is missing. 8 authors are shortened to "et al.". |
| S3 | Correct, incomplete | Article number 17 is missing. |
| S4 | Correct | 8 authors shortened to "et al.". |
| S5 | Correct | 8 authors shortened to "et al.". |
| S6 | Correct | |
| S7 | Correct | |
| S8 | Correct | 7 authors shortened to "et al.". |
| S9 | Correct | |
| S10 | Correct | |
| S11 | Correct | |
| S12 | Correct | Crossref stores the authors' initials as family names ("S, Asha"). "Asha, S." is the usual way these names are cited. |
| S13 | Correct | The year note "(2022 online; 2023 volume)" is accurate but not standard. The literature review writes 2023. |
| S14 | Correct | LNCS 13245 matches the listing for DASFAA 2022 Part I (ISBN 978-3-031-00122-2). |
| S15 | Correct | The year note "(2022 issue; 2021 online)" is accurate but not standard. |
| S16 | Correct | |
| S17 | Correct | |
| S18 | Correct | |
| S19 | Correct | |
| S20 | Correct | 4148441 is the publisher's article ID. |
| M1 | Correct | |
| M2 | Correct | |
| M3 | Correct | |
| M4 | Correct | The archived NeurIPS page shows Lundberg, Scott M. and Lee, Su-In, Advances in Neural Information Processing Systems 30, 2017. |
| M5 | Correct | |
| M6 | Correct | |
| M7 | Correct | arXiv 2211.14437: Bertrand, Tawbi and Desharnais, 2022. |
| D1 | Correct | The year note "(2020 repository release)" is accurate but not standard. |
| D2 | Correct | "version 2" is right: this DOI is the second of two Zenodo versions (27 May 2025). 6 creators are shortened to "et al.". |

## Suggested fixes (reference list only, no prose)

1. S2: add the article number: "Scientific Reports, 14, 24715."
2. S3: add the article number: "Cybersecurity, 8, 17."
3. Optional: list all authors instead of "et al." in S2, S4, S5, S8 and D2. APA lists up to 20 authors, and the literature review already lists them in full.
4. Optional: write single years, as the literature review does: S13 (2023), S15 (2022) and D1 (2020).

Not checked: whether each statement the report makes about a study is what the paper itself says. That needs the papers. The report's statements were compared with the literature review's summaries earlier (`docs/REPORT_VS_LITERATURE_REVIEW.md`).
