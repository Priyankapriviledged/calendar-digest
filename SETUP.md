# Calendar → Telegram Daily Digest
**Replace Make.com with a free Python script + cron job**

---

## What you'll need
- A machine to run this on (see options below)
- A Google account (you already have one)
- Your existing Telegram bot token + chat ID

---

## Step 1 — Choose where to run it

| Option | Cost | Effort |
|---|---|---|
| **Oracle Cloud Free Tier VM** | Free forever | ~15 min setup |
| **Raspberry Pi / home server** | Free (hardware you own) | ~5 min |
| **GitHub Actions** | Free (2000 min/month) | ~10 min |

> **Recommendation:** Oracle Cloud's Always Free VM (AMD, 1 OCPU, 1GB RAM) is perfect. Sign up at cloud.oracle.com — no credit card charges for Always Free resources.

---

## Step 2 — Get your Telegram credentials

You likely already have these from your Make.com setup.

**Bot token:** From `@BotFather` on Telegram → `/mybots` → your bot → API Token.

**Chat ID:** Send any message to your bot, then open:
```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```
Look for `"chat": {"id": 123456789}` — that number is your chat ID.

---

## Step 3 — Set up Google Calendar API

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (e.g. "Calendar Digest")
3. Enable the **Google Calendar API**:
   - APIs & Services → Library → search "Google Calendar API" → Enable
4. Create credentials:
   - APIs & Services → Credentials → Create Credentials → **OAuth 2.0 Client ID**
   - Application type: **Desktop app**
   - Download the JSON file → rename it to **`credentials.json`**
5. Add your Google account as a test user:
   - APIs & Services → OAuth consent screen → Test users → Add your email

---

## Step 4 — Set up the script on your machine

```bash
# 1. Copy these files to your machine
scp -r calendar-telegram/ user@your-server:~/

# 2. SSH into your machine
ssh user@your-server

# 3. Install dependencies
cd ~/calendar-telegram
pip3 install -r requirements.txt

# 4. Edit config.json with your values
nano config.json
```

Fill in `config.json`:
```json
{
  "telegram_bot_token": "123456:ABC-your-actual-token",
  "telegram_chat_id": "987654321",
  "timezone": "Europe/Helsinki",
  "calendars": ["primary"],
  "include_tomorrow": true
}
```

**Want events from multiple calendars?** Find your calendar IDs in Google Calendar:
Settings → click a calendar → Scroll down to "Calendar ID" (looks like `name@group.calendar.google.com`)
Then add them to the list: `"calendars": ["primary", "your-other-cal@group.calendar.google.com"]`

---

## Step 5 — Authenticate with Google (one-time)

Run the script **once manually** from a machine with a browser:

```bash
python3 calendar_to_telegram.py
```

A browser window will open → log in → grant calendar access.
This creates a `token.json` file that handles all future logins automatically (it auto-refreshes).

If running on a headless server, do this first on your laptop, then copy `token.json` to the server:
```bash
scp token.json user@your-server:~/calendar-telegram/
```

---

## Step 6 — Test it

```bash
python3 calendar_to_telegram.py
```

You should receive a Telegram message within seconds. ✅

---

## Step 7 — Schedule with cron (6am daily)

```bash
crontab -e
```

Add this line (runs at 06:00 Helsinki time):
```
0 6 * * * cd /home/youruser/calendar-telegram && /usr/bin/python3 calendar_to_telegram.py >> /home/youruser/calendar-telegram/digest.log 2>&1
```

> **Important:** Make sure your server's timezone is set to `Europe/Helsinki`.
> Check with: `timedatectl`
> Set with: `sudo timedatectl set-timezone Europe/Helsinki`

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `token.json` expires | Script auto-refreshes — only fails if you revoke access in Google settings |
| Bot doesn't receive message | Double-check chat ID; make sure you've sent at least one message to the bot first |
| `403 Forbidden` from Google | Re-run auth flow; check the calendar ID is correct |
| Cron doesn't fire | Check log file: `tail -f ~/calendar-telegram/digest.log` |
| Special characters break Telegram | The script escapes MarkdownV2 automatically — if issues persist, edit `parse_mode` to `"HTML"` in the script |

---

## GitHub Actions alternative (no server needed)

If you don't want to maintain a server at all, create `.github/workflows/digest.yml` in a **private** repo:

```yaml
name: Daily Calendar Digest
on:
  schedule:
    - cron: '0 4 * * *'  # 4 UTC = 6 Helsinki (adjust for DST)
jobs:
  send-digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python calendar_to_telegram.py
        env:
          # Store token.json content as a GitHub secret
          GOOGLE_TOKEN: ${{ secrets.GOOGLE_TOKEN }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

> Note: For GitHub Actions you'd need to slightly modify the script to read credentials from env vars. Let me know if you want that version.
