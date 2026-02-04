"""
Entry point: runs Telegram bot polling + APScheduler for timed notifications.
"""

import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import TIMEZONE, NOTIFY_HOURS
from bot import build_app
from scheduler import send_task_notification, send_status_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def setup_scheduler() -> AsyncIOScheduler:
    """Configure APScheduler with notification jobs."""
    sched = AsyncIOScheduler(timezone=TIMEZONE)

    # Schedule task reminders at each notify hour
    for hour in NOTIFY_HOURS:
        if hour == NOTIFY_HOURS[-1]:
            # Last slot of the day = end-of-day summary
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

    # Initialize the bot application (increase connect timeout for slow networks)
    await app.initialize()
    await app.start()

    # Start polling for Telegram messages (non-blocking)
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

    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        sched.shutdown()
        await app.updater.stop()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
