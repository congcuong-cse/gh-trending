#!/usr/bin/env python3
"""Build a static GitHub Pages site from the daily trending archive.

Reads every ``archive/<date>.md`` digest, renders it to HTML, and writes a
browsable site into ``site/``:

  site/index.html      landing page: latest digest + full archive index
  site/<date>.html     one page per archived digest
  site/style.css       shared styles

The site is rebuilt from scratch on every run, so it can be regenerated in CI
(see .github/workflows/pages.yml) without committing generated HTML.
"""

from __future__ import annotations

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_DIR = ROOT / "archive"
SITE_DIR = ROOT / "site"

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})$")

SITE_TITLE = "Daily GitHub Trending"
SITE_TAGLINE = "An automated digest of the top 10 trending GitHub repositories, refreshed daily."
REPO_URL = "https://github.com/congcuong-cse/gh-trending"

MD_EXTENSIONS = ["tables", "fenced_code", "sane_lists", "toc"]


def find_digests() -> list[tuple[str, Path]]:
    """Return (date, path) for every archive/<date>.md, newest first."""
    digests = []
    for path in ARCHIVE_DIR.glob("*.md"):
        m = DATE_RE.match(path.stem)
        if m:
            digests.append((m.group(1), path))
    digests.sort(key=lambda item: item[0], reverse=True)
    return digests


def pretty_date(date: str) -> str:
    try:
        return datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %-d, %Y")
    except ValueError:
        return date


def render_markdown(text: str) -> str:
    return markdown.markdown(text, extensions=MD_EXTENSIONS)


def page(title: str, body: str, *, depth_to_root: str = "") -> str:
    """Wrap rendered body content in the shared HTML shell."""
    year = datetime.now(timezone.utc).year
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{SITE_TAGLINE}">
<link rel="stylesheet" href="{depth_to_root}style.css">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{depth_to_root}index.html">📈 {SITE_TITLE}</a>
    <nav>
      <a href="{depth_to_root}index.html">Home</a>
      <a href="{REPO_URL}">GitHub</a>
    </nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>{SITE_TAGLINE}</p>
    <p>Built automatically by a scheduled Claude Code session · © {year} ·
       <a href="{REPO_URL}">source</a></p>
  </div>
</footer>
</body>
</html>
"""


def archive_list_html(digests: list[tuple[str, Path]], depth_to_root: str = "") -> str:
    items = []
    for date, _ in digests:
        items.append(
            f'    <li><a href="{depth_to_root}{date}.html">'
            f'<span class="date">{date}</span>'
            f'<span class="day">{pretty_date(date)}</span></a></li>'
        )
    return '<ul class="archive-list">\n' + "\n".join(items) + "\n</ul>"


def build_digest_pages(digests: list[tuple[str, Path]]) -> None:
    for i, (date, path) in enumerate(digests):
        text = path.read_text(encoding="utf-8")
        content = render_markdown(text)

        newer = digests[i - 1][0] if i > 0 else None
        older = digests[i + 1][0] if i + 1 < len(digests) else None
        nav = []
        if newer:
            nav.append(f'<a class="prev" href="{newer}.html">← Newer ({newer})</a>')
        if older:
            nav.append(f'<a class="next" href="{older}.html">Older ({older}) →</a>')
        pager = f'<div class="pager">{"".join(nav)}</div>' if nav else ""

        body = f"""<article class="digest">
{content}
</article>
{pager}
<p class="back"><a href="index.html">← All digests</a></p>"""
        (SITE_DIR / f"{date}.html").write_text(
            page(f"{SITE_TITLE} — {date}", body), encoding="utf-8"
        )


def build_index(digests: list[tuple[str, Path]]) -> None:
    if digests:
        latest_date, latest_path = digests[0]
        latest_html = render_markdown(latest_path.read_text(encoding="utf-8"))
        latest_section = f"""<section class="latest">
  <div class="latest-head">
    <h2>Latest digest</h2>
    <a class="permalink" href="{latest_date}.html">permalink →</a>
  </div>
  <article class="digest">
{latest_html}
  </article>
</section>"""
    else:
        latest_section = "<p>No digests yet. Run the daily routine to generate one.</p>"

    body = f"""<section class="hero">
  <h1>📈 {SITE_TITLE}</h1>
  <p>{SITE_TAGLINE} No API key required — summaries are written by a scheduled
     Claude Code session.</p>
