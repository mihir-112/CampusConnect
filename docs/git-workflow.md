# Git workflow for the team

Branches: Mihir `feature/core-announcement-engine`, Aariz `feature/publisher-auth`,
Nayeem `feature/notice-details`, Moksh `feature/student-dashboard`, Mridul `feature/search-notifications`.

## Mihir (once): create the repository
```powershell
cd CampusConnect
git init -b main
git add .
git commit -m "Initial architecture: app structure, models, shared interfaces"
git remote add origin https://github.com/<mihir-username>/CampusConnect.git
git push -u origin main
```
On GitHub: Settings > Collaborators > add Aariz, Nayeem, Moksh, Mridul.
Settings > Branches > protect `main` (require a pull request and the CI check).

## Everyone: get the code and your branch
```powershell
git clone https://github.com/<mihir-username>/CampusConnect.git
cd CampusConnect
git checkout -b feature/<your-branch-name>     # use your name from the list above
python -m venv venv ; venv\Scripts\activate ; pip install -r requirements.txt
```

## Daily loop
```powershell
git pull origin main              # bring in teammates' merged work
# ...edit only the files you own (see the README table)...
python -m pytest                  # must pass before you push
git add <your files>
git commit -m "Short message saying what and why"
git push -u origin feature/<your-branch-name>
```

## Pull request
1. On GitHub choose **Compare & pull request**, base `main`, compare your branch.
2. Write what you built, which tests cover it, and what other modules it touches.
3. Request a review from a teammate (suggested: Mihir reviews Aariz, Aariz reviews Nayeem, Nayeem reviews Moksh, Moksh reviews Mridul, Mridul reviews Mihir).
4. Fix requested changes by committing to the same branch; the PR updates itself.
5. After approval and a green CI check, click **Merge**. Then everyone runs `git pull origin main`.

## If two people changed the same file
```powershell
git checkout feature/<your-branch-name>
git pull origin main              # Git marks conflicts with <<<<<<< ======= >>>>>>>
# edit the file to keep the right lines, remove the markers
git add <file> ; git commit ; python -m pytest ; git push
```
Avoid conflicts: edit only your own files, and tell the owner if you need a change in theirs.

## Record your own work
Use GitHub Issues for tasks, keep commits small, and save genuine screenshots in `members/<you>/evidence/`.
Never commit `instance/`, `venv/` or `.env`.
