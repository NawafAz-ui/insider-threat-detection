# Evidence documents

One document per day of the capstone plan, plus a summary of the three student activities (Steps 1 to 3). Each one says what was done, how it was checked, and shows the screenshots.
All numbers come from generated CERT-layout data, so they are not research findings.

| File | Day or step | What it covers |
|---|---|---|
| Day1_Methodology_Review_and_Prototype.pdf | 1 | Methodology gaps and dependencies; engine fixes (safe result replacement, scored label); dependency lock file |
| Day2_Dataset_Sources_and_Validation.pdf | 2 | Dataset sources, collection steps, input requirements; the input validation rules V1 to V10; a rejected dataset |
| Day3_Processing_Steps_and_Run_Control.pdf | 3 | Processing steps, algorithm configuration, outputs; run requests, the worker and the Run analysis panel, shown live on MongoDB |
| Day5_Baselines_and_Run_Report.pdf | 5 | Baseline methods and comparison criteria (comparison F); the run table, the run report and its tests |
| Steps1to3_Summary.pdf | Steps 1 to 3 | The three student activities compared with the work and the evidence: environment, data and core processing, and the main feature proof of concept (session page, user history, assistant) |

To repeat the checks: `cd backend`, activate the virtual environment, then `python -m pytest -q` (74 passed, 1 skipped on 7 November 2026) and `python scripts/run_experiments.py --seeds 5`.
