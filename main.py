"""
Entry point: runs Telegram bot polling + APScheduler + health check web server.
The health endpoint keeps Render from spinning down the free-tier service.
"""

import asyncio
import logging
import os
from aiohttp import web

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import TIMEZONE, NOTIFY_HOURS
from bot import build_app
from scheduler import send_task_notification, send_status_summary
from state import get_current_week, get_completed_tasks
from tasks import get_tasks_for_week

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def health_handler(request):
    """Health check endpoint — keeps Render from sleeping."""
    week = get_current_week()
    tasks = get_tasks_for_week(week)
    done = len(get_completed_tasks(week))
    return web.json_response({
        "status": "ok",
        "week": week,
        "progress": f"{done}/{len(tasks)}",
    })


def setup_scheduler() -> AsyncIOScheduler:
    """Configure APScheduler with notification jobs."""
    sched = AsyncIOScheduler(timezone=TIMEZONE)

    for hour in NOTIFY_HOURS:
        if hour == NOTIFY_HOURS[-1]:
            sched.add_job(
                send_status_summary,
                CronTrigger(hour=hour, minute=0, timezone=TIMEZONE),
                id=f"summary_{hour}",
                name=f"End of day summary ({hour}:00)",
            )
        else:
            sched.add_job(
                send_task_notification,
                CronTrigger(hour=hour, minute=0, timezone=TIMEZONE),
                id=f"notify_{hour}",
                name=f"Task notification ({hour}:00)",
            )

    return sched


async def main():
    logger.info("Starting Daily Grind Bot...")

    # Build Telegram bot
    app = build_app()

    await app.initialize()
    await app.start()

    await app.updater.start_polling(
        drop_pending_updates=True,
        connect_timeout=30,
        read_timeout=30,
        pool_timeout=30,
    )
    logger.info("Telegram bot polling started")

    # Start scheduler
    sched = setup_scheduler()
    sched.start()
    logger.info(f"Scheduler started — notifications at {NOTIFY_HOURS} ({TIMEZONE})")

    # Start health check web server (Render needs a port listener)
    port = int(os.getenv("PORT", 10000))
    web_app = web.Application()
    web_app.router.add_get("/", health_handler)
    web_app.router.add_get("/health", health_handler)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health server listening on port {port}")

    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        sched.shutdown()
        await runner.cleanup()
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
