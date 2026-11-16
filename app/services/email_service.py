import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_ticket_email(ticket_id: int, user_discord_id: str, priority: str, description: str, remaining_time: str):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    if smtp_password:
        smtp_password = smtp_password.replace(" ", "")

    if not smtp_email or not smtp_password:
        print("Missing SMTP_EMAIL or SMTP_PASSWORD in .env")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[TICKET #{ticket_id}] [{priority}] - Remaining Time: {remaining_time}"
        msg["From"] = smtp_email
        msg["To"] = smtp_email

        email_body = (
            f"New IT Support Ticket Submitted!\n\n"
            f"- Ticket ID: #{ticket_id}\n"
            f"- Discord User ID: {user_discord_id}\n"
            f"- Priority: {priority}\n"
            f"- Time Limit (Countdown): {remaining_time}\n"
            f"- Issue Description:\n{description}\n"
        )
        msg.set_content(email_body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_email, smtp_password)
            server.send_message(msg)

        print(f"Sent notification email for Ticket #{ticket_id} to {smtp_email}")
    except Exception as e:
        print(f"Email error: {e}")
