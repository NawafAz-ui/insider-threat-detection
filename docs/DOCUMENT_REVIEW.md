# Check of Group7_Research_and_Methodology.docx (1 November 2026)

For the owner of the file, not for the supervisor. Everything below was read from the Word file and compared with the code, the tests and the local database.

## 1. What was checked
- Every cross-reference to a section number, figure and table.
- Every test name and code file named in the document (all exist in the repository).
- Numbers: 33 test functions in the file (32 pass, 1 skipped), 40 build modules, 7,329 results, 66 flagged, 2 runs, threshold.
- Facts about the code: flags of `itd.engine` and `backup_db.py`, 500 default and 2,000 limit of the user history, the question length limit.
- Figures 2 and 3 against the text of Sections 12 and 13.
- Banned wording: no "Day 1" style wording, no em-dashes, no placeholders, no repeated paragraphs.

## 2. Problems found and fixed (text only, layout untouched)
| # | Where | Problem | Fix |
|---|---|---|---|
| 1 | Section 12, paragraph under Figure 2 | Said UC2, UC3, UC5 and UC6 need a token; UC4 also needs one. It also described links that the figure does not draw. | Now "UC2 to UC6 need the token it returns" and says the figure shows who uses each use case, not the links. |
| 2 | Section 13, closing paragraph | Said the planned experiments are in Sections 16 to 18; the resource experiment is in Section 19. | "Sections 16 to 19". |
| 3 | Section 13, stage 10 | "no user or PC names are sent" is too strong: Section 18 says the analyst's free-text question is also sent and may hold an identifier. | "no user or PC names are put in the evidence". |
| 4 | Section 19, last paragraph of the security part | Said the real-server schema test was skipped "in this update", but Section 21 records that it ran and passed. | Dated it to the 27 October check and pointed to Section 21. |
| 5 | Section 11, secure configuration paragraph | "this update did not repeat them because MongoDB was unavailable" has the same problem. | "the 27 October 2026 check ...". |
| 6 | Section 20 table | Rows called "Fresh pytest run" and "Fresh Vite build" show 27 tests, but Section 21 shows a later run with 32. | Renamed with the date, 27 October 2026. |
| 7 | Section 20 table, committed API demo | The committed demo file says threshold 19.3. The stored runs in the database say 19.54. Section 21 says 19.5. | Added "as written there; the stored run shows 19.5". |
| 8 | Section 23 heading | "23." had a dot; every other heading has none. | "23". |

Checks after the fixes: the Word validity check passed, and only `word/document.xml` changed. A copy of the file before these fixes is in the scratchpad (`check/before_fixes.docx`).

## 3. Left as it is (your decision)
- **Repeated issue list.** The same open problems (no calibration, no statement check of hosted answers, single-model thresholds on test labels, two day-level features, baseline replay) appear in Section 13 (closing paragraph), Section 20 (evidence limits), Section 21 (issue table), Section 22 (objectives and inconsistencies table) and Section 23 (priorities). Section 21 is the full list. The others could shrink to one sentence and a reference. Not done, because it changes the team's pages.
- **Design science steps** appear in Section 11 (one paragraph) and Section 13 (table). The table adds the project mapping, so it is not wasted, but the Section 11 paragraph could point to it.
- **Test counts** appear in the executive overview, Sections 20 and 21. They now differ on purpose (27 on 27 October, 32 after the update) and each one is dated.
- **Two headings numbered 10 and two numbered 20** ("continued" pages). This comes from the team's original file. Renaming them "10 (continued)" would be tidier.
- **Section 10 text** mentions repository IDs FR-11, FR-12, NFR-8 and NFR-9, while this document uses FR10 to FR13. The paragraph says they are different ID sets; it is original wording.
- **Repository file `docs/screenshots/10-demo-api-results.md`** says threshold 19.3; the database says 19.54. I did not edit that file.

