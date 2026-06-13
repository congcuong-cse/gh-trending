"""Send the rendered digest email via the Resend HTTPS API, with SMTP fallback.

Skips cleanly (exit 0) when mail is not configured, so the daily routine
never fails just because email isn't set up.

Configure via environment variables (e.g. in the trigger / environment):

* ``RESEND_API_KEY`` - API key from resend.com (preferred: works over HTTPS,
  so it isn't blocked by network policies that only allow port 443).
* ``MAIL_FROM``      - sender address; default ``onboarding@resend.dev``
* ``MAIL_TO``        - recipient; default ``congcuong.cse@gmail.com``

SMTP fallback (used only if ``RESEND_API_KEY`` is not set):

* ``SMTP_HOST``  - default ``smtp.gmail.com``
* ``SMTP_PORT``  - default ``465`` (implicit TLS)
* ``SMTP_USER``  - sender address / SMTP username  (required to send)
* ``SMTP_PASS``  - SMTP password / Gmail App Password (required to send)
"""

from __future__ import annotations

import os
import smtplib
import ssl
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent


def _send_via_resend(api_key: str, body_file: Path, subject: str, recipient: str) -> None:
    sender = os.environ.get("MAIL_FROM", "onboarding@resend.dev")
    response = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "from": f"GitHub Trending Bot <{sender}>",
            "to": [recipient],
            "subject": subject,
            "html": body_file.read_text(encoding="utf-8"),
        },
        timeout=30,
    )
    response.raise_for_status()


def _send_via_smtp(user: str, password: str, body_file: Path, subject: str, recipient: str) -> None:
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))

    msg = EmailMessage()
    msg["Subject"] = subject
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


def main() -> int:
    resend_key = os.environ.get("RESEND_API_KEY")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")

    if not resend_key and not (user and password):
        print("Neither RESEND_API_KEY nor SMTP_USER/SMTP_PASS set — skipping email.")
        return 0

    body_file = ROOT / "email_body.html"
    if not body_file.exists():
        print("email_body.html missing — run render_email.py first. Skipping.")
        return 0

    recipient = os.environ.get("MAIL_TO", "congcuong.cse@gmail.com")
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    subject = f"GitHub Trending — Top 10 for {date}"

    if resend_key:
        _send_via_resend(resend_key, body_file, subject, recipient)
    else:
        _send_via_smtp(user, password, body_file, subject, recipient)

    print(f"Sent digest to {recipient}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
