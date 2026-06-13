# 📈 Daily GitHub Trending Summary

An automated digest of the **top 10 trending GitHub repositories**, refreshed
every day and summarized by a **scheduled Claude Code session** — no API key
required.

## How it works

```
Daily scheduled Claude Code session (a "trigger" on Claude Code for web)
        │  follows the routine in CLAUDE.md
        ▼
  src/fetch_trending.py   → scrapes github.com/trending → data/today.json + data/today.md
        │
        ▼
  Claude (the routine)    → reads the data, writes archive/<date>.md, updates this README
        │
        ▼
  src/render_email.py + src/send_email.py → emails the digest (optional)
        │
        ▼
  git commit & push       → digest archived in the repo
```

- **No official API**: GitHub doesn't expose trending data, so we scrape the
  public HTML page (`src/fetch_trending.py`). The parser targets stable
  `article.Box-row` elements.
- **No `ANTHROPIC_API_KEY`**: the summary is written by Claude Code itself when
  the daily routine runs. The steps live in [`CLAUDE.md`](CLAUDE.md).
- **Archive**: every day's digest is committed under [`archive/`](archive/).
- **Email (optional)**: sent via the [Resend](https://resend.com) HTTPS API when
  `RESEND_API_KEY` is set (works even when only port 443 egress is allowed), or
  via SMTP when `SMTP_USER`/`SMTP_PASS` are set; otherwise the email step is
  skipped.

## Trigger the daily routine

Set up a **scheduled session** in Claude Code for web
([docs](https://code.claude.com/docs/en/claude-code-on-the-web)):

1. Open this repo's environment in Claude Code for web.
2. Create a **scheduled trigger** that runs daily with the prompt:
   > Run the daily GitHub Trending routine described in `CLAUDE.md`.
3. Claude will fetch, summarize, (optionally) email, commit and push — on its own.

To run it **on demand**, just start a session and give it the same prompt.

## Email setup (optional)

Set these as environment variables in the environment (Settings → Environment).

**Option A — Resend (recommended)**: uses HTTPS, so it works under network
policies that only allow port 443 egress.

| Variable         | Purpose                                  | Default                |
|------------------|-------------------------------------------|------------------------|
| `RESEND_API_KEY` | API key from [resend.com](https://resend.com) (**required**) | — |
| `MAIL_FROM`      | sender address                           | `onboarding@resend.dev` |
| `MAIL_TO`        | recipient                                | `congcuong.cse@gmail.com` |

**Option B — SMTP** (used only if `RESEND_API_KEY` is not set; requires the
environment to allow outbound traffic on port 465/587):

| Variable    | Purpose                                            | Default              |
|-------------|----------------------------------------------------|----------------------|
| `SMTP_USER` | sender address / SMTP username (**required**)      | —                    |
| `SMTP_PASS` | SMTP password / Gmail [App Password](https://support.google.com/accounts/answer/185833) (**required**) | — |
| `MAIL_TO`   | recipient                                          | `congcuong.cse@gmail.com` |
| `SMTP_HOST` | SMTP server                                        | `smtp.gmail.com`     |
| `SMTP_PORT` | `465` (SSL) or `587` (STARTTLS)                    | `465`                |

If neither `RESEND_API_KEY` nor `SMTP_USER`/`SMTP_PASS` are set,
`send_email.py` exits cleanly and the rest of the routine still runs.

## Run locally

```bash
pip install -r requirements.txt
python src/fetch_trending.py        # writes data/today.json and data/today.md
# (then summarize by hand or let Claude do it, then:)
python src/render_email.py          # builds email_body.html
python src/send_email.py            # sends it if SMTP_* env vars are set
```

## Latest digest

[2026-06-13](archive/2026-06-13.md)

## Archive

<!-- newest first; updated automatically -->
- [2026-06-13](archive/2026-06-13.md)
