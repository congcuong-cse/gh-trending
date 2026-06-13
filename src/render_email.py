"""Render today's digest Markdown into an HTML email body.

Reads the dated digest produced by the Claude Code routine
(``archive/<date>.md``) and writes ``email_body.html`` for the mail step.
Also exports the email subject as a GitHub Actions output.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    digest = ROOT / "archive" / f"{date}.md"

    # Fall back to the raw table if the AI digest is missing for some reason.
    if not digest.exists():
        digest = ROOT / "data" / "today.md"

    md_text = digest.read_text(encoding="utf-8")
    html_body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])

    styled = (
        "<div style=\"font-family:-apple-system,Segoe UI,Roboto,sans-serif;"
        "max-width:760px;margin:0 auto;line-height:1.5;color:#1f2328\">"
        f"{html_body}"
        "<hr><p style=\"color:#656d76;font-size:12px\">"
        "Automated daily digest from github.com/trending.</p></div>"
    )

    (ROOT / "email_body.html").write_text(styled, encoding="utf-8")

    subject = f"GitHub Trending — Top 10 for {date}"
    if out := os.environ.get("GITHUB_OUTPUT"):
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"subject={subject}\n")

    print(f"Rendered email for {date} ({len(md_text)} chars of markdown).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
