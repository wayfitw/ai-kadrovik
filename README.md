# AI-Кадровик

Система кадрового делопроизводства РФ с ИИ-агентом. Текущий этап — **MVP на ручном вводе**
(7–27 октября 2026).

Начни с `CLAUDE.md`, затем `docs/00-PROJECT-BRIEF.md` → `docs/02-MVP-SCOPE.md` →
`docs/03-BACKLOG-MVP.md`.

## Быстрый старт (Docker)

```bash
cp .env.example .env            # поменяй пароли на стенде
docker compose up -d --build    # postgres, redis, minio, soffice, api, worker, beat, frontend
curl http://localhost:8000/health
open http://localhost:3000      # кабинет
```

`api` при старте сам применяет миграции (`alembic upgrade head`).
Роль `audit_writer` создаётся init-скриптом Postgres при первом запуске
(`docker/postgres/initdb/`), права на `audit_log` выдаёт миграция `0001`.

## Разработка без Docker

```bash
cd backend
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install -e ".[dev]"
alembic upgrade head && uvicorn app.main:app --reload

cd ../frontend && npm ci && npm run dev
```

Проверки перед PR: `make lint`, в `backend/` —
`TEST_DATABASE_URL=postgresql+psycopg://…/kadrovik_test pytest`.
CI делает то же самое плюс сборку трёх образов.

## Структура

```
backend/     FastAPI, SQLAlchemy 2, Alembic, Celery      (app/<домен>/ — см. CLAUDE.md)
frontend/    Next.js 14 + TypeScript — кабинет
templates/   DOCX-шаблоны (docxtpl), блок 2.3
docker/      образ soffice, init-скрипты Postgres
deploy/      стенд: запуск, бэкап и восстановление Postgres, cron
docs/        бриф, архитектура, границы MVP, бэклог, правовой пакет, стенд, дневные акты
```
