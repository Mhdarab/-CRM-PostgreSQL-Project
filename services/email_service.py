import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


load_dotenv()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SMTP_USER = os.getenv("CRM_EMAIL", "").strip()
SMTP_PASS = os.getenv("CRM_PASSWORD", "").strip().replace(" ", "")


def send_email(to_email, subject, body, dry_run=False):
    """Send one email. If creds missing → dry-run (print only)."""
    if dry_run:
        print(f"[DRY RUN] → {to_email} | {subject}")
        return True
    if not SMTP_USER or not SMTP_PASS:
        print("❌ CRM_EMAIL / CRM_PASSWORD missing in .env - nothing was sent")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        print(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send to {to_email}: {e}")
        return False


def send_event_emails(event, dry_run=True):
    subject = f"Reminder: {event['title']} on {event['date']} at {event['time']}"
    body = (
        f"Hello,\n\n"
        f"You are invited to the following event:\n\n"
        f"📌 Title:    {event['title']}\n"
        f"📅 Date:     {event['date']}\n"
        f"⏰ Time:     {event['time']}\n"
        f"📍 Location: {event.get('location', 'N/A')}\n\n"
        f"Best regards,\nWEAR:HERE Team"
    )

    results = []
    for email in event.get("participants", []):
        ok = send_email(email, subject, body, dry_run=dry_run)
        results.append((email, ok))
    return results