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
- **Email (optional)**: sent via SMTP only when `SMTP_USER`/`SMTP_PASS` are set;
  otherwise the email step is skipped.

## Trigger the daily routine

Set up a **scheduled session** in Claude Code for web
([docs](https://code.claude.com/docs/en/claude-code-on-the-web)):

1. Open this repo's environment in Claude Code for web.
2. Create a **scheduled trigger** that runs daily with the prompt:
   > Run the daily GitHub Trending routine described in `CLAUDE.md`.
3. Claude will fetch, summarize, (optionally) email, commit and push — on its own.

To run it **on demand**, just start a session and give it the same prompt.

## Email setup (optional)

Set these as environment variables in the environment (Settings → Environment):

| Variable    | Purpose                                            | Default              |
|-------------|----------------------------------------------------|----------------------|
| `SMTP_USER` | sender address / SMTP username (**required**)      | —                    |
| `SMTP_PASS` | SMTP password / Gmail [App Password](https://support.google.com/accounts/answer/185833) (**required**) | — |
| `MAIL_TO`   | recipient                                          | `congcuong.cse@gmail.com` |
| `SMTP_HOST` | SMTP server                                        | `smtp.gmail.com`     |
| `SMTP_PORT` | `465` (SSL) or `587` (STARTTLS)                    | `465`                |

If `SMTP_USER`/`SMTP_PASS` are absent, `send_email.py` exits cleanly and the
rest of the routine still runs.

## Run locally

```bash
pip install -r requirements.txt
python src/fetch_trending.py        # writes data/today.json and data/today.md
# (then summarize by hand or let Claude do it, then:)
python src/render_email.py          # builds email_body.html
python src/send_email.py            # sends it if SMTP_* env vars are set
```

## Latest digest

_The first scheduled run will populate this section._

## Archive

<!-- newest first; updated automatically -->
_No digests yet._
