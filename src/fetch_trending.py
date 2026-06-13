"""Fetch the top GitHub trending repositories for the day.

GitHub has no official trending API, so we scrape the public
``github.com/trending`` HTML page. The page is server-rendered and stable,
which makes it reliable to parse.

Outputs two files under ``data/``:

* ``today.json``  - structured data for the top N repos
* ``today.md``    - a raw Markdown table (no AI narrative yet)

The AI narrative is added afterwards by the Claude Code routine in CI.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

TRENDING_URL = "https://github.com/trending"
TOP_N = 10
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# A browser-like UA avoids the occasional bot challenge page.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def _clean(text: str | None) -> str:
    """Collapse whitespace in scraped text."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _digits(text: str | None) -> int:
    """Pull the first integer out of a string like '1,234 stars today'."""
    if not text:
        return 0
    match = re.search(r"[\d,]+", text)
    return int(match.group().replace(",", "")) if match else 0


def fetch_trending(since: str = "daily", top_n: int = TOP_N) -> list[dict]:
    """Scrape the trending page and return a list of repo dicts."""
    resp = requests.get(
        TRENDING_URL, params={"since": since}, headers=HEADERS, timeout=30
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("article.Box-row")

    repos: list[dict] = []
    for rank, row in enumerate(rows[:top_n], start=1):
        title_link = row.select_one("h2 a")
        if not title_link:
            continue
        full_name = _clean(title_link.get("href", "")).strip("/")

        desc_el = row.select_one("p")
        lang_el = row.select_one('span[itemprop="programmingLanguage"]')
        today_el = row.select_one("span.d-inline-block.float-sm-right")

        star_els = row.select('a[href$="/stargazers"], a[href$="/forks"]')
        total_stars = _digits(star_els[0].get_text()) if star_els else 0
        forks = _digits(star_els[1].get_text()) if len(star_els) > 1 else 0

        repos.append(
            {
                "rank": rank,
                "name": full_name,
                "url": f"https://github.com/{full_name}",
                "description": _clean(desc_el.get_text() if desc_el else ""),
                "language": _clean(lang_el.get_text() if lang_el else ""),
                "stars": total_stars,
                "forks": forks,
                "stars_today": _digits(today_el.get_text() if today_el else ""),
            }
        )

    return repos


def to_markdown_table(repos: list[dict]) -> str:
    """Render the raw repo list as a Markdown table."""
    lines = [
        "| # | Repository | Language | Stars | Stars today | Description |",
        "|--:|------------|----------|------:|------------:|-------------|",
    ]
    for r in repos:
        desc = r["description"].replace("|", "\\|")
        lines.append(
            f"| {r['rank']} | [{r['name']}]({r['url']}) | "
            f"{r['language'] or '-'} | {r['stars']:,} | "
            f"+{r['stars_today']:,} | {desc} |"
        )
    return "\n".join(lines)


def main() -> int:
    repos = fetch_trending()
    if not repos:
        print("ERROR: no repositories parsed - page layout may have changed.",
              file=sys.stderr)
        return 1

    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    payload = {"date": date, "source": TRENDING_URL, "repos": repos}
    (DATA_DIR / "today.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (DATA_DIR / "today.md").write_text(
        f"# GitHub Trending - {date}\n\n{to_markdown_table(repos)}\n",
        encoding="utf-8",
    )

    print(f"Fetched {len(repos)} trending repos for {date}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