## 4. Not checked
- Real Word page breaks. The new tables are long, so Section 21 and Section 23 may flow to an extra page. Open the file in Word and scroll once.
- The numbers in the Section 21 test record (for example 37 access-log entries) are as recorded on 31 October; I re-checked only the 7,329 results, 66 flagged, 2 runs and the threshold.
- No result on real CERT r4.2 or SPEDIA exists, and none is claimed.

## 5. Sections and what each one has
**Title page, Executive overview, Document guide.** Names and ID numbers, a short summary of the project, the 20 studies, the repository status and the later update, and a one-paragraph guide to the sections.

**1 Research scope and questions.** The problem and the unit of analysis (a session), target behaviors, research questions RQ1 to RQ5 with evidence needed, scope and expected contribution.

**2 Literature search and selection method.** Type of review, sources, search strings Q1 to Q7, inclusion and exclusion rules.

**3 Screening record and evidence quality.** 20 retained studies (16 empirical, 4 reviews), counts by publisher, retrieval and verification log, appraisal rules, date notes.

**4 Evidence extraction, studies S1 to S5.** One table: objective and method, data, limitation and what it means for the project. Short interpretation.

**5 Evidence extraction, studies S6 to S10.** Same table layout, plus interpretation on graph and temporal work.

**6 Evidence extraction, studies S11 to S15.** Same layout, interpretation on representation, ranking and usefulness to an analyst.

**7 Evidence extraction, studies S16 to S20.** Same layout, ensemble caution, rule against comparing percentages across studies.

**8 Critical synthesis and research gap.** Themes, four design lessons (sessions, imbalance, validation, explanation), the bounded research gap and the proposed contribution.

**9 Existing applications and project positioning.** Table of five commercial products (Microsoft Purview, Splunk, Exabeam, Securonix, Proofpoint), why the prototype is smaller, design choices.

**10 System requirements and acceptance evidence** (and "10 Operational requirements continued"). FR1 to FR13 and NF1 to NF5 with acceptance evidence, traceability to RQ1 to RQ5, schema deployment, user-history limits, run provenance.

**11 Research design and system architecture.** Design science approach, three tiers and two workflows (Figure 1), data ownership, secure database configuration.

**12 Use cases, roles and access control (new).** Three actors, use-case diagram (Figure 2), seven analyst use cases UC1 to UC7, five administrator use cases UC8 to UC12, access table by role and endpoint, notes on logging and other controls.

**13 Overall workflow and processing stages (new).** Design science steps mapped to the project, workflow diagram (Figure 3), ten-stage table (input and rule, output, code and test), list of method gaps.

**14 Data provenance and session construction.** Generated data and later benchmarks, CSV input contract, session rules, audit points.

**15 Behavioral features and personal baselines.** 39 features by group, the ten baseline metrics and the deviation formula, temporal correctness, feature assumptions.

**16 Model training and calibrated risk.** Settings of the three models, 70/15/15 time split, the current risk score, the target calibration procedure.

**17 Detection evaluation and comparisons.** Core protocol, metrics and uncertainty, five planned matched experiments A to E, SPEDIA transfer.

**18 Explanations and assistant evaluation.** What SHAP explains, evidence bundle, target statement check, planned 30-question experiment and two-reviewer labeling.

**19 Security and computational evaluation.** Security acceptance steps, TLS and database checks, resource and speed experiment, privacy and ethics.

**20 Repository evidence and proposal alignment** (and "20 Operational evidence continued"). Test and build results of 27 October, fixture metrics, table of proposal element against evidence, committed demo records, evidence limits.

**21 Prototype status, remaining core modules and test record (new).** Status by component, changes made in this update, 11 issues with type, priority, plan and status, test record of 31 October.

**22 Review against project objectives and research gaps (new).** Objectives O1 to O7 with evidence and limit, gaps G1 to G5, inconsistencies between project documents, limits to state in every report.

**23 Deliverables and remaining evaluation work.** Work-plan coverage table, implementation priorities, threats to validity, and a second coverage table for the prototype and review activities (new).

**References.** S1 to S10; S11 to S20; methodological and dataset references M1 to M6, D1, D2 and project sources P1, P2, R1; vendor sources V1 to V5 with the verification record and the research record boundary.
