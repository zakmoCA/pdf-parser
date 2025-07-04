import imaplib
import email
from email.header import decode_header
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def fetch_relevant_pdf_attachments(download_path: Path):
    from_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    imap_server = "imap.gmail.com"
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(from_email, password)
    mail.select("inbox")

    # Search all emails (newest first)
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()[::-1]  # reverse for latest first

    saved_files = []
    keywords = ["invoice", "purchase", "delivery"]

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = msg.get("Subject", "")
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode(errors="ignore")
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        if any(kw in subject.lower() for kw in keywords) or any(kw in body.lower() for kw in keywords):
            for part in msg.walk():
                content_disposition = str(part.get("Content-Disposition", ""))
                content_type = part.get_content_type()
                filename = part.get_filename()

                if (
                    "attachment" in content_disposition
                    and content_type == "application/pdf"
                    and filename
                    and any(kw in filename.lower() for kw in keywords)
                ):
                    file_path = download_path / filename
                    if not file_path.exists():
                        with open(file_path, "wb") as f:
                            f.write(part.get_payload(decode=True))
                        print(f"✅ Saved: {file_path}")
                    else:
                        print(f"⚠️ File already exists: {file_path}")
                    saved_files.append(file_path)

            if saved_files:
                print(f"📧 Used email with subject: {subject}")
                break  # stop after first relevant email with attachment

    mail.logout()
    return saved_files if saved_files else None
