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


# Подключаемся к PostgreSQL
docker-compose -f docker-compose.db.yml exec postgres psql -U app_user -d notifier_db

# В psql создаем тестовую БД
CREATE DATABASE test_db;
\q
uv run python scripts/setup_test_db.py
# Запуск всех BDD тестов
pytest tests/ -v
# Или с маркировкой BDD
pytest tests/ -m bdd -v

# Или конкретные step-файлы
pytest tests/steps/test_user_steps_async.py -v
pytest tests/steps/test_health_steps_async.py -v  
pytest tests/steps/test_resource_steps_async.py -v
```