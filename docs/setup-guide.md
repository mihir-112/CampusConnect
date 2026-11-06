# Setup guide (Windows PowerShell)

You need **Python 3.12+** (the `py` launcher) and **Node.js 20+** with npm. Check:
```powershell
py --version
node --version
npm --version
```

## 1. Get the code
```powershell
git clone <your-repository-url> CampusConnect
cd CampusConnect
```

## 2. Backend (FastAPI)
```powershell
py -m venv venv
venv\Scripts\Activate.ps1
```
If PowerShell refuses to run the script, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` once in this window, then activate again.
```powershell
py -m pip install -r backend\requirements-dev.txt
```

Create the first publisher (you will be asked for a password of 8+ characters):
```powershell
py -m backend.cli create-publisher
```

Start the API:
```powershell
py -m uvicorn backend.main:app --reload --port 8000
```
Check it: open <http://127.0.0.1:8000/docs>. The database file is created in `instance\` automatically.

Optional: set your own signing key so logins survive a server restart.
```powershell
$env:SECRET_KEY = py -c "import secrets; print(secrets.token_urlsafe(48))"
```

## 3. Frontend (React, in a second PowerShell window)
```powershell
cd CampusConnect\frontend
npm install
npm run dev
```
Open <http://localhost:5173>. Publisher login is at <http://localhost:5173/publisher/login>. The dev server forwards `/api` requests to port 8000.

## 4. Run the tests
Backend and integration tests (from the project folder, venv active):
```powershell
py -m pytest
```
Frontend tests:
```powershell
cd frontend
npm test
```
Production build of the React app:
```powershell
npm run build
```

## Troubleshooting
| Problem | Fix |
|---|---|
| `py` is not recognised | Reinstall Python and tick "Install launcher for all users" |
| Login fails with 401 right after restarting the server | No `SECRET_KEY` was set, so old tokens are invalid. Log in again |
| Browser shows "We couldn't load announcements" | The API is not running on port 8000 |
| Port already in use | Close the other program, or use `--port 8001` and change `proxy` in `frontend\vite.config.js` |
| Start again with empty data | Stop the server and delete the `instance` folder |
