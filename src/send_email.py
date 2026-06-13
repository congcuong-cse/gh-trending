"""Send the rendered digest email over SMTP.

Skips cleanly (exit 0) when mail is not configured, so the daily routine
never fails just because email isn't set up.

Configure via environment variables (e.g. in the trigger / environment):

* ``SMTP_HOST``  - default ``smtp.gmail.com``
* ``SMTP_PORT``  - default ``465`` (implicit TLS)
* ``SMTP_USER``  - sender address / SMTP username  (required to send)
* ``SMTP_PASS``  - SMTP password / Gmail App Password (required to send)
* ``MAIL_TO``    - recipient; default ``congcuong.cse@gmail.com``
"""

from __future__ import annotations

import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    if not user or not password:
        print("SMTP_USER/SMTP_PASS not set — skipping email.")
        return 0

    body_file = ROOT / "email_body.html"
    if not body_file.exists():
        print("email_body.html missing — run render_email.py first. Skipping.")
        return 0

    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))
    recipient = os.environ.get("MAIL_TO", "congcuong.cse@gmail.com")
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    msg = EmailMessage()
    msg["Subject"] = f"GitHub Trending — Top 10 for {date}"
    msg["From"] = f"GitHub Trending Bot <{user}>"
    msg["To"] = recipient
    msg.set_content("Your mail client does not support HTML.")
    msg.add_alternative(body_file.read_text(encoding="utf-8"), subtype="html")

    context = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=context) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
    else:  # STARTTLS (e.g. port 587)
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls(context=context)
            smtp.login(user, password)
            smtp.send_message(msg)

    print(f"Sent digest to {recipient}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
