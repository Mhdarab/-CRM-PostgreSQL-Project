"""
Google Calendar Service
Author: Waseem

Reads events from a Google Calendar using a service account.
"""

import os
from datetime import datetime, timezone

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


# --------------------------------------------------
# CONFIG
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials", "service_account.json")

# 👉 Paste your Calendar ID here
CALENDAR_ID = "isaacwaseem257@gmail.com"

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


# --------------------------------------------------
# AUTH
# --------------------------------------------------
def _get_service():
    creds = Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


# --------------------------------------------------
# FETCH EVENTS
# --------------------------------------------------
def fetch_events(max_results=50, time_min=None):
    """
    Return a list of events from the calendar.
    Each event is returned as a dict with keys:
        id, title, date, time, participants, location, description
    """
    service = _get_service()

    
    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=time_min,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    raw_events = events_result.get("items", [])
    return [_normalize(ev) for ev in raw_events]


def _normalize(event):
    """Convert a Google Calendar event to our internal dict shape."""
    start = event.get("start", {})
    start_dt = start.get("dateTime") or start.get("date", "")

    # Split date and time
    if "T" in start_dt:
        date_part, time_part = start_dt.split("T")
        time_part = time_part[:5]  # HH:MM
    else:
        date_part = start_dt
        time_part = "All day"

    participants = [a.get("email") for a in event.get("attendees", []) if a.get("email")]

    return {
        "id": event.get("id", ""),
        "title": event.get("summary", "(No title)"),
        "date": date_part,
        "time": time_part,
        "location": event.get("location", ""),
        "description": event.get("description", ""),
        "participants": participants,
    }


def get_event_by_id(event_id):
    """Return one event by ID."""
    service = _get_service()
    event = service.events().get(calendarId=CALENDAR_ID, eventId=event_id).execute()
    return _normalize(event)