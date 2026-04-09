"""
FILE: modules/email_sender.py
PURPOSE: Send bulk emails via SMTP from CSV recipient list
"""

import smtplib
import csv
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

from config import (
    EMAIL_HOST, EMAIL_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, RECIPIENTS_CSV
)

logger = logging.getLogger("EmailSender")


class EmailSender:
    """Send personalized bulk emails via SMTP."""

    def __init__(self):
        self.sent = 0
        self.failed = 0
        self.log_entries = []

    def _connect(self):
        """Create and return SMTP connection."""
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        return server

    def send_single(self, to_email, subject, body, name=""):
        """Send a single email."""
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            return {"success": False, "error": "Email credentials not configured"}

        try:
            msg = MIMEMultipart()
            msg["From"] = EMAIL_ADDRESS
            msg["To"] = to_email
            msg["Subject"] = subject

            personalized_body = body.replace("{name}", name)
            msg.attach(MIMEText(personalized_body, "plain"))

            server = self._connect()
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
            server.quit()

            self.sent += 1
            self.log_entries.append({"to": to_email, "status": "sent"})
            logger.info(f"Email sent to {to_email}")
            return {"success": True}

        except Exception as e:
            self.failed += 1
            self.log_entries.append({"to": to_email, "status": "failed", "error": str(e)})
            logger.error(f"Failed to send to {to_email}: {e}")
            return {"success": False, "error": str(e)}

    def send_bulk(self, csv_path=None):
        """Send emails to all recipients in a CSV file."""
        path = Path(csv_path) if csv_path else RECIPIENTS_CSV
        if not path.exists():
            logger.error(f"CSV not found: {path}")
            return {"success": False, "error": "CSV file not found"}

        results = []
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Case-insensitive header lookup
                    lowered_row = {k.lower(): v for k, v in row.items()}
                    result = self.send_single(
                        to_email=lowered_row.get("email", ""),
                        subject=lowered_row.get("subject", "Message"),
                        body=lowered_row.get("message", ""),
                        name=lowered_row.get("name", ""),
                    )
                    results.append({**row, **result})

        except Exception as e:
            logger.error(f"Bulk send failed: {e}")
            return {"success": False, "error": str(e)}

        return {
            "success": True,
            "sent": self.sent,
            "failed": self.failed,
            "results": results,
        }

    def preview_recipients(self, csv_path=None):
        """Read recipient list without sending."""
        path = Path(csv_path) if csv_path else RECIPIENTS_CSV
        if not path.exists():
            return []
        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return [{k.lower(): v for k, v in row.items()} for row in reader]
        except Exception:
            return []

    def run(self):
        """CLI entry point."""
        print("\n" + "═" * 55)
        print("  📧 EMAIL SENDER")
        print("═" * 55)

        recipients = self.preview_recipients()
        if not recipients:
            print("  ℹ️  No recipients found in CSV.")
            return

        print(f"\n  Recipients: {len(recipients)}")
        for r in recipients[:5]:
            print(f"    • {r.get('name', '')} <{r.get('email', '')}>")

        confirm = input("\n  Send emails now? (y/n): ").strip().lower()
        if confirm == "y":
            result = self.send_bulk()
            print(f"\n  ✅ Sent: {result['sent']}")
            print(f"  ❌ Failed: {result['failed']}")
