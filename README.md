# 📈 Daily GitHub Trending Summary

An automated digest of the **top 10 trending GitHub repositories**, refreshed
every day and summarized by Claude Code.

## How it works

```
GitHub Actions (cron, daily 08:00 UTC)
        │
        ▼
  src/fetch_trending.py   → scrapes github.com/trending, writes data/today.json + data/today.md
        │
        ▼
  Claude Code (claude-code-action) → reads the data, writes archive/<date>.md, updates this README
        │
        ▼
  git commit & push       → digest archived in the repo
```

- **No official API**: GitHub doesn't expose trending data, so we scrape the
  public HTML page (`src/fetch_trending.py`). The parser targets stable
  `article.Box-row` elements.
- **AI summary**: the [`claude-code-action`](https://github.com/anthropic/claude-code-action)
  runs in CI and follows [`prompts/summarize.md`](prompts/summarize.md) to turn
  raw repo metadata into a readable digest.
- **Archive**: every day's digest is committed under [`archive/`](archive/).
- **Email**: the digest is also emailed each morning via Gmail SMTP.

## Setup

1. Add a repository secret **`ANTHROPIC_API_KEY`** (Settings → Secrets and
   variables → Actions). Alternatively swap in `claude_code_oauth_token`.
2. Add email secrets for the daily mail-out:
   - **`MAIL_USERNAME`** — the Gmail address that sends the digest.
   - **`MAIL_PASSWORD`** — a Gmail [App Password](https://support.google.com/accounts/answer/185833)
     (not your normal password; requires 2FA enabled).

   The recipient is set to `congcuong.cse@gmail.com` in the workflow.
3. Ensure Actions have write permission (Settings → Actions → General →
   Workflow permissions → *Read and write*).
4. The workflow runs daily, or trigger it manually from the **Actions** tab
   (*Daily GitHub Trending Summary* → *Run workflow*).

## Run locally

```bash
pip install -r requirements.txt
python src/fetch_trending.py        # writes data/today.json and data/today.md
```

## Latest digest

_The first scheduled run will populate this section._

## Archive

<!-- newest first; updated automatically -->
_No digests yet._
