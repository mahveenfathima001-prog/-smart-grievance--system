# notification.py
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# ✅ CORRECT — variable names inside os.getenv()
ACCOUNT_SID   = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN")
WHATSAPP_FROM = "whatsapp:+14155238886"

if ACCOUNT_SID and AUTH_TOKEN:
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    print("✅ Twilio client ready!")
else:
    client = None
    print("⚠️ Twilio credentials not found!")


def send_whatsapp(to_number, message):
    if not client:
        print("⚠️ Twilio not configured")
        return False
    try:
        to_number = to_number.strip().replace(" ", "").replace("-", "")
        if not to_number.startswith('+'):
            to_number = '+91' + to_number

        msg = client.messages.create(
            body  = message,
            from_ = WHATSAPP_FROM,
            to    = f"whatsapp:{to_number}"
        )
        print(f"✅ WhatsApp sent! SID: {msg.sid}")
        return True

    except Exception as e:
        print(f"❌ WhatsApp failed: {e}")
        return False


def send_sms(to_number, message):
    print("⚠️ SMS skipped — no phone number purchased")
    return False


def notify_citizen(to_number, subject, message):
    if not to_number:
        print("⚠️ No contact number")
        return
    print(f"📱 Notifying: {to_number}")
    send_whatsapp(to_number, message)


def complaint_submitted_msg(complaint_id, category, department):
    return f"""
✅ *Grievance Submitted Successfully!*

🆔 Complaint ID: *#{complaint_id}*
📂 Category: {category}
🏢 Department: {department}
📊 Status: Pending

🔍 Track your complaint:
http://127.0.0.1:5000/track

— Smart Grievance Portal 🏛
"""


def status_updated_msg(complaint_id, new_status, title):
    emoji = {
        "Pending":     "🟡",
        "In Progress": "🔵",
        "Resolved":    "✅"
    }
    e = emoji.get(new_status, "📋")
    return f"""
{e} *Complaint Status Update*

🆔 Complaint ID: *#{complaint_id}*
📝 Title: {title}
📊 New Status: *{new_status}*

🔍 Track your complaint:
http://127.0.0.1:5000/track

— Smart Grievance Portal 🏛
"""