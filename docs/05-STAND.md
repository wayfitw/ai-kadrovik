# 05. Тестовый стенд и бэкапы

Один сервер (Ubuntu 22.04+, 4 vCPU, 8 ГБ RAM, 60 ГБ диска), Docker Engine 24+ с плагином
compose. Всё работает из одного `docker compose up` (см. `docker-compose.yml`).

## Первый запуск

```bash
sudo useradd -m -G docker deploy && sudo -iu deploy
git clone <repo> /opt/kadrovik && cd /opt/kadrovik
cp .env.example .env
# обязательно поменять: SECRET_KEY, PDN_MASTER_KEY, POSTGRES_PASSWORD, AUDIT_DB_PASSWORD,
# MINIO_SECRET_KEY. APP_ENV=stand
bash deploy/stand-up.sh
```

Скрипт собирает образы, поднимает стек, ждёт `/health` и печатает его ответ.
Порты наружу: `8000` (API, `/docs`), `3000` (кабинет). Postgres и MinIO слушают
только `127.0.0.1`. Перед демонстрацией заказчику поставить nginx с HTTPS перед
`3000` и `8000` (не входит в блок 1.1).

## Обновление

```bash
cd /opt/kadrovik && bash deploy/stand-up.sh    # git pull --ff-only, build, up -d
```

Миграции применяет контейнер `api` при старте.

## Бэкап Postgres по cron

```bash
sudo mkdir -p /var/backups/kadrovik && sudo chown deploy /var/backups/kadrovik
sudo touch /var/log/kadrovik-backup.log && sudo chown deploy /var/log/kadrovik-backup.log
crontab deploy/crontab.example       # ежедневно 02:10 UTC, хранить 14 дней
bash deploy/backup-postgres.sh       # проверить вручную
```

Дамп в формате `pg_dump --format=custom` + `.sha256`. Восстановление:
`bash deploy/restore-postgres.sh /var/backups/kadrovik/kadrovik-<дата>.dump`.
Файлы MinIO (`data/minio`) бэкапить отдельно вместе с `.env` — без `PDN_MASTER_KEY`
зашифрованные ПДн не восстановить.

## Проверка после развёртывания

1. `curl http://<host>:8000/health` → `"status":"ok"`, `db` и `redis` — `ok`.
2. `docker compose exec postgres psql -U kadrovik -c "\du audit_writer"` — роль есть.
3. `docker compose exec postgres psql -U kadrovik -c "UPDATE audit_log SET note='x'"`
   → `ERROR: audit_log is append-only`.
4. `make test` — тесты проходят внутри контейнера `api`.

## Статус

Скрипты и инструкция готовы, стенд **не развёрнут**: нужен адрес сервера и SSH-доступ
от заказчика (см. дневной акт за 2026-10-06, раздел 3).
