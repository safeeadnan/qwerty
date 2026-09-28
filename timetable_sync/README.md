# Google Calendar Timetable Sync

This script syncs your trimester timetable directly to your primary Google Calendar with 15-minute popup reminders.

## Extracted Timetable

| Day | Date | Subject | Room | Start Time | End Time |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Monday** | 2026-09-28 | Business Insights & Prescriptive Analytics | PT-GND-2 | 10:45 AM | 12:15 PM |
| **Monday** | 2026-09-28 | Digital Innovation & Product Leadership | PT-2-4 | 06:30 PM | 08:00 PM |
| **Tuesday** | 2026-09-29 | Digital Innovation & Product Leadership | PT-1-2 | 10:45 AM | 12:15 PM |
| **Tuesday** | 2026-09-29 | Business Insights & Prescriptive Analytics | PT-GND-2 | 12:30 PM | 02:00 PM |
| **Tuesday** | 2026-09-29 | Advanced OD Consulting and Facilitation Skills | PT-2-5 | 04:45 PM | 06:15 PM |
| **Wednesday** | 2026-09-30 | Neuroscience for Managerial and Personal Effectiveness | PT-1-3 | 09:00 AM | 10:30 AM |
| **Wednesday** | 2026-09-30 | Strategic Tools and Techniques | PT-1-2 | 12:30 PM | 02:00 PM |
| **Wednesday** | 2026-09-30 | Advanced OD Consulting and Facilitation Skills | PT-2-5 | 03:00 PM | 04:30 PM |
| **Friday** | 2026-10-02 | Neuroscience for Managerial and Personal Effectiveness | PT-1-3 | 10:45 AM | 12:15 PM |
| **Friday** | 2026-10-02 | Strategic Tools and Techniques | PT-2-5 | 06:30 PM | 08:00 PM |

## How to Run

1. Place your `credentials.json` file in this directory (`c:\Users\safee\qwerty\`).
2. Run:
   ```bash
   python sync_calendar.py
   ```
3. A browser window will open. Sign in and grant access to manage your calendar events.
