# Publisher Auth and security

**Branch:** `feature/publisher-auth`

## What I built
| Area | Files |
|---|---|
| Models | `features/publisher-auth/backend/models/publisher.py`, `revoked_token.py` |
| Passwords | `backend/security/passwords.py`: Argon2, plus verification and upgrade of old Flask hashes |
| Tokens | `backend/security/tokens.py`: JWT creation and checking |
| Dependencies | `backend/security/dependencies.py`: `get_current_publisher`, `get_optional_publisher` |
| Brute-force protection | `backend/security/throttle.py` |
| Service and routes | `services/auth_service.py`, `routes/auth.py` (`/api/auth/login`, `logout`, `me`) |
| Command line | `backend/cli.py`: `py -m backend.cli create-publisher` |
| Frontend | `features/publisher-auth/frontend/`: `AuthContext`, `tokenStorage`, `LoginPage`, `ProtectedRoute` |
| Tests | `features/publisher-auth/tests/test_auth.py`, `auth.test.jsx` |

## Completed tasks
- [x] Login, logout, current-user endpoints
- [x] Argon2 hashing; old Flask scrypt/PBKDF2 hashes still log in and are upgraded
- [x] JWT with expiry, unique id and required claims
- [x] Logout really ends the session (token id stored as revoked)
- [x] Lock after 5 failed attempts for 5 minutes
- [x] Same message for unknown user and wrong password
- [x] CORS limited to configured origins
- [x] Login page, protected navigation, automatic return to login when a session ends
- [x] Security documentation and tests

## How it connects to the others
Every protected endpoint uses my dependency. The React API client reads my `tokenStorage` and tells `AuthContext` when a token stops working.

Documentation: [security.md](documentation/security.md).

## Git history and pull requests
Fill this in from your real GitHub history. Leave a row empty rather than invent one.

| Commit or PR | What it contains | Link |
|---|---|---|
| | | |
| | | |
