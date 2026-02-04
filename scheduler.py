"""
Scheduled notification logic.
Fires 6 times daily — each time sends one incomplete task.
"""

import logging

from tasks import get_tasks_for_week
from state import (
    get_current_week,
    get_incomplete_tasks,
    all_tasks_complete,
    get_and_advance_notify_index,
)
from notifier import notify
from github_checker import check_new_issues, format_issue_alerts

logger = logging.getLogger(__name__)


async def send_task_notification():
    """Core scheduled job: send an incomplete task reminder."""
    week = get_current_week()
    tasks = get_tasks_for_week(week)

    # Check if all tasks are done
    if all_tasks_complete(week, len(tasks)):
        await notify(
            f"*Week {week} — ALL TASKS COMPLETE*\n\n"
            f"Everything done. Next week's tasks load automatically.\n"
            f"Rest up or get ahead."
        )
        return

    # Get incomplete tasks
    incomplete = get_incomplete_tasks(week, tasks)
    if not incomplete:
        return

    # Round-robin through incomplete tasks so you see different ones each notification
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

    # Also check for new GitHub issues (once per cycle, at the first slot)
    if slot == 0:
        try:
            new_issues = await check_new_issues()
            alert = format_issue_alerts(new_issues)
            if alert:
                await notify(alert)
        except Exception as e:
            logger.error(f"GitHub issue check failed: {e}")


async def send_status_summary():
    """Send a brief status at the end of day (10 PM slot)."""
    week = get_current_week()
    tasks = get_tasks_for_week(week)
    incomplete = get_incomplete_tasks(week, tasks)
    done_count = len(tasks) - len(incomplete)

    if incomplete:
        remaining = "\n".join(
            [f"  {i + 1}. {t}" for i, t in incomplete]
        )
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
