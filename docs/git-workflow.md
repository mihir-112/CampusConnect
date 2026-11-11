# Git and GitHub workflow

## Branches
| Branch | Owner |
|---|---|
| `main` | protected: merge only through a pull request with green CI |
| `feature/core-announcement-engine` | core-announcement-engine |
| `feature/publisher-auth` | publisher-auth |
| `feature/notice-details` | notice-details |
| `feature/student-dashboard` | student-dashboard |
| `feature/search-notifications` | search-notifications |

## One-time setup (team lead)
```powershell
git init
git add .
git commit -m "Add CampusConnect React and FastAPI project"
git branch -M main
git remote add origin <your-repository-url>
git push -u origin main
```
Then each member creates their branch:
```powershell
git checkout -b feature/<your-branch-name>
```
On GitHub: Settings > Branches > add a rule for `main` that requires a pull request and the **CI** checks (`Backend tests`, `Frontend tests and build`).

## Daily routine
```powershell
git checkout main; git pull
git checkout feature/<your-branch>; git merge main
# ... work only inside your own features/<feature-name>/ folder ...
py -m pytest features\<feature-name>       # your backend tests
cd frontend; npm test; cd ..               # frontend tests
git add features\<feature-name>
git commit -m "Short, specific message about what you changed"
git push -u origin feature/<your-branch>
```

## Pull requests
1. Open a pull request from your branch to `main`.
2. Describe what you built, which issue it closes, and paste the real test output.
3. Wait for CI to pass. Another member reviews and answers or fixes comments.
4. Merge. Everyone then pulls `main`.

## Rules
- Use GitHub Issues to split the work; each issue names one member and one folder.
- Changes to shared files (`backend/main.py`, `frontend/src/routes/AppRoutes.jsx`, `docs/api-documentation.md`) need a second member's review because they affect everyone.
- Commit only your own work. Do not create artificial commits or credit anyone for work they did not do; the history is part of your evaluation evidence.
- Never commit `.env`, `instance/`, `node_modules/` or `venv/` (already in `.gitignore`).

## Suggested issues (create these on GitHub)
core-announcement-engine: database and models; announcement CRUD; publish/unpublish; error format; dashboard and form pages.
publisher-auth: login API; JWT dependencies; logout and revocation; login throttle; login page and protected routes.
notice-details: upload endpoint; file validation; serve and download; detail page; PDF preview.
student-dashboard: layout and navigation; home page; cards and category tabs; states; responsive CSS; UI design document.
search-notifications: search endpoint; search bar; notification creation; bell and list; read state.
