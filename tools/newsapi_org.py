from __future__ import annotations

import requests

from utils.cache import cache_data
from utils.settings import read_secret


@cache_data(ttl=300, show_spinner=False)
def fetch_newsapi_articles(topic: str, limit: int = 10) -> list[dict]:
    api_key = read_secret("NEWSAPI_KEY")
    if not api_key:
        raise RuntimeError("Missing `NEWSAPI_KEY`.")

    response = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": topic,
            "pageSize": limit,
            "language": "en",
            "sortBy": "publishedAt",
            "apiKey": api_key,
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
                "source": source.get("name", "NewsAPI"),
                "published_at": article.get("publishedAt", ""),
            }
        )

    return articles
