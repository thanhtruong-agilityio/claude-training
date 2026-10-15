# todo-app

Practice project for the Claude training exercises. Small on purpose: React + Vite + TS front end, FastAPI + SQLite back end.

## Run

```bash
# backend (http://localhost:8000, docs at /docs)
cd todo-app/backend
uv sync && uv run uvicorn app.main:app --reload

# frontend (http://localhost:5173, proxies /api -> :8000)
cd todo-app/frontend
npm install && npm run dev
```

## Test

```bash
cd todo-app/backend && uv run pytest
cd todo-app/frontend && npm test
```

## API

| Method | Path | Notes |
|---|---|---|
| GET | `/todos` | list |
| POST | `/todos` | `{title}` -> 201 |
| PATCH | `/todos/{id}` | `{title?, done?}` |
| DELETE | `/todos/{id}` | delete |

## Tickets

Practice tickets live in [../docs/tickets/](../docs/tickets/).
