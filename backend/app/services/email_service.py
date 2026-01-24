import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_stock_report_email(buffer: bytes | io.BytesIO, filename: str, recipients: list[str]):
    """
    Fake sending a stock report PDF or Excel via email as attachment.
    Logs the action instead of connecting to SMTP.
    """
    msg = MIMEMultipart()
    msg["Subject"] = "Daily Stock Report"
    msg["From"] = "reports@example.com"
    msg["To"] = ", ".join(recipients)

    # Email body
    body = MIMEText("<p>Please find attached the daily stock report.</p>", "html")
    msg.attach(body)

    # Attachment
    if isinstance(buffer, bytes):
        file_bytes = buffer
    else:
        buffer.seek(0)
        file_bytes = buffer.read()

    attachment = MIMEApplication(file_bytes, Name=filename)
    attachment["Content-Disposition"] = f'attachment; filename="{filename}"'
    msg.attach(attachment)

    # Fake sending email
    print(f"[FAKE EMAIL] To: {recipients}")
    print(f"[FAKE EMAIL] Subject: {msg['Subject']}")
    print(f"[FAKE EMAIL] Filename: {filename}")
    print("[FAKE EMAIL] Email sent successfully (simulated).")
