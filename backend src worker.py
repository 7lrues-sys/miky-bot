"""
File-level: Background worker for scheduled tasks (morning push, processing media).
This is a simple APScheduler-based worker for MVP.
Heavy AI tasks should be pushed to a task queue (Celery/Redis) in production.
"""

import os
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, time, timedelta
from .db import init_db_pool, fetch, fetchrow, execute
from dotenv import load_dotenv

load_dotenv()

async def send_morning_push():
    """
    Scan users and send morning push for those whose local time is 07:00.
    This is a minimal placeholder: in production compute per-user timezone and schedule properly.
    """
    # For MVP: send to users who have timezone = 'Europe/Kiev' and haven't received today's push.
    rows = await fetch("SELECT id, telegram_id, timezone, language FROM users WHERE is_active = TRUE AND timezone IS NOT NULL")
    today = datetime.utcnow().date()
    for u in rows:
        # Naive timezone check omitted in MVP: in production convert timezone to user local time.
        # Here we only log an entry to daily_push_logs to avoid duplication.
        try:
            await execute(
                "INSERT INTO daily_push_logs (user_id, date_sent, push_type) VALUES ($1,$2,$3) ON CONFLICT DO NOTHING",
                u["id"], today, "morning"
            )
            # In real worker: call Telegram API to send messages (use Bot instance or webhook).
            print(f"[worker] Would send morning push to user {u['telegram_id']} (lang={u['language']})")
        except Exception as e:
            print("Error sending push for user", u["telegram_id"], e)

async def process_pending_media():
    """
    Placeholder worker that would pick up media_archive rows and call AI (Whisper/Vision).
    For MVP we just mark pending -> failed after demo processing.
    """
    rows = await fetch("SELECT id, user_id, file_id FROM media_archive WHERE status='pending' LIMIT 10")
    for r in rows:
        try:
            # TODO: download file via Telegram API + call Whisper -> then update media_archive and corresponding task.
            await execute("UPDATE media_archive SET status=$1 WHERE id=$2", "unrecognized", r["id"])
            print(f"[worker] Marked media {r['id']} as unrecognized (placeholder)")
        except Exception as e:
            print("Error processing media", e)

def start_scheduler():
    """
    Start APScheduler with jobs.
    """
    scheduler = AsyncIOScheduler()
    # Run simple workers periodically.
    scheduler.add_job(lambda: asyncio.create_task(process_pending_media()), "interval", seconds=30)
    # Morning push check every minute (for production this should be per-minute and compute local time).
    scheduler.add_job(lambda: asyncio.create_task(send_morning_push()), "interval", seconds=60)
    scheduler.start()
    print("Worker scheduler started")

async def main():
    """
    Initialize DB and scheduler, then keep alive.
    """
    await init_db_pool()
    start_scheduler()
    # Keep the worker alive
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Worker stopped")
