# Daily Grind Bot

Sends you 6 task reminders per day (Telegram + WhatsApp) based on your IMPORTANT.md roadmap. Tasks repeat until you mark them done.

## Setup

### 1. Telegram Bot

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`, follow prompts, name it whatever you want
3. Copy the bot token — that's your `TELEGRAM_BOT_TOKEN`
4. Start a chat with your new bot, send `/start`
5. The bot replies with your chat ID — that's your `TELEGRAM_CHAT_ID`

### 2. Callmebot WhatsApp

1. Save this number in your contacts: `+34 644 71 84 74`
2. Send this WhatsApp message to that number: `I allow callmebot to send me messages`
3. You'll receive an API key — that's your `CALLMEBOT_API_KEY`
4. Your phone number with country code (no + or spaces) is your `CALLMEBOT_PHONE`

### 3. Deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app), create new project from GitHub repo
3. Add a **Volume** — mount path: `/data` (this keeps your progress across deploys)
4. Add environment variables (Settings > Variables):

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
CALLMEBOT_PHONE=...
CALLMEBOT_API_KEY=...
START_DATE=2025-02-03
STATE_FILE=/data/state.json
```

5. Railway auto-detects the Procfile and starts the worker

### 4. GitHub Token (Optional)

For issue alerts on target repos. Without it, GitHub rate-limits to 60 requests/hour (still works, just fewer checks).

1. Go to github.com > Settings > Developer Settings > Personal Access Tokens > Fine-grained
2. Create token with public repo read access
3. Add as `GITHUB_TOKEN` in Railway

## Usage

### Telegram Commands

| Command | What it does |
|---------|-------------|
| `/done 3` | Mark task 3 as complete |
| `/status` | Show week progress |
| `/tasks` | List all tasks this week |
| `/week` | Show current week and month |
| `/help` | Command list |

### How It Works

- **Monday**: 6 new tasks load based on your roadmap week
- **6x daily** (7am, 10am, 1pm, 4pm, 7pm WAT): sends one incomplete task
- **10pm WAT**: end-of-day summary with remaining tasks
- **Tasks repeat** every notification cycle until you `/done` them
- **GitHub issues**: checks target repos for new `good first issue` labels once daily

### Notification Schedule (WAT / UTC+1)

| Time | Content |
|------|---------|
| 7:00 | Incomplete task |
| 10:00 | Incomplete task + new GitHub issues |
| 13:00 | Incomplete task |
| 16:00 | Incomplete task |
| 19:00 | Incomplete task |
| 22:00 | End-of-day summary |

## Troubleshooting

**Bot doesn't respond to /start**
Check that `TELEGRAM_BOT_TOKEN` is correct. Try regenerating the token with BotFather.

**No WhatsApp messages**
Callmebot requires you to send the authorization message first. Re-send "I allow callmebot to send me messages" to +34 644 71 84 74.

**Progress resets after Railway redeploy**
You forgot to add a Volume. Go to Railway dashboard > your service > add Volume > mount at `/data`.

**"Unauthorized" GitHub API errors in logs**
Your `GITHUB_TOKEN` expired or has wrong permissions. Regenerate it. The bot still works without it — just fewer issue checks per hour.

**Wrong week number**
Check your `START_DATE` env var. The bot calculates weeks from that date.
