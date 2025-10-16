import time

import dotenv

from lib.notifications import send_email, send_ntfy_notification


def test_send_email():
    subject = f"CRAB Monitor Manual Test {int(time.time())}"
    body = "This is a manual confirmation email test."

    send_email("Test", "This is a test", "ryansantos1174@gmail.com")
    print("\n📧 An email has been sent. Please check your inbox.")
    confirm = input("Did you receive the email? (y/n): ").strip().lower()

    assert confirm == "y", "Manual confirmation failed — email not received."

def test_send_ntfy():
    send_ntfy_notification("This is a test")
