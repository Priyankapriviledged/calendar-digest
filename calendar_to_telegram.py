#!/usr/bin/env python3
"""
calendar_to_telegram.py
Reads today's Google Calendar events and sends a digest to Telegram.
Designed to run on GitHub Actions - reads all secrets from environment variables.
"""

import os
import json
import datetime
import requests
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

TIMEZONE           = "Europe/Helsinki"
TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]
GOOGLE_TOKEN_JSON  = os.environ["GOOGLE_TOKEN"]

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_calendar_service():
    token_data = json.loads(GOOGLE_TOKEN_JSON)
    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes", SCOPES),
    )
    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
    return build("calendar", "v3", credentials=creds)

def get_todays_events(service):
    tz = ZoneInfo(TIMEZONE)
    today = datetime.date.today()
    start = datetime.datetime.combine(today, datetime.time.min, tzinfo=tz)
    end   = datetime.datetime.combine(today, datetime.time.max, tzinfo=tz)
    result = service.events().list(
        calendarId="primary",
        timeMin=start.isoformat(),
        timeMax=end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
        maxResults=20,
    ).execute()
    return result.get("items", [])

def format_event(event):
    summary   = event.get("summary", "No title")
    start_raw = event["start"].get("dateTime") or event["start"].get("date")

    if "T" not in start_raw:
        start_str = "All day"
    else:
        tz = ZoneInfo(TIMEZONE)
        start_dt  = datetime.datetime.fromisoformat(start_raw).astimezone(tz)
        start_str = start_dt.strftime("%H:%M")

    return f"{start_str} — {summary}"

def build_message(events):
    lines = ["\U0001f5d3 Meetings for today", ""]

    if events:
        for e in events:
            lines.append(format_event(e))
    else:
        lines.append("Nothing scheduled. Enjoy your day!")

    return "\n".join(lines)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }, timeout=10)
    response.raise_for_status()
    print("Message sent successfully.")

def main():
    service = get_calendar_service()
    events  = get_todays_events(service)
    message = build_message(events)
    send_telegram(message)

if __name__ == "__main__":
    main()
