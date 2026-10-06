# Developer shortcuts. Everything else goes through docker compose.
-include .env
export

.PHONY: up down logs ps api-shell migrate revision test lint fmt backup

up:            ## start the whole stack
	docker compose up -d --build
down:
	docker compose down
logs:
	docker compose logs -f --tail=100 api worker beat
ps:
	docker compose ps
api-shell:
	docker compose exec api bash
migrate:       ## apply migrations inside the api container
	docker compose exec api alembic upgrade head
revision:      ## make revision m="message"
	docker compose exec api alembic revision --autogenerate -m "$(m)"
test:          ## backend tests inside the api container against <POSTGRES_DB>_test
	docker compose exec \
	  -e TEST_DATABASE_URL=postgresql+psycopg://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@postgres:5432/$(POSTGRES_DB)_test \
	  api pytest -v
lint:
	cd backend && ruff check . && ruff format --check .
	cd frontend && npm run -s typecheck && npm run -s lint
fmt:
	cd backend && ruff check --fix . && ruff format .
backup:
	bash deploy/backup-postgres.sh
