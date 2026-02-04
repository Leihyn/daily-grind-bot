"""
Send messages to Telegram and WhatsApp (Callmebot).
"""

import logging
import urllib.parse

import httpx

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    CALLMEBOT_PHONE,
    CALLMEBOT_API_KEY,
)

logger = logging.getLogger(__name__)


async def send_telegram(text: str):
    """Send a message via Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured — skipping")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, timeout=15)
            if resp.status_code != 200:
                logger.error(f"Telegram error: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"Telegram send failed: {e}")


async def send_whatsapp(text: str):
    """Send a message via Callmebot WhatsApp API."""
    if not CALLMEBOT_PHONE or not CALLMEBOT_API_KEY:
        logger.warning("WhatsApp (Callmebot) not configured — skipping")
        return

    # Callmebot expects URL-encoded text
    encoded = urllib.parse.quote_plus(text)
    url = (
        f"https://api.callmebot.com/whatsapp.php"
        f"?phone={CALLMEBOT_PHONE}"
        f"&text={encoded}"
        f"&apikey={CALLMEBOT_API_KEY}"
    )

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, timeout=30)
            if resp.status_code != 200:
                logger.error(f"WhatsApp error: {resp.status_code} {resp.text}")
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")


async def notify(text: str):
    """Send to both Telegram and WhatsApp."""
    await send_telegram(text)
    await send_whatsapp(text)
