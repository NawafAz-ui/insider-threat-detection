# Figures of the Research and Methodology document

All five figures were drawn on 6 November 2026 in a formal notation. Figures 1 and 3 were redrawn the same day, simpler, because the owner found them confusing. The files are in `docs/figures/`. The five figures wait for the owner's review.

| Figure | Section | Notation | Files |
|---|---|---|---|
| 1 System architecture | 5.1 | UML component diagram | `figure1-system-architecture.png`, `.svg` |
| 2 Context diagram | 5.2 | Data-flow diagram, level 0, Gane-Sarson | `figure2-context-diagram.png`, `.svg` |
| 3 Level-1 data-flow diagram | 5.2 | Data-flow diagram, level 1, Gane-Sarson, four processes | `figure3-level1-dfd.png`, `.svg` |
| 4 Use-case diagram | 6.1 | UML use-case diagram | `figure4-use-case-diagram.png`, `.svg` |
| 5 Overall workflow | 7 | UML activity diagram with two partitions | `figure5-activity-diagram.png`, `.svg` |

## Rules followed
- Figure 1: components with the component symbol, one package per tier, a dashed arrow for "uses" (the component at the tail uses the one at the head), a document symbol for the CSV files, an "external" component for the hosted model, a database symbol for MongoDB. No actors and no ball-and-socket interfaces: they made the first version hard to read.
- Figures 2 and 3: rectangle = external entity, rounded rectangle with an ID = process, open-ended box with an ID = data store, arrow = named data flow. The context diagram has one process and no data store. Every process has an input and an output, and no flow joins an entity or a store to another entity or store without a process. The flows crossing the boundary in Figure 3 are the ones in Figure 2. Figure 3 has four processes: P1 read logs and score sessions (batch engine), P2 administer the database, P3 serve analysts (dashboard and REST API), P4 answer questions (assistant).
- Figure 4: actors outside the system boundary, ovals for use cases, plain lines for associations, a dashed arrow from the extending use case to the base use case marked "extend". It shows no order of steps. Only UC4 extends UC3: the user page (UC5) also opens from the flagged list, so it extends nothing.
- Figure 5: two initial nodes (the analyst flow starts on its own, because the API is a separate process that runs independently of the batch run), actions, a datastore object node, a merge and a decision with guards (the analyst may ask any number of questions, or none), an activity final node, two partitions, open-arrowhead flows.

## Check against the code (6 November 2026)
An independent reviewer read the code and checked every element of the first versions. Figures 1 and 2: all right (Figure 1 label for the engine lacked the reads, now added). Figure 3: one label lacked the reads of the access log (now added); the eight-process version was replaced. Figure 4: one wrong «extend» (UC5, removed). Figure 5: the API was drawn as starting after the batch run and the assistant as one pass (both corrected); the ten stages show the logical order, while the code overlaps some of them (explanation and storage run block by block, and stages 3 and 4 read saved baselines and models unless the run retrains), which was left as it is. The "Administrator" actor works on the command line; an account with the role "admin" can also use the dashboard like an analyst, which Section 6 of the report states. Not checked: a live run, and the Word captions.

## How to redraw
- Figures 1 to 5: `node src/figN.mjs out.svg`, then `node src/svg2png.mjs out.svg out.png 3` (needs Node and Google Chrome). The shared shapes are in `src/dfdlib.mjs`; `src/fig1.mjs` draws its own package, component, document and database shapes.

`docs/figures/` also holds older diagrams from the long version (`context-diagram.png`, `data-flow-level1.png`, `database-diagram.png`, `sequence-diagram.png`). The report does not use them.

## Update of 9 November 2026
All five figures were redrawn for the code merged on 7 November: Figure 1 adds the run worker, eleven endpoints and the run_requests collection; Figure 2 adds the dashboard run request and the run status; Figure 3 adds the run request and run status between the administrator and P3, and run requests in the flows of D1; Figure 4 adds UC13 to UC15 and shows the administrator as a special kind of analyst (generalization); Figure 5 adds the input check (0) with a flow final node for input errors. They are in the next version of the report (`Research & Methodology - Group 7 - 09.11.2026 Version.docx`) with their alternative text, and await the owner's review.
