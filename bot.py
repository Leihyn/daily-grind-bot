"""
Telegram bot command handlers.
Users interact via /done, /status, /tasks, /week, /help.
"""

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from tasks import get_tasks_for_week
from state import (
    get_current_week,
    get_completed_tasks,
    get_incomplete_tasks,
    mark_task_done,
    all_tasks_complete,
)

logger = logging.getLogger(__name__)


def is_authorized(update: Update) -> bool:
    """Only respond to the configured chat."""
    return str(update.effective_chat.id) == str(TELEGRAM_CHAT_ID)


async def cmd_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark a task as complete. Usage: /done 3"""
    if not is_authorized(update):
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: /done <task_number>\nExample: /done 3"
        )
        return

    try:
        task_num = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Task number must be a number. Example: /done 3")
        return

    week = get_current_week()
    tasks = get_tasks_for_week(week)
    task_index = task_num - 1  # Convert to 0-based

    if task_index < 0 or task_index >= len(tasks):
        await update.message.reply_text(
            f"Invalid task number. This week has tasks 1-{len(tasks)}."
        )
        return

    was_new = mark_task_done(week, task_index)

    if was_new:
        completed = get_completed_tasks(week)
        remaining = len(tasks) - len(completed)

        if remaining == 0:
            await update.message.reply_text(
                f"*Task {task_num} — DONE*\n\n"
                f"'{tasks[task_index]}'\n\n"
                f"*ALL TASKS COMPLETE FOR WEEK {week}.*\n"
                f"Next week's tasks load automatically.",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text(
                f"*Task {task_num} — DONE*\n\n"
                f"'{tasks[task_index]}'\n\n"
                f"{remaining} task{'s' if remaining != 1 else ''} remaining this week.",
                parse_mode="Markdown",
            )
    else:
        await update.message.reply_text(f"Task {task_num} was already marked done.")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current week progress."""
    if not is_authorized(update):
        return

    week = get_current_week()
    tasks = get_tasks_for_week(week)
    completed = get_completed_tasks(week)
    incomplete = get_incomplete_tasks(week, tasks)

    lines = [f"*Week {week} — {len(completed)}/{len(tasks)} complete*\n"]

    for i, task in enumerate(tasks):
        status = "done" if i in completed else "TODO"
        lines.append(f"  {i + 1}. [{status}] {task}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all tasks for current week."""
    if not is_authorized(update):
        return

    week = get_current_week()
    tasks = get_tasks_for_week(week)
    completed = get_completed_tasks(week)

    lines = [f"*Week {week} Tasks:*\n"]
    for i, task in enumerate(tasks):
        marker = "[x]" if i in completed else "[ ]"
        lines.append(f"{i + 1}. {marker} {task}")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show what week you're on and overall month."""
    if not is_authorized(update):
        return

    week = get_current_week()
    month = ((week - 1) // 4) + 1

    await update.message.reply_text(
        f"*Week {week} (Month {month})*\n\n"
        f"Use /tasks to see this week's list.\n"
        f"Use /status for progress.",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available commands."""
    if not is_authorized(update):
        return

    await update.message.reply_text(
        "*Commands:*\n\n"
        "/done <number> — Mark task complete (e.g. /done 3)\n"
        "/status — Current week progress\n"
        "/tasks — List all tasks this week\n"
        "/week — Show current week and month\n"
        "/help — This message",
        parse_mode="Markdown",
    )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command (first interaction)."""
    if not is_authorized(update):
        # Still respond to /start so user can get their chat ID
        await update.message.reply_text(
            f"Your chat ID: `{update.effective_chat.id}`\n\n"
            f"Set this as TELEGRAM_CHAT_ID in your environment.",
            parse_mode="Markdown",
        )
        return

    week = get_current_week()
    tasks = get_tasks_for_week(week)

    lines = [
        "*Daily Grind Bot — Active*\n",
        f"Week {week} loaded. {len(tasks)} tasks.\n",
        "You'll get 6 reminders daily until every task is marked done.\n",
        "*Commands:*",
        "/done <number> — Mark task complete",
        "/status — Progress",
        "/tasks — This week's list",
        "/help — All commands",
    ]
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


def build_app() -> Application:
    """Build and return the Telegram bot application."""
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("done", cmd_done))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("tasks", cmd_tasks))
    app.add_handler(CommandHandler("week", cmd_week))
    app.add_handler(CommandHandler("help", cmd_help))

    return app
