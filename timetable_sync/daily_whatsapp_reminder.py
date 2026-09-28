import os
import sys
import urllib.parse
from datetime import datetime
import requests

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# 1. Add CallMeBot to your WhatsApp contacts (+34 644 10 55 84 or +34 644 65 32 96).
# 2. Send the message: "I allow callmebot to send me messages"
# 3. CallMeBot will reply with your personal API key.
# 4. Fill in your phone number with country code (e.g., "+919876543210") and API key below:
PHONE_NUMBER = os.getenv("WHATSAPP_PHONE", "+917620410836")  # Replace with your phone number
API_KEY = os.getenv("CALLMEBOT_API_KEY", "YOUR_API_KEY")     # Replace with your CallMeBot API key

# Weekly schedule mapping
WEEKLY_SCHEDULE = {
    0: {  # Monday
        "day_name": "Monday",
        "classes": [
            {
                "time": "10:45 AM – 12:15 PM",
                "subject": "Business Insights & Prescriptive Analytics",
                "room": "PT-GND-2",
            },
            {
                "time": "06:30 PM – 08:00 PM",
                "subject": "Digital Innovation & Product Leadership",
                "room": "PT-2-4",
            },
        ],
    },
    1: {  # Tuesday
        "day_name": "Tuesday",
        "classes": [
            {
                "time": "10:45 AM – 12:15 PM",
                "subject": "Digital Innovation & Product Leadership",
                "room": "PT-1-2",
            },
            {
                "time": "12:30 PM – 02:00 PM",
                "subject": "Business Insights & Prescriptive Analytics",
                "room": "PT-GND-2",
            },
            {
                "time": "04:45 PM – 06:15 PM",
                "subject": "Advanced OD Consulting and Facilitation Skills",
                "room": "PT-2-5",
            },
        ],
    },
    2: {  # Wednesday
        "day_name": "Wednesday",
        "classes": [
            {
                "time": "09:00 AM – 10:30 AM",
                "subject": "Neuroscience for Managerial and Personal Effectiveness",
                "room": "PT-1-3",
            },
            {
                "time": "12:30 PM – 02:00 PM",
                "subject": "Strategic Tools and Techniques",
                "room": "PT-1-2",
            },
            {
                "time": "03:00 PM – 04:30 PM",
                "subject": "Advanced OD Consulting and Facilitation Skills",
                "room": "PT-2-5",
            },
        ],
    },
    3: {  # Thursday
        "day_name": "Thursday",
        "classes": [],  # Free day
    },
    4: {  # Friday
        "day_name": "Friday",
        "classes": [
            {
                "time": "10:45 AM – 12:15 PM",
                "subject": "Neuroscience for Managerial and Personal Effectiveness",
                "room": "PT-1-3",
            },
            {
                "time": "06:30 PM – 08:00 PM",
                "subject": "Strategic Tools and Techniques",
                "room": "PT-2-5",
            },
        ],
    },
    5: {  # Saturday
        "day_name": "Saturday",
        "classes": [],
    },
    6: {  # Sunday
        "day_name": "Sunday",
        "classes": [],
    },
}


def build_daily_message(day_idx=None):
    """Generates the formatted WhatsApp message for a given day (defaults to today)."""
    now = datetime.now()
    if day_idx is None:
        day_idx = now.weekday()

    schedule_data = WEEKLY_SCHEDULE.get(day_idx, {"day_name": "Today", "classes": []})
    day_name = schedule_data["day_name"]
    classes = schedule_data["classes"]

    date_str = now.strftime("%d %b %Y")

    if not classes:
        msg = (
            f"🎉 *Good Morning!*\n"
            f"📅 *{day_name}, {date_str}*\n\n"
            f"✨ No lectures scheduled for today! Enjoy your free time or use it for self-study. ☕"
        )
        return msg

    msg_lines = [
        f"🎓 *Daily Class Schedule - {day_name}*",
        f"📅 {date_str}",
        f"━━━━━━━━━━━━━━━━━━━",
        f"You have *{len(classes)} lecture{'s' if len(classes) > 1 else ''}* today:\n",
    ]

    for idx, c in enumerate(classes, start=1):
        msg_lines.append(f"{idx}️⃣ *{c['subject']}*")
        msg_lines.append(f"   ⏰ {c['time']}")
        msg_lines.append(f"   📍 Room: *{c['room']}*\n")

    msg_lines.append("━━━━━━━━━━━━━━━━━━━")
    msg_lines.append("Have a great and productive day! 🚀")

    return "\n".join(msg_lines)


def send_whatsapp_message(message, phone=PHONE_NUMBER, api_key=API_KEY):
    """Sends the WhatsApp message via the CallMeBot API gateway."""
    if "XXXXXXXXXX" in phone or api_key == "YOUR_API_KEY":
        print("\n[INFO] WhatsApp phone number or API key not yet configured!")
        print("Here is a preview of the message that would be sent:\n")
        print("--------------------------------------------------")
        print(message)
        print("--------------------------------------------------")
        print("\nTo send real WhatsApp messages:")
        print("1. Get your free API key from CallMeBot (instructions in README or terminal).")
        print("2. Update PHONE_NUMBER and API_KEY in 'daily_whatsapp_reminder.py'.")
        return False

    encoded_text = urllib.parse.quote(message)
    # Ensure phone number doesn't have '+' in query param for CallMeBot
    clean_phone = phone.replace("+", "").replace(" ", "").strip()
    url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_text}&apikey={api_key}"

    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            print(f"✓ WhatsApp reminder successfully sent to {phone}!")
            return True
        else:
            print(f"✗ Failed to send WhatsApp message. Server returned HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Network error while sending WhatsApp message: {e}")
        return False


if __name__ == "__main__":
    # Check if a specific day preview was requested (e.g. `python daily_whatsapp_reminder.py --day 0`)
    day_arg = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        day_arg = int(sys.argv[1])

    message = build_daily_message(day_arg)

    if "--preview" in sys.argv:
        print("\n--- WhatsApp Message Preview ---")
        print(message)
        print("--------------------------------\n")
    else:
        send_whatsapp_message(message)
