"""
Single-run script for GitHub Actions.
Each invocation: check for /done replies, update state, send notification.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

import httpx

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, TIMEZONE
from tasks import get_tasks_for_week
from state import (
    load_state,
    save_state,
    get_current_week,
    get_incomplete_tasks,
    get_completed_tasks,
    mark_task_done,
    all_tasks_complete,
    get_and_advance_notify_index,
)
from notifier import send_telegram, send_whatsapp, notify
from github_checker import check_new_issues, format_issue_alerts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def process_telegram_updates():
    """Check for /done messages from Telegram and process them."""
    state = load_state()
    last_update_id = state.get("last_update_id", 0)

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"offset": last_update_id + 1, "timeout": 5}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params, timeout=15)
            data = resp.json()
        except Exception as e:
            logger.error(f"Failed to get updates: {e}")
            return

    if not data.get("ok"):
        logger.error(f"Telegram getUpdates failed: {data}")
        return

    updates = data.get("result", [])
    week = get_current_week()
    tasks = get_tasks_for_week(week)

    for update in updates:
        state["last_update_id"] = update["update_id"]

        msg = update.get("message", {})
        chat_id = str(msg.get("chat", {}).get("id", ""))
        text = msg.get("text", "").strip()

        # Only process messages from authorized chat
        if chat_id != str(TELEGRAM_CHAT_ID):
            continue

        # Handle /done command
        if text.startswith("/done"):
            parts = text.split()
            if len(parts) >= 2:
                try:
                    task_num = int(parts[1])
                    task_index = task_num - 1

                    if 0 <= task_index < len(tasks):
                        was_new = mark_task_done(week, task_index)
                        completed = get_completed_tasks(week)
                        remaining = len(tasks) - len(completed)

                        if was_new:
                            if remaining == 0:
                                await send_telegram(
                                    f"*Task {task_num} — DONE*\n\n"
                                    f"'{tasks[task_index]}'\n\n"
                                    f"*ALL TASKS COMPLETE FOR WEEK {week}.*\n"
                                    f"Next week's tasks load automatically."
                                )
                            else:
                                await send_telegram(
                                    f"*Task {task_num} — DONE*\n\n"
                                    f"'{tasks[task_index]}'\n\n"
                                    f"{remaining} task{'s' if remaining != 1 else ''} remaining this week."
                                )
                        else:
                            await send_telegram(f"Task {task_num} was already marked done.")
                    else:
                        await send_telegram(f"Invalid task number. This week has tasks 1-{len(tasks)}.")
                except ValueError:
                    await send_telegram("Usage: /done <number>\nExample: /done 3")

        # Handle /status command
        elif text == "/status":
            completed = get_completed_tasks(week)
            incomplete = get_incomplete_tasks(week, tasks)
            lines = [f"*Week {week} — {len(completed)}/{len(tasks)} complete*\n"]
            for i, task in enumerate(tasks):
                status = "done" if i in completed else "TODO"
                lines.append(f"  {i + 1}. [{status}] {task}")
            await send_telegram("\n".join(lines))

        # Handle /tasks command
        elif text == "/tasks":
            completed = get_completed_tasks(week)
            lines = [f"*Week {week} Tasks:*\n"]
            for i, task in enumerate(tasks):
                marker = "[x]" if i in completed else "[ ]"
                lines.append(f"{i + 1}. {marker} {task}")
            await send_telegram("\n".join(lines))

        # Handle /week command
        elif text == "/week":
            month = ((week - 1) // 4) + 1
            await send_telegram(
                f"*Week {week} (Month {month})*\n\n"
                f"Send /tasks to see this week's list.\n"
                f"Send /status for progress."
            )

    save_state(state)


async def send_task_notification():
    """Send one incomplete task."""
    week = get_current_week()
    tasks = get_tasks_for_week(week)

    if all_tasks_complete(week, len(tasks)):
        await notify(
            f"*Week {week} — ALL TASKS COMPLETE*\n\n"
            f"Everything done. Next week's tasks load automatically.\n"
            f"Rest up or get ahead."
        )
        return

    incomplete = get_incomplete_tasks(week, tasks)
    if not incomplete:
        return

    slot = get_and_advance_notify_index()
    pick_index = slot % len(incomplete)
    task_idx, task_text = incomplete[pick_index]

    total = len(tasks)
    done_count = total - len(incomplete)

    message = (
        f"*Task {task_idx + 1}/{total} — INCOMPLETE*\n\n"
        f"{task_text}\n\n"
        f"Progress: {done_count}/{total} done (Week {week})\n"
        f"Reply /done {task_idx + 1} when finished."
    )

    await notify(message)


async def send_status_summary():
    """End-of-day summary."""
    week = get_current_week()
    tasks = get_tasks_for_week(week)
    incomplete = get_incomplete_tasks(week, tasks)
    done_count = len(tasks) - len(incomplete)

    if incomplete:
        remaining = "\n".join([f"  {i + 1}. {t}" for i, t in incomplete])
        message = (
            f"*End of Day — Week {week}*\n\n"
            f"Done: {done_count}/{len(tasks)}\n\n"
            f"Still incomplete:\n{remaining}\n\n"
            f"These will keep coming until you finish them."
        )
    else:
        message = (
            f"*End of Day — Week {week}*\n\n"
            f"All {len(tasks)} tasks complete. Solid work."
        )

    await notify(message)


async def check_github_issues():
    """Check for new issues on target repos."""
    try:
        new_issues = await check_new_issues()
        alert = format_issue_alerts(new_issues)
        if alert:
            await notify(alert)
    except Exception as e:
        logger.error(f"GitHub issue check failed: {e}")


async def main():
    mode = os.getenv("RUN_MODE", "notify")
    logger.info(f"Running in mode: {mode}")

    # Always process pending /done messages first
    await process_telegram_updates()

    if mode == "summary":
        await send_status_summary()
    elif mode == "notify":
        await send_task_notification()
        # Check GitHub issues once daily (on the first run)
        hour = datetime.now().hour
        if hour < 10:
            await check_github_issues()


if __name__ == "__main__":
    asyncio.run(main())
