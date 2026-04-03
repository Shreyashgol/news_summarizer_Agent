from __future__ import annotations

import re
from urllib.parse import quote_plus

import feedparser

from utils.cache import cache_data


def _strip_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value or "").strip()


@cache_data(ttl=300, show_spinner=False)
def fetch_rss_articles(topic: str, limit: int = 10) -> list[dict]:
    query = quote_plus(topic)
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)

    if getattr(feed, "bozo", 0):
        raise RuntimeError("Unable to parse the RSS feed.")

    articles: list[dict] = []
    for entry in feed.entries[:limit]:
        articles.append(
            {
                "title": entry.get("title", ""),
                "description": _strip_html(entry.get("summary", "")),
                "content": "",
                "url": entry.get("link", ""),
                "source": "Google News RSS",
                "published_at": entry.get("published", ""),
            }
        )

    return articles
