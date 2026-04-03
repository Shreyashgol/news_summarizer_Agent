from __future__ import annotations

import requests

from utils.cache import cache_data
from utils.settings import read_secret


@cache_data(ttl=300, show_spinner=False)
def fetch_gnews_articles(topic: str, limit: int = 10) -> list[dict]:
    api_key = read_secret("GNEWS_API_KEY")
    if not api_key:
        raise RuntimeError("Missing `GNEWS_API_KEY`.")

    response = requests.get(
        "https://gnews.io/api/v4/search",
        params={
            "q": topic,
            "lang": "en",
            "max": limit,
            "sortby": "publishedAt",
            "token": api_key,
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()

    articles: list[dict] = []
    for article in payload.get("articles", []):
        source = article.get("source") or {}
        articles.append(
            {
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "url": article.get("url", ""),
                "source": source.get("name", "GNews"),
                "published_at": article.get("publishedAt", ""),
            }
        )

    return articles
