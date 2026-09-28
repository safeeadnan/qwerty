import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Ensure proper utf-8 encoding on Windows terminals
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

SCOPES = ['https://www.googleapis.com/auth/calendar.events']

# Subject color mapping:
# 7: Peacock (Blue)
# 6: Tangerine (Orange)
# 3: Grape (Purple)
# 4: Flamingo (Pink)
# 10: Basil (Green)
SUBJECT_COLORS = {
    "Business Insights & Prescriptive Analytics": {
        "colorId": "7",
        "colorName": "Peacock (Cyan/Blue)"
    },
    "Digital Innovation & Product Leadership": {
        "colorId": "6",
        "colorName": "Tangerine (Orange)"
    },
    "Advanced OD Consulting and Facilitation Skills": {
        "colorId": "3",
        "colorName": "Grape (Purple)"
    },
    "Neuroscience for Managerial and Personal Effectiveness": {
        "colorId": "4",
        "colorName": "Flamingo (Pink)"
    },
    "Strategic Tools and Techniques": {
        "colorId": "10",
        "colorName": "Basil (Green)"
    }
}


def get_calendar_service(credentials_path="credentials.json", token_path="token.json"):
    """OAuth authentication flow."""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print(f"[ERROR] '{credentials_path}' not found!")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def apply_color_coding(service):
    """Fetches timetable events and applies custom color coding to each subject."""
    print("Fetching calendar events to color-code...\n")

    page_token = None
    updated_count = 0

    while True:
        events_result = service.events().list(
            calendarId='primary',
            timeMin='2026-09-01T00:00:00Z',
            singleEvents=False,  # Update parent recurring series so all weeks inherit the color
            pageToken=page_token
        ).execute()

        events = events_result.get('items', [])
        for event in events:
            summary = event.get('summary', '').strip()
            if summary in SUBJECT_COLORS:
                color_info = SUBJECT_COLORS[summary]
                color_id = color_info["colorId"]
                color_name = color_info["colorName"]

                current_color = event.get('colorId')
                if current_color != color_id:
                    try:
                        service.events().patch(
                            calendarId='primary',
                            eventId=event['id'],
                            body={'colorId': color_id}
                        ).execute()
                        print(f"🎨 Updated '{summary}' -> {color_name}")
                        updated_count += 1
                    except HttpError as err:
                        print(f"✗ Failed to color '{summary}': {err}")
                else:
                    print(f"✓ '{summary}' already has color {color_name}")

        page_token = events_result.get('nextPageToken')
        if not page_token:
            break

    print(f"\nDone! Color-coded {updated_count} event series successfully.")


if __name__ == '__main__':
    service = get_calendar_service()
    apply_color_coding(service)
