# Telegram Notifier Backend

Enterprise backend for telegram notifications built with FastAPI, PostgreSQL, and modern Python practices.

## Development

```bash
# Setup environment
uv venv
source .venv/bin/activate
uv sync

# Run only database in Docker
docker compose -f docker-compose.db.yml up -d
uv run python scripts/load_fixtures.py
uv run python -m app.main



# Run all in Docker
docker compose -f docker-compose.yml up -d
docker-compose exec app uv run python scripts/load_fixtures.py
```