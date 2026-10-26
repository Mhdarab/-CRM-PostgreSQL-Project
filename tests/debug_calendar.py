"""
Diagnostic — finds why 0 events are returned.
Run: python debug_calendar.py
"""

import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials", "service_account.json")

# 👇 MUST match the ID used in google_calendar_service.py
CALENDAR_ID = "isaacwaseem257@gmail.com"

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

print("=" * 60)
print("STEP 1: Authenticate")
print("=" * 60)
creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
service = build("calendar", "v3", credentials=creds, cache_discovery=False)
print(f"✅ Service account: {creds.service_account_email}")

print("\n" + "=" * 60)
print("STEP 2: List all calendars visible to the service account")
print("=" * 60)
try:
    cal_list = service.calendarList().list().execute()
    items = cal_list.get("items", [])
    print(f"Found {len(items)} calendar(s):")
    for c in items:
        print(f"  • ID:   {c.get('id')}")
        print(f"    Name: {c.get('summary')}")
        print(f"    Role: {c.get('accessRole')}")
        print()
except Exception as e:
    print(f"❌ {e}")

print("=" * 60)
print(f"STEP 3: List events from CALENDAR_ID = {CALENDAR_ID}")
print("=" * 60)
try:
    events = service.events().list(
        calendarId=CALENDAR_ID,
        maxResults=50,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    items = events.get("items", [])
    print(f"✅ {len(items)} event(s) found")
    for ev in items[:10]:
        start = ev.get("start", {}).get("dateTime", ev.get("start", {}).get("date", ""))
        attendees = ev.get("attendees", [])
        print(f"  • {start} | {ev.get('summary', '(no title)')} | {len(attendees)} attendees")
except Exception as e:
    print(f"❌ Error: {e}")