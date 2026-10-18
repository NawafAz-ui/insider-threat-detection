# Start database, API and dashboard (Windows PowerShell). Run from the project root:  .\start_all.ps1
# Needs: Docker Desktop running, backend\.venv created, frontend\node_modules installed (see README).
$root = $PSScriptRoot
docker compose up -d
if (-not $env:JWT_SECRET) { $env:JWT_SECRET = [guid]::NewGuid().ToString("N") + [guid]::NewGuid().ToString("N") }
$secret = $env:JWT_SECRET
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
  "cd '$root\backend'; .\.venv\Scripts\Activate.ps1; `$env:JWT_SECRET='$secret'; python -m itd.serve"
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
  "cd '$root\frontend'; npm run dev"
Write-Host "Started. Dashboard: http://localhost:5173   API docs: http://127.0.0.1:8000/docs"
Write-Host "Check the connections:  cd backend; python scripts\check_connection.py --user alice --password <password>"
