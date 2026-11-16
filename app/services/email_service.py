import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_ticket_email(ticket_id: int, user_discord_id: str, priority: str, description: str, remaining_time: str):
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    admin_email = os.getenv("ADMIN_EMAIL")

    if not smtp_email or not smtp_password or not admin_email:
        print("Chua cau hinh SMTP_EMAIL, SMTP_PASSWORD hoac ADMIN_EMAIL trong file .env")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[TICKET #{ticket_id}] [{priority}] - Remaining Time: {remaining_time}"
        msg["From"] = smtp_email
        msg["To"] = admin_email

        noi_dung_email = (
            f"New IT Support Ticket Submitted!\n\n"
            f"- Ticket ID: #{ticket_id}\n"
            f"- Discord User ID: {user_discord_id}\n"
            f"- Priority: {priority}\n"
            f"- Time Limit (Countdown): {remaining_time}\n"
            f"- Issue Description:\n{description}\n"
        )
        msg.set_content(noi_dung_email)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_email, smtp_password)
            server.send_message(msg)

        print(f"Da gui email thong bao Ticket #{ticket_id} toi {admin_email}")
    except Exception as e:
        print(f"Loi khi gui email: {e}")