</section>
{latest_section}
<section class="archive">
  <h2>Archive</h2>
  {archive_list_html(digests)}
</section>"""
    (SITE_DIR / "index.html").write_text(
        page(SITE_TITLE, body), encoding="utf-8"
    )


CSS = """:root {
  --bg: #0d1117;
  --surface: #161b22;
  --border: #30363d;
  --text: #e6edf3;
  --muted: #9198a1;
  --accent: #2f81f7;
  --accent-soft: rgba(47, 129, 247, 0.15);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
.wrap { width: 100%; max-width: 880px; margin: 0 auto; padding: 0 20px; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }

.site-header {
  border-bottom: 1px solid var(--border);
  background: rgba(13, 17, 23, 0.85);
  backdrop-filter: blur(8px);
  position: sticky; top: 0; z-index: 10;
}
.site-header .wrap {
  display: flex; align-items: center; justify-content: space-between;
  padding-top: 14px; padding-bottom: 14px;
}
.brand { font-weight: 700; font-size: 1.05rem; color: var(--text); }
.site-header nav a { margin-left: 18px; color: var(--muted); font-size: 0.95rem; }
.site-header nav a:hover { color: var(--text); text-decoration: none; }

.hero { padding: 48px 0 8px; }
.hero h1 { font-size: 2.1rem; margin: 0 0 10px; }
.hero p { color: var(--muted); font-size: 1.05rem; max-width: 70ch; }

section { margin: 36px 0; }
h2 { font-size: 1.4rem; border-bottom: 1px solid var(--border); padding-bottom: 8px; }

.latest-head { display: flex; align-items: baseline; justify-content: space-between; }
.latest-head h2 { border: 0; padding: 0; }
.permalink { font-size: 0.9rem; }

.digest {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 8px 28px 24px;
}
.digest h1 { font-size: 1.8rem; }
.digest h2 { font-size: 1.3rem; margin-top: 28px; }
.digest h3 { font-size: 1.1rem; margin-top: 22px; }
.digest h3 { color: var(--text); }
.digest a { font-weight: 600; }

table { border-collapse: collapse; width: 100%; margin: 18px 0; font-size: 0.9rem; display: block; overflow-x: auto; }
th, td { border: 1px solid var(--border); padding: 8px 10px; text-align: left; vertical-align: top; }
th { background: var(--accent-soft); }
tr:nth-child(even) td { background: rgba(255, 255, 255, 0.02); }

code { background: rgba(110, 118, 129, 0.25); padding: 0.15em 0.4em; border-radius: 6px; font-size: 0.9em; }
pre { background: #010409; border: 1px solid var(--border); border-radius: 10px; padding: 16px; overflow-x: auto; }
pre code { background: none; padding: 0; }

.archive-list { list-style: none; padding: 0; margin: 0; display: grid; gap: 10px; }
.archive-list li a {
  display: flex; align-items: baseline; gap: 14px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 14px 18px; color: var(--text);
}
.archive-list li a:hover { border-color: var(--accent); text-decoration: none; }
.archive-list .date { font-weight: 700; font-variant-numeric: tabular-nums; }
.archive-list .day { color: var(--muted); font-size: 0.92rem; }

.pager { display: flex; justify-content: space-between; margin: 24px 0 8px; gap: 12px; flex-wrap: wrap; }
.pager a { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 8px 14px; }
.pager .next { margin-left: auto; }
.back { margin-top: 8px; }

.site-footer { border-top: 1px solid var(--border); margin-top: 56px; padding: 28px 0; color: var(--muted); font-size: 0.88rem; }
.site-footer p { margin: 4px 0; }

@media (max-width: 600px) {
  .hero h1 { font-size: 1.7rem; }
  .digest { padding: 4px 16px 18px; }
  .archive-list li a { flex-direction: column; gap: 2px; }
}
"""


def main() -> None:
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    digests = find_digests()
    (SITE_DIR / "style.css").write_text(CSS, encoding="utf-8")
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")
    build_index(digests)
    build_digest_pages(digests)

    print(f"Built site with {len(digests)} digest(s) into {SITE_DIR}")


if __name__ == "__main__":
    main()
