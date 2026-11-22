# linkly

A tiny URL shortener used as a demo starter repo.

**Stack:** FastAPI · SQLAlchemy 2 · SQLite · Alembic · pytest — managed with [uv](https://docs.astral.sh/uv/).

## What already works

| Method | Path            | Description                                   |
| ------ | --------------- | --------------------------------------------- |
| POST   | `/links`        | Create a short code for a URL (`201`)         |
| GET    | `/{code}`       | Redirect to the target URL (`307`)            |
| GET    | `/links/{code}` | Return the link as JSON (`200`, or `404`)     |

There are 3 passing tests in `tests/test_links.py`.

## Project layout

```
linkly/
  db.py         # engine, session, declarative Base, get_db dependency
  models.py     # Link model
  schemas.py    # Pydantic request/response models
  main.py       # FastAPI app and routes
migrations/     # Alembic environment + versions
tests/          # pytest suite (in-memory SQLite)
alembic.ini
pyproject.toml
```

## Run it

Requires `uv` (Python 3.14 is installed automatically by uv if missing).

```bash
uv sync                                  # create .venv and install deps
uv run alembic upgrade head              # create linkly.db with the links table
uv run uvicorn linkly.main:app --reload  # http://127.0.0.1:8000  (docs at /docs)
uv run pytest                            # 3 passed
```

The database URL defaults to `sqlite:///./linkly.db`; override it with the `DATABASE_URL` environment variable.

### Try it with curl

```bash
curl -s -X POST localhost:8000/links \
  -H 'Content-Type: application/json' \
  -d '{"url": "https://fastapi.tiangolo.com"}'
# {"code":"g8nPPw","target_url":"https://fastapi.tiangolo.com/","created_at":"..."}

curl -i localhost:8000/g8nPPw        # HTTP/1.1 307 Temporary Redirect, location: https://fastapi.tiangolo.com/
curl -s localhost:8000/links/g8nPPw  # the link as JSON
```

## Back to the starting point

The initial commit is tagged `starter`. To reset the demo:

```bash
git checkout starter          # look at the starting state
git switch -c my-demo starter # or start a fresh branch from it
```

## Replicate this repo from scratch

These are the exact commands used to build the starter:

```bash
# 1. Scaffold the project with uv
uv init linkly && cd linkly
rm main.py

# 2. Dependencies
uv add fastapi "uvicorn[standard]" "sqlalchemy>=2" alembic pydantic
uv add --dev pytest httpx2   # httpx2: what Starlette's TestClient now expects

# 3. Write the code: linkly/{__init__,db,models,schemas,main}.py and tests/{conftest,test_links}.py

# 4. pytest config (append to pyproject.toml)
cat >> pyproject.toml <<'EOF'

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
EOF

# 5. Alembic
uv run alembic init migrations
#   - migrations/env.py: import linkly.models, set target_metadata = Base.metadata,
#     and config.set_main_option("sqlalchemy.url", DATABASE_URL)
#   - alembic.ini: leave sqlalchemy.url empty (env.py sets it)
uv run alembic revision --autogenerate -m "create links table"
uv run alembic upgrade head

# 6. Verify
uv run pytest

# 7. Ignore the local DB, commit and tag
echo '*.db' >> .gitignore
git init
git add -A
git commit -m "linkly starter"
git tag starter
```
