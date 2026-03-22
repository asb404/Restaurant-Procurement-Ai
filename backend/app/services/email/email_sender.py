import os
import smtplib
from email.message import EmailMessage


def send_email(to_email: str, subject: str, body: str) -> None:
    from_email = "abhavsar964@gmail.com"
    app_password = os.getenv("EMAIL_PASSWORD", "")
    recipient_email = "asb4420@gmail.com"

    if not app_password:
        print("Email send failed: EMAIL_PASSWORD is not set")
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = from_email
    message["To"] = recipient_email
    message.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(from_email, app_password)
            smtp.send_message(message)
    except Exception as error:
        print(f"Email send failed: {error}")
