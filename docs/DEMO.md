# Day 7: first end-to-end workflow demonstration

Workflow shown: **logs in -> sessions -> features -> risk score -> explanation -> database -> API -> dashboard -> analyst question.**

## A. Clean start (2 minutes)
1. Docker Desktop is running.
2. From the project root: `.\start_all.ps1` (or start the API and dashboard by hand as in the README).
3. In `backend` with the virtual environment active:
   ```powershell
   python scripts\check_connection.py --user alice --password "<password>"
   ```
   Every line should say OK and the last line "Everything is connected."  **Screenshot 1.**

## B. Run the pipeline live (1 minute, optional but impressive)
```powershell
python scripts\generate_synthetic_cert.py data\cert_synthetic
python -m itd.engine --data data\cert_synthetic --retrain
```
The engine prints the five steps, the run time, the model weights, the threshold and a precision / recall / F1 / PR-AUC table.  **Screenshot 2.**
Refresh the dashboard afterwards: the list now shows the new run.

## C. Dashboard walkthrough (3 minutes)
| Step | Do | Say | Screenshot |
|---|---|---|---|
| 1 | Open `http://localhost:5173`, enter a wrong password | Errors are shown, and 5 failures pause sign-in | 3 (login with error) |
| 2 | Sign in as `alice` | Token-based login, expires in 30 minutes | |
| 3 | Look at the flagged list | Highest risk first; levels never shown as "safe"; summary cards show flagged / scored / threshold | 4 (list with cards) |
| 4 | Click the top (High) session | Score ring, S1 to S3 drivers, B1 to B3 baseline differences, "a flag is not proof" notice | 5 (detail, High) |
| 5 | Ask the assistant "Why was this flagged?" | It only sees the stored evidence; answer names the tags it used | 6 (chat with tags) |
| 6 | Go back, open the lowest (Borderline) session | Weaker evidence, drivers marked minor | 7 (detail, Borderline) |

## D. Show the other tiers (2 minutes)
- API: `http://127.0.0.1:8000/docs` **Screenshot 8**, or `python scripts\demo_api.py --user alice --password "<password>"` **Screenshot 9**.
- Database: `python scripts\demo_db.py` (collections, CRUD, access log) **Screenshot 10**.

## E. Expected results
- Wrong password -> error; right password -> list. 
- The list is sorted by risk, and its first row is the highest score.
- Session detail shows a score, up to 3 S items and up to 3 B items.
- The chat answer lists evidence tags (R, S1 to S3, B1 to B3).
- The access log contains your login, the sessions you opened and your question.
- Exact counts and scores differ slightly between runs of the data generator.

## F. If something fails
`check_connection.py` names the first broken link and the command to fix it.
The assistant answers from a local template unless `LLM_API_KEY` is set; say so if asked.
