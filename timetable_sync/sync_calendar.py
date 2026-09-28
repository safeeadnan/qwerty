import os
import sys

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# OAuth Scope required to manage calendar events
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Default timezone for the events
TIMEZONE = 'Asia/Kolkata'

# Extracted timetable lecture events
# Anchored to the week starting Monday, September 28, 2026
LECTURES = [
    # --- MONDAY ---
    {
        "summary": "Business Insights & Prescriptive Analytics",
        "location": "Room: PT-GND-2",
        "start": "2026-09-28T10:45:00",
        "end": "2026-09-28T12:15:00",
    },
    {
        "summary": "Digital Innovation & Product Leadership",
        "location": "Room: PT-2-4",
        "start": "2026-09-28T18:30:00",
        "end": "2026-09-28T20:00:00",
    },
    # --- TUESDAY ---
    {
        "summary": "Digital Innovation & Product Leadership",
        "location": "Room: PT-1-2",
        "start": "2026-09-29T10:45:00",
        "end": "2026-09-29T12:15:00",
    },
    {
        "summary": "Business Insights & Prescriptive Analytics",
        "location": "Room: PT-GND-2",
        "start": "2026-09-29T12:30:00",
        "end": "2026-09-29T14:00:00",
    },
    {
        "summary": "Advanced OD Consulting and Facilitation Skills",
        "location": "Room: PT-2-5",
        "start": "2026-09-29T16:45:00",
        "end": "2026-09-29T18:15:00",
    },
    # --- WEDNESDAY ---
    {
        "summary": "Neuroscience for Managerial and Personal Effectiveness",
        "location": "Room: PT-1-3",
        "start": "2026-09-30T09:00:00",
        "end": "2026-09-30T10:30:00",
    },
    {
        "summary": "Strategic Tools and Techniques",
        "location": "Room: PT-1-2",
        "start": "2026-09-30T12:30:00",
        "end": "2026-09-30T14:00:00",
    },
    {
        "summary": "Advanced OD Consulting and Facilitation Skills",
        "location": "Room: PT-2-5",
        "start": "2026-09-30T15:00:00",
        "end": "2026-09-30T16:30:00",
    },
    # --- FRIDAY ---
    {
        "summary": "Neuroscience for Managerial and Personal Effectiveness",
        "location": "Room: PT-1-3",
        "start": "2026-10-02T10:45:00",
        "end": "2026-10-02T12:15:00",
    },
    {
        "summary": "Strategic Tools and Techniques",
        "location": "Room: PT-2-5",
        "start": "2026-10-02T18:30:00",
        "end": "2026-10-02T20:00:00",
    },
]


def get_calendar_service(credentials_path="credentials.json", token_path="token.json"):
    """Handles OAuth 2.0 flow and returns an authenticated Google Calendar API service instance."""
    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"\n[ERROR] '{credentials_path}' was not found in: {os.path.abspath('.')}")
                print("\nPlease follow these steps to place it here:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Navigate to APIs & Services > Credentials.")
                print("3. Create an OAuth 2.0 Client ID (Application type: Desktop app).")
                print("4. Download the JSON, rename it to 'credentials.json', and place it in this directory.")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token_file:
            token_file.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


# Subject color mapping for Google Calendar
SUBJECT_COLORS = {
    "Business Insights & Prescriptive Analytics": "7",             # Peacock (Blue)
    "Digital Innovation & Product Leadership": "6",                # Tangerine (Orange)
    "Advanced OD Consulting and Facilitation Skills": "3",         # Grape (Purple)
    "Neuroscience for Managerial and Personal Effectiveness": "4", # Flamingo (Pink)
    "Strategic Tools and Techniques": "10",                        # Basil (Green)
}


def sync_events(service, repeat_weekly=True, weeks=12):
    """Inserts timetable lectures into primary calendar, skipping any that already exist."""
    print(f"Checking primary calendar for existing events...\n")

    # Fetch existing events to prevent duplicates
    existing_events = service.events().list(
        calendarId="primary",
        timeMin="2026-09-28T00:00:00Z",
        timeMax="2026-10-05T00:00:00Z",
        singleEvents=False,
    ).execute().get("items", [])

    existing_signatures = set()
    for item in existing_events:
        summary = item.get("summary", "")
        start_time = item.get("start", {}).get("dateTime", "")
        if summary and start_time:
            existing_signatures.add((summary, start_time[:19]))

    print(f"Pushing {len(LECTURES)} lecture events to Google Calendar (Primary)...\n")

    for idx, lecture in enumerate(LECTURES, start=1):
        lecture_sig = (lecture["summary"], lecture["start"][:19])
        if lecture_sig in existing_signatures:
            print(f"[{idx}/{len(LECTURES)}] Skipping already existing: {lecture['summary']} ({lecture['start']})")
            continue

        event_body = {
            "summary": lecture["summary"],
            "location": lecture["location"],
            "description": f"Trimester Lecture\nCourse: {lecture['summary']}\nLocation: {lecture['location']}",
            "colorId": SUBJECT_COLORS.get(lecture["summary"], "7"),
            "start": {
                "dateTime": f"{lecture['start']}+05:30",
                "timeZone": TIMEZONE,
            },
            "end": {
                "dateTime": f"{lecture['end']}+05:30",
                "timeZone": TIMEZONE,
            },
            # Explicit 15-minute popup reminder as required
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 15}
                ],
            },
        }

        # Optional recurrence rule across the trimester/semester
        if repeat_weekly:
            event_body["recurrence"] = [f"RRULE:FREQ=WEEKLY;COUNT={weeks}"]

        try:
            created_event = service.events().insert(calendarId="primary", body=event_body).execute()
            print(f"[{idx}/{len(LECTURES)}] Added: {lecture['summary']}")
            print(f"      Time: {lecture['start']} -> {lecture['end']}")
            print(f"      Room: {lecture['location']}")
            print(f"      Link: {created_event.get('htmlLink')}\n")
        except HttpError as err:
            print(f"[{idx}/{len(LECTURES)}] Failed to add '{lecture['summary']}': {err}\n")

    print("Sync process completed!")


if __name__ == "__main__":
    service = get_calendar_service()
    # repeat_weekly=True will schedule each lecture weekly for 12 weeks
    sync_events(service, repeat_weekly=True, weeks=12)
