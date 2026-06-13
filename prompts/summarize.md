# Daily GitHub Trending summary — instructions for Claude Code

You are generating today's GitHub Trending digest. Work only with the data
already fetched into the repo; do not browse the web.

## Steps

1. Read `data/today.json`. It contains today's date and the top 10 trending
   repositories (name, url, language, stars, stars today, description).

2. Create `archive/<date>.md` (use the `date` field, e.g. `archive/2026-06-13.md`)
   with this structure:

   ```
   # GitHub Trending — <date>

   ## TL;DR
   <2–4 sentences on the overall themes of today's list: dominant languages,
   recurring topics (AI agents, web frameworks, devtools, etc.), anything
   notable about the day.>

   ## Top 10

   ### 1. owner/repo  (+N stars today)
   <One or two sentences in plain English: what the project is and why someone
   might care. Infer from the description and name; do not invent facts you
   cannot support.>

   ... repeat for all 10, keeping the ranking from the data ...

   ## Table
   <Paste the Markdown table from data/today.md here.>
   ```

3. Update `README.md` so that:
   - The "Latest digest" section embeds (or links to) today's archive file.
   - An "Archive" index list includes a link to the new dated file, newest first.

## Style

- Concise and skimmable. No marketing fluff.
- Never fabricate stats — use only the numbers in `today.json`.
- Keep each repo blurb to 1–2 sentences.
