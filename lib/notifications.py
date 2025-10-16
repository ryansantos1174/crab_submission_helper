import os
import logging

import dotenv
import smtplib
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


dotenv.load_dotenv()
app_password = os.environ["GMAIL_APP_PASSWORD"]
ntfy_topic = os.environ["NTFY_TOPIC"]

def send_email(subject: str, body: str, to_email: str):
    if not app_password:
        logger.error("An app password has not been set in your .env file. Please set that up before"
        "attempting to setup an email")
        return
    # Edit these:
    from_email = "crab.helper.monitoring@gmail.com"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "crab.helper.monitoring@gmail.com"
    password = app_password  # Not your normal password!

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def send_ntfy_notification(message:str):
    if not ntfy_topic:
        logger.error("A ntfy topic has not been set in your .env file. Please set that up before"
        "attempting to send an ntfy notification")

    import requests
    requests.post(ntfy_topic,
    data=message.encode(encoding='utf-8'))
