#!/usr/bin/env python3
"""
auth_helper.py
Run this ONCE on your Windows laptop to generate the Google token.
It will open a browser for you to log in, then print the token
you need to paste into GitHub Secrets.
"""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

print("\n=== Google Calendar Auth Helper ===\n")
print("A browser window will open. Log in with your Google account and grant access.")
print("Come back here after you approve.\n")

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

token_data = json.loads(creds.to_json())
token_json_string = json.dumps(token_data)

print("\n" + "="*60)
print("SUCCESS! Copy EVERYTHING between the lines below")
print("(including the curly braces) and paste it into GitHub Secrets")
print("as the value for GOOGLE_TOKEN")
print("="*60 + "\n")
print(token_json_string)
print("\n" + "="*60)
