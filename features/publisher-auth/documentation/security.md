# Security notes

## Login flow
1. React posts `{username, password}` to `/api/auth/login`.
2. The server checks the Argon2 hash. On success it returns a JWT valid for `ACCESS_TOKEN_MINUTES` (default 120).
3. React keeps the token in `sessionStorage` and sends `Authorization: Bearer <token>` with every request.
4. `POST /api/auth/logout` stores the token's id in `revoked_tokens`; later requests with that token get 401.

## Decisions
| Topic | Decision | Reason |
|---|---|---|
| Password storage | Argon2 via `argon2-cffi` | Slow on purpose, salted, current best practice |
| Old passwords | Werkzeug hashes verified, then re-hashed on login | Migrated publishers keep working |
| Token | JWT HS256, claims `sub`, `jti`, `iat`, `exp`; `exp`, `sub`, `jti` required | Expiry cannot be skipped by a forged token |
| Secret key | From `SECRET_KEY`; if missing, random per run with a warning | Nothing secret in source code |
| Token storage | `sessionStorage` | Lasts one tab session; not sent automatically to any site |
| CSRF | Not needed | CSRF attacks rely on cookies the browser sends by itself. We use an `Authorization` header, which another site cannot make the browser add |
| XSS | React escapes all text; no `dangerouslySetInnerHTML` is used | A stored token can be stolen by injected scripts, so we avoid injection |
| CORS | Only `CORS_ORIGINS` (default: the Vite dev server); only needed methods and headers | Other sites cannot call the API from a browser |
| Brute force | 5 failures per username in 5 minutes gives 429 | Slows guessing; resets on restart |
| Username probing | Identical 401 message for unknown user and wrong password | Do not reveal which usernames exist |
| Authorisation | Always on the server (`get_owned`), never only in React | Hiding a button is not security |
| Uploads | Extension, size and file signature checked; random names; outside any public folder | See notice-details's file notes |

## Known limits (be honest in the presentation)
- The login throttle is in memory and per server process.
- Tokens cannot be revoked by an admin except by changing `SECRET_KEY`, which ends every session.
- Serve the application over HTTPS when deployed beyond a local network.
