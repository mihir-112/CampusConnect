# Backend architecture (beginner-friendly)

**Think of the backend as a restaurant.** The *route* is the waiter: it takes the order (the request) and brings back the dish (the response), nothing more. The *service* is the kitchen: it knows the rules (a title is required, only the owner can delete) and does the work. The *model* is the pantry: it describes what is stored in the database.

```text
HTTP request -> route -> service -> model -> SQLite
                  |          |
        Pydantic checks   emits events ("published")
        the input         -> other members' code reacts
```

## Decisions and why
| Decision | Why |
|---|---|
| `create_app(settings)` function | Tests build an app with a temporary database, so real data is never touched |
| One `Database` object per app, session per request | Simple, safe, and easy to explain |
| Pydantic validators hold the rules | One place for validation; the form on the React side only gives quicker feedback |
| Event hub (`backend/shared/events.py`) | The core says "this was published"; it does not need to know that notifications exist |
| One error format | The React client has one place that understands every error |
| Same table names as the Flask version | Existing data keeps working |
| `published_at` set once | Students see when it was first published; sorting stays stable if it is unpublished and published again |
| Publisher list is a separate endpoint | Public endpoints can never leak drafts by accident |

## Rules enforced here
Title 1 to 150 characters; description required; category one of four; link must be http(s); only the author can edit, publish, unpublish or delete; drafts are invisible to everyone but their author.

## Request example
`POST /api/announcements` with a token and `{"title": "...", "description": "...", "category": "Events", "is_published": true}`:
1. FastAPI checks the token (publisher-auth's dependency) and the body (my schema); problems become a 422 with field messages.
2. `announcement_service.create` saves the row and sets `published_at`.
3. It emits `announcement.published`; search-notifications's handler creates the notification.
4. The route returns the announcement as JSON (201).
