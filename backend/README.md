# backend

FastAPI-ядро AI-Кадровика. Запуск локально:

```bash
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

Проверки: `ruff check . && ruff format --check . && pytest`.
