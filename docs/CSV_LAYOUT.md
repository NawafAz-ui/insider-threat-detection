# CSV layout (based on CERT r4.2)

Put these files in one folder and pass it to `python -m itd.engine --data <folder>`.
Dates are `MM/DD/YYYY HH:MM:SS`. Extra columns are ignored.

| File | Columns used |
|---|---|
| `logon.csv` | id, date, user, pc, activity (`Logon` / `Logoff`) |
| `device.csv` | id, date, user, pc, activity (`Connect` / `Disconnect`) |
| `email.csv` | id, date, user, pc, to, size, attachments |
| `file.csv` | id, date, user, pc, filename |
| `http.csv` | id, date, user, pc, url |
| `answers.csv` (optional) | activity_type, id: ids of malicious events; a session is malicious if it contains one |

Build `answers.csv` from the CERT answer files: `python scripts/build_answers.py <answers-folder> <dataset-folder>`.
Sample data in this layout: `python scripts/generate_synthetic_cert.py data/cert_synthetic`.

SPEDIA is a single CSV: convert it with `python -m itd.spedia` (see `spedia_mapping.example.json`).
