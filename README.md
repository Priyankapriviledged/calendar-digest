# 📅 Google Calendar → Telegram Daily Digest

A lightweight automation that sends you a summary of today's Google Calendar events every morning at **6:00 AM (Helsinki time)** via Telegram — completely free, no third-party automation tools required.

Built to replace Make.com for a simple daily digest workflow. Runs on **GitHub Actions**, so nothing needs to stay on or be maintained on your end.

---

## What it does

Every morning at 6 AM, this script:

1. Connects to your Google Calendar
2. Fetches all events scheduled for today
3. Formats them into a clean, readable message
4. Sends the message to your Telegram bot

**Example message when you have meetings:**

```
🗓 Meetings for today

09:00 — Sprint Planning
11:00 — Customer Sync
14:00 — API Review
```

**Example message when you have nothing scheduled:**

```
🗓 Meetings for today

Nothing scheduled. Enjoy your day!
```

---

## How it works

```
GitHub Actions (scheduler)
        │
        │  triggers at 6:00 AM daily
        ▼
  calendar_to_telegram.py
        │
        ├──► Google Calendar API  →  fetches today's events
        │
        └──► Telegram Bot API     →  sends the message to you
```

GitHub Actions is a free cloud service that can run scripts on a schedule. It stores your API keys securely as encrypted secrets, so nothing sensitive is exposed in the code.

---

## Files in this repository

| File | Purpose |
|---|---|
| `calendar_to_telegram.py` | The main script — fetches events and sends the Telegram message |
| `auth_helper.py` | A one-time helper script you run on your laptop to generate the Google token |
| `requirements.txt` | The Python libraries the script depends on |
| `.github/workflows/daily_digest.yml` | Tells GitHub Actions when and how to run the script |
| `README.md` | This file |

---

## Setup

### What you need before starting

- A **Google account** (the one with your calendar)
- A **Telegram bot token** and **chat ID** (from your existing bot setup via @BotFather)
- A **GitHub account** (free at github.com)
- A **Windows/Mac/Linux laptop** for a one-time authentication step

Setup takes around 20–30 minutes and is done entirely through web browsers and one short command on your laptop.

---

### Step 1 — Google Cloud setup (one time only)

You need to give this script permission to read your Google Calendar. Google requires you to create a small "project" in their cloud console to do this.

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and sign in with your Google account
2. Click **Select a project** at the top → **New project** → name it `Calendar Digest` → **Create**
3. Go to **APIs & Services → Library**, search for `Google Calendar API`, click it → **Enable**
4. Go to **APIs & Services → OAuth consent screen** → choose **External** → **Create**
   - Fill in: App name (`Calendar Digest`), your email in the support email field, your email again at the bottom
   - Click **Save and Continue** through all the remaining screens
5. Go to **APIs & Services → Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
   - Application type: **Desktop app** → name it anything → **Create**
6. Click the download icon next to the credential you just created — this saves a file called `credentials.json` to your laptop

---

### Step 2 — Generate your Google token (one time only)

This step runs a small helper script on your laptop that opens a browser window, asks you to log in to Google, and then gives you a token string to store in GitHub.

1. Download or clone this repository to your laptop
2. Place the `credentials.json` file (from Step 1) inside the project folder
3. Open a terminal / Command Prompt in that folder
4. Install the required libraries:
   ```
   pip install -r requirements.txt
   ```
5. Run the helper:
   ```
   python auth_helper.py
   ```
6. A browser window will open — log in with your Google account and click **Allow**
7. Return to the terminal — you'll see a long block of text starting with `{` and ending with `}`
8. **Copy the entire block** — you'll need it in the next step

> **Note:** `credentials.json` is only needed for this one-time step. Do not upload it to GitHub.

---

### Step 3 — Add secrets to GitHub

Your Telegram credentials and Google token are stored as encrypted secrets in GitHub — they are never visible in the code.

1. In your GitHub repository, go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret** and add these three secrets:

| Secret name | Where to find the value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | From @BotFather on Telegram → your bot → API Token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID number |
| `GOOGLE_TOKEN` | The full block of text copied in Step 2 |

---

### Step 4 — Test it

1. Go to the **Actions** tab in your GitHub repository
2. Click **Daily Calendar Digest** in the left sidebar
3. Click **Run workflow** → **Run workflow**
4. Wait about 30 seconds — you should receive a Telegram message

If you see a green checkmark in Actions, it worked. If you see a red X, click on it to see the error log and refer to the Troubleshooting section below.

---

## Schedule

The workflow runs at **6:00 AM Helsinki time (Europe/Helsinki)** every day.

In the workflow file this is written as `cron: '0 3 * * *'` — that's 3:00 AM UTC, which equals 6:00 AM Helsinki time during winter. During Finnish summer time (EEST, UTC+3), the message will arrive at 5:00 AM instead of 6:00 AM. If you want to adjust for this, change the cron to `0 3 * * *` in winter and `0 3 * * *` in summer, or simply accept the one-hour drift across seasons.

> **Tip:** GitHub Actions free tier allows up to 2,000 minutes per month for private repositories. This workflow uses about 1 minute per day (roughly 30 minutes per month), well within the free limit.

---

## Customisation

### Change the schedule

Edit `.github/workflows/daily_digest.yml` and change the cron expression:

```yaml
- cron: '0 3 * * *'   # 03:00 UTC = 06:00 Helsinki winter time
```

Use [crontab.guru](https://crontab.guru) to generate a different cron expression if needed.

### Add more calendars

In `calendar_to_telegram.py`, find the line:

```python
calendarId="primary",
```

Replace `"primary"` with your other calendar's ID. You can find a calendar's ID in Google Calendar under **Settings → click the calendar → Calendar ID**.

---

## Troubleshooting

| Problem | What to check |
|---|---|
| Red X in GitHub Actions | Click the failed run → expand the step that failed → read the error message |
| No Telegram message received | Double-check `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in GitHub Secrets. Make sure you've sent at least one message to the bot first. |
| `GOOGLE_TOKEN` error | Re-run `auth_helper.py` on your laptop and replace the secret in GitHub with the fresh token |
| Message arrives at wrong time | Adjust the `cron` expression in the workflow file — remember GitHub uses UTC |
| `pip` not found on laptop | Install Python from [python.org](https://python.org) — tick "Add Python to PATH" during installation |

---

## Privacy & security

- Your calendar data is never stored anywhere — it is fetched, formatted, and sent to Telegram in a single run, then discarded
- All credentials (Telegram token, Google token) are stored as **encrypted GitHub Secrets** — not visible in the repository code or logs
- The Google token only has **read-only access** to your calendar (`calendar.readonly` scope) — it cannot create, edit, or delete events
- This repository is **private** — only you can see its contents

---

## Tech stack

| Component | Technology |
|---|---|
| Language | Python 3.11 |
| Scheduler | GitHub Actions (free tier) |
| Calendar access | Google Calendar API v3 |
| Messaging | Telegram Bot API |
| Auth | OAuth 2.0 (Google) |

---

*Built as a free alternative to Make.com for a simple daily digest workflow.*
