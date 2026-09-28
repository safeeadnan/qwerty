import os
import sys
from collections import defaultdict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

SUBJECT_NAMES = {
    "Business Insights & Prescriptive Analytics",
    "Digital Innovation & Product Leadership",
    "Advanced OD Consulting and Facilitation Skills",
    "Neuroscience for Managerial and Personal Effectiveness",
    "Strategic Tools and Techniques"
}


def get_calendar_service():
    """OAuth authentication flow."""
    creds = None
    token_file = "token.json"

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                print("[ERROR] credentials.json not found!")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def remove_duplicate_events(service):
    """
    Finds all timetable events in the primary calendar and deletes duplicates,
    keeping only ONE copy of each event.
    """
    print("Fetching calendar events to identify duplicates...\n")

    page_token = None
    all_events = []

    # Retrieve all events from September 2026 onwards
    while True:
        events_result = service.events().list(
            calendarId='primary',
            timeMin='2026-09-01T00:00:00Z',
            singleEvents=False,  # Get the parent recurring series so deleting removes the whole series
            pageToken=page_token
        ).execute()

        items = events_result.get('items', [])
        all_events.extend(items)

        page_token = events_result.get('nextPageToken')
        if not page_token:
            break

    # Group events by summary and start time
    grouped = defaultdict(list)
    for event in all_events:
        summary = event.get('summary', '').strip()
        if summary in SUBJECT_NAMES:
            start_info = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
            recurrence = str(event.get('recurrence', ''))
            key = (summary, start_info, recurrence)
            grouped[key].append(event)

    total_deleted = 0

    for (summary, start_time, recurrence), events_list in grouped.items():
        if len(events_list) > 1:
            print(f"Found {len(events_list)} copies of '{summary}' starting at {start_time}")
            # Keep the first one, delete the rest
            to_keep = events_list[0]
            to_delete = events_list[1:]

            print(f"  Keeping: event ID {to_keep['id']}")
            for dup in to_delete:
                dup_id = dup['id']
                try:
                    service.events().delete(calendarId='primary', eventId=dup_id).execute()
                    print(f"  ✓ Deleted duplicate ID: {dup_id}")
                    total_deleted += 1
                except HttpError as err:
                    print(f"  ✗ Failed to delete {dup_id}: {err}")
            print()
        else:
            print(f"✓ Only 1 copy of '{summary}' ({start_time}) - No action needed.")

    print(f"\nCompleted! Deleted a total of {total_deleted} duplicate events.")
    print("Each lecture is now scheduled exactly ONCE.")


if __name__ == '__main__':
    service = get_calendar_service()
    remove_duplicate_events(service)
