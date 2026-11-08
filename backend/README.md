# Aloe backend

FastAPI service backed by PostgreSQL. First increment: a modular
market-data service (MDS) with a mock source, persisted to Postgres.

## Setup

```bash
# 1. Start Postgres
docker compose up -d db

# 2. Install dependencies (uses uv)
uv sync

# 3. Apply migrations
uv run alembic upgrade head

# 4. Seed mock market data
uv run python -m app.seed

# 5. Run the API
uv run uvicorn app.main:app --reload
```

Open http://localhost:8000/docs for the OpenAPI UI.

## Environment

Configuration is read from the environment (optionally a local `.env`).
See `.env.example` for the available variables.
