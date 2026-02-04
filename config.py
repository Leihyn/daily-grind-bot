import os

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# WhatsApp (Callmebot)
CALLMEBOT_PHONE = os.getenv("CALLMEBOT_PHONE")  # with country code, e.g. 2348012345678
CALLMEBOT_API_KEY = os.getenv("CALLMEBOT_API_KEY")

# GitHub (optional, for issue alerts)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Timezone
TIMEZONE = "Africa/Lagos"  # WAT (UTC+1)

# Roadmap start date (YYYY-MM-DD)
START_DATE = os.getenv("START_DATE", "2025-02-03")

# Notification times (24h format, WAT)
NOTIFY_HOURS = [7, 10, 13, 16, 19, 22]

# State file path (use Railway volume mount if available)
STATE_FILE = os.getenv("STATE_FILE", "/data/state.json")

# Target repos for issue alerts
TARGET_REPOS = [
    "Uniswap/v4-core",
    "foundry-rs/foundry",
    "aave/aave-v3-core",
    "smartcontractkit/chainlink",
    "OpenZeppelin/openzeppelin-contracts",
    "coral-xyz/anchor",
]

ISSUE_LABELS = ["good first issue", "help wanted", "documentation"]
