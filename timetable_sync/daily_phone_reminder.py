import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
import requests

# Indian Standard Time (IST) UTC+05:30
IST = timezone(timedelta(hours=5, minutes=30))

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# ==============================================================================
# CONFIGURATION
# ==============================================================================
# 1. PHONE PUSH NOTIFICATION (via free ntfy.sh - zero setup required!):
# Just choose any unique topic name (e.g., 'safee-mba-classes-836')
NTFY_TOPIC = "safee-mba-classes-836"

# 2. DAILY EMAIL CONFIGURATION:
# Recipient email address (your phone's Gmail/email app will receive this)
RECIPIENT_EMAIL = "safeeadnan@gmail.com"  # Update with your desired recipient email

# Sender Gmail settings (optional - requires a Gmail App Password)
# Generate from: https://myaccount.google.com/apppasswords
SENDER_EMAIL = ""         # e.g., yourgmail@gmail.com
GMAIL_APP_PASSWORD = ""   # 16-character app password (not your normal password)

# ==============================================================================
# WEEKLY TIMETABLE DATA
# ==============================================================================
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


def get_today_schedule(day_idx=None):
    now = datetime.now(IST)
    if day_idx is None:
        day_idx = now.weekday()
    return WEEKLY_SCHEDULE.get(day_idx, {"day_name": "Today", "classes": []}), now


def send_phone_push_notification(day_idx=None):
    """
    Sends a rich, beautifully formatted push notification directly to your phone via ntfy.sh.
    Features:
    - Full Markdown support (bold, code blocks, bullet trees)
    - Action buttons (One-tap open Google Calendar)
    - Custom icons, emojis, and priority tags
    """
    schedule_data, now = get_today_schedule(day_idx)
    day_name = schedule_data["day_name"]
    classes = schedule_data["classes"]
    date_str = now.strftime("%A, %d %B %Y")

    if not classes:
        title = f"☀️ Free Day! • {day_name}"
        body_lines = [
            f"📅 **{date_str}**",
            "━━━━━━━━━━━━━━━━━━━━━━",
            "🎉 **No lectures scheduled for today!**",
            "",
            "✨ Perfect time for:",
            "  ☕ Catching up on sleep & coffee",
            "  📖 Reading case studies & assignments",
            "  🏃 Relaxing and recharging",
            "━━━━━━━━━━━━━━━━━━━━━━",
            "Enjoy your day off! 🌟"
        ]
        tags = ["tada", "sunny", "coffee"]
        priority = 3
    else:
        title = f"🎓 {len(classes)} Class{'es' if len(classes) > 1 else ''} Today • {day_name}"
        body_lines = [
            f"📅 **{date_str}**",
            f"⚡ **Schedule Overview ({len(classes)} Sessions)**",
            "━━━━━━━━━━━━━━━━━━━━━━",
            ""
        ]

        subject_emojis = {
            "Business Insights & Prescriptive Analytics": "📊",
            "Digital Innovation & Product Leadership": "💡",
            "Advanced OD Consulting and Facilitation Skills": "🤝",
            "Neuroscience for Managerial and Personal Effectiveness": "🧠",
            "Strategic Tools and Techniques": "🎯",
        }

        for idx, c in enumerate(classes, start=1):
            emoji = subject_emojis.get(c['subject'], "📚")
            body_lines.append(f"{emoji} **{idx}. {c['subject']}**")
            body_lines.append(f"   ├ ⏰ **{c['time']}**")
            body_lines.append(f"   └ 📍 Room: `{c['room']}`")
            body_lines.append("")

        body_lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        body_lines.append("💡 *Have a productive and impactful day!* 🚀")
        tags = ["mortarboard", "calendar", "alarm_clock"]
        priority = 4

    payload = {
        "topic": NTFY_TOPIC,
        "title": title,
        "message": "\n".join(body_lines),
        "priority": 4 if classes else 3,
        "tags": tags,
        "markdown": True,
        "click": "https://calendar.google.com",
        "actions": [
            {
                "action": "view",
                "label": "📅 Open Google Calendar",
                "url": "https://calendar.google.com"
            }
        ]
    }

    try:
        response = requests.post("https://ntfy.sh", json=payload, timeout=10)
        if response.status_code == 200:
            print(f"✓ Premium rich push notification sent to topic: '{NTFY_TOPIC}'!")
            print(f"  Title: {title}")
            return True
        else:
            print(f"✗ Push failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error sending push notification: {e}")
        return False


def send_daily_email(day_idx=None):
    """Sends a formatted daily class timetable email to your inbox."""
    if not SENDER_EMAIL or not GMAIL_APP_PASSWORD:
        print("\n[NOTE] Email sending skipped (SENDER_EMAIL / GMAIL_APP_PASSWORD not set).")
        print("To enable email reminders, add your Gmail App Password to daily_phone_reminder.py.")
        return False

    schedule_data, now = get_today_schedule(day_idx)
    day_name = schedule_data["day_name"]
    classes = schedule_data["classes"]
    date_str = now.strftime("%d %b %Y")

    subject = f"🎓 Timetable Briefing: {day_name}, {date_str}"

    if not classes:
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #2b7de9;">Good Morning! ☀️</h2>
            <p style="font-size: 16px;">Today is <strong>{day_name}, {date_str}</strong>.</p>
            <p style="font-size: 15px; color: #555;">No lectures are scheduled for today. Enjoy your day! ☕</p>
        </div>
        """
    else:
        cards_html = ""
        for idx, c in enumerate(classes, start=1):
            cards_html += f"""
            <div style="background-color: #f8f9fa; border-left: 4px solid #1a73e8; padding: 12px 16px; margin-bottom: 12px; border-radius: 4px;">
                <h3 style="margin: 0 0 6px 0; color: #202124;">{idx}. {c['subject']}</h3>
                <p style="margin: 4px 0; color: #5f6368; font-size: 14px;"><strong>⏰ Time:</strong> {c['time']}</p>
                <p style="margin: 4px 0; color: #5f6368; font-size: 14px;"><strong>📍 Room:</strong> {c['room']}</p>
            </div>
            """

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #1a73e8; margin-top: 0;">🎓 Class Schedule for Today</h2>
            <p style="font-size: 15px; color: #3c4043;"><strong>{day_name}, {date_str}</strong> • {len(classes)} lecture(s)</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 16px 0;" />
            {cards_html}
            <p style="color: #888; font-size: 12px; margin-top: 20px;">Have a productive day! 🚀</p>
        </div>
        """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print(f"✓ Daily briefing email successfully sent to {RECIPIENT_EMAIL}!")
        return True
    except Exception as e:
        print(f"✗ Failed to send email: {e}")
        return False


if __name__ == "__main__":
    # Test push notification
    print("--- Sending Phone Push Notification ---")
    send_phone_push_notification()

    # Attempt email if configured
    send_daily_email()
