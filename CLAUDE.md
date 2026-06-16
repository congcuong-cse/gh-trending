# Daily GitHub Trending — Claude routine

This repo's daily digest is produced by a **scheduled Claude Code session**
(a trigger on Claude Code for web), not by an API key in CI. When you run as
that daily routine, follow these steps exactly.

## Daily routine

1. **Sync**: make sure you're on `main` (or the repo's default branch) and pulled
   up to date.

2. **Fetch**: run the scraper.
   ```bash
   pip install -r requirements.txt
   python src/fetch_trending.py
   ```
   This writes `data/today.json` (top 10, structured) and `data/today.md` (raw table).

3. **Summarize**: read `data/today.json` and create `archive/<date>.md`
   (use the `date` field, e.g. `archive/2026-06-13.md`) with this structure:

   ```
   # GitHub Trending — <date>

   ## TL;DR
   <2–4 sentences on the day's themes: dominant languages, recurring topics
   (AI agents, web frameworks, devtools…), anything notable.>

   ## Top 10

   ### 1. owner/repo  (+N stars today)
   <1–2 plain-English sentences: what it is and why it might matter. Infer from
   the name/description; never invent stats not present in today.json.>

   ... all 10, keeping the ranking ...

   ## Table
   <Paste the Markdown table from data/today.md.>
   ```

4. **Update `README.md`**: refresh the "Latest digest" link and prepend today's
   file to the "Archive" index (newest first).

5. **Email (optional)**: if mail is configured, send the digest.
   ```bash
   python src/render_email.py   # builds email_body.html
   python src/send_email.py     # sends it; skips cleanly if SMTP_* env vars are unset
   ```

6. **Commit & push, then auto-merge to `main`**:
   ```bash
   git add archive/ data/ README.md
   git commit -m "Trending digest for <date>"
   BRANCH=$(git branch --show-current)
   git push -u origin "$BRANCH"
   ```
   If `BRANCH` is not `main`, immediately merge it into `main` in the same session:
   ```bash
   git fetch origin main
   # Rebase our digest commit on top of any new main commits, resolving conflicts
   # (data/today.* always take our version; README.md archive list needs both dates)
   git rebase origin/main
   git push --force-with-lease origin "$BRANCH"
   # Fast-forward main to the rebased branch
   git checkout main
   git pull --ff-only origin main
   git merge --ff-only "$BRANCH"
   git push origin main
   ```
   Conflict resolution during rebase: `data/today.json` and `data/today.md` always keep **our** (today's) version; `README.md` needs both dates in the archive (newest first). After resolving, `git add` the files and `git rebase --continue`.

   This ensures every digest lands on `main` in the same session, triggering the Pages deploy automatically without manual intervention.

7. **Publish (automatic)**: the push to `main` triggers the
   `Deploy GitHub Pages` workflow (`.github/workflows/pages.yml`), which runs
   `python src/build_site.py` and publishes the browsable site to
   <https://congcuong-cse.github.io/gh-trending/>. You don't need to build or
   commit the site yourself — it's regenerated from `archive/` in CI, and the
   generated `site/` directory is gitignored.

## Style rules

- Concise, skimmable, no marketing fluff. 1–2 sentences per repo.
- Use only the numbers in `data/today.json`; never fabricate stats.
- The digest is written in **English**.
