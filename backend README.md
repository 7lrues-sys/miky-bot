# Mikky Backend (MVP)

Minimal backend scaffold (aiogram + PostgreSQL) for the Mikky planner bot.

Quick start (local)
1. Copy env: cp .env.example .env and fill values.
2. Create Postgres database and run migration:
   psql $DATABASE_URL -f db/migrations/001_init.sql
3. Create Python venv and install requirements:
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
4. Run the bot:
   python -m backend.src.bot
5. Run the worker (in separate terminal):
   python -m backend.src.worker

Notes and next steps
- This MVP stores raw content and minimal FSM handlers for onboarding and creating tasks.
- Heavy AI processing (Whisper, GPT parsing) must be implemented in worker.py and moved to a reliable queue (Celery + Redis) in production.
- Scheduler in worker.py is a placeholder: for correct per-user local-time pushes, compute next run using user timezone (pytz / zoneinfo) and schedule jobs or run periodic checks with timezone conversion.
- Add admin endpoints protected by ADMIN_TOKEN to allow CRUD for predictions and viewing logs.

If you want, я могу сейчас:
- Сгенерировать SQL seed for first 1000 predictions,
- Добавить basic admin REST endpoints (FastAPI) to manage predictions/users,
- Convert worker to Celery tasks (requires Redis + Celery setup).

Reply with next action: \"seed_predictions\", \"admin_api\" or \"celery_worker\".
