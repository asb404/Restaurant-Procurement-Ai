import imaplib
import os
from email import message_from_bytes
from email.message import Message
from email.utils import parseaddr


def _extract_plain_text(msg: Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True) or b""
                return payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
        return ""
    payload = msg.get_payload(decode=True) or b""
    return payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")


def fetch_recent_quote_emails() -> list[dict]:
    email_address = os.getenv("EMAIL_ADDRESS", "")
    email_password = os.getenv("EMAIL_PASSWORD", "")
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
    imap_port = int(os.getenv("IMAP_PORT", "993"))

    if not email_address or not email_password:
        print("Inbox monitor skipped: missing EMAIL_ADDRESS or EMAIL_PASSWORD")
        return []

    results: list[dict] = []
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)
    try:
        mail.login(email_address, email_password)
        mail.select("INBOX")

        status, data = mail.search(None, "ALL")
        if status != "OK":
            return []

        message_ids = data[0].split()
        recent = message_ids[-5:]

        for msg_id in reversed(recent):
            fetch_status, msg_data = mail.fetch(msg_id, "(RFC822)")
            if fetch_status != "OK" or not msg_data:
                continue

            raw = msg_data[0][1]
            msg = message_from_bytes(raw)

            subject = str(msg.get("Subject", ""))
            if "quote" not in subject.lower() and "rfq" not in subject.lower():
                continue

            from_email = parseaddr(str(msg.get("From", "")))[1]
            message_id = str(msg.get("Message-ID", "")).strip()
            body = _extract_plain_text(msg)

            results.append(
                {
                    "message_id": message_id,
                    "from_email": from_email,
                    "subject": subject,
                    "body": body,
                }
            )
    finally:
        try:
            mail.logout()
        except Exception:
            pass

    return results
