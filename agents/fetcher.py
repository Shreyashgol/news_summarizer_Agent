from __future__ import annotations

from tools.newsapi_org import fetch_newsapi_articles
from tools.news_api import fetch_gnews_articles
from tools.rss_parser import fetch_rss_articles


def fetch_articles(plan: dict) -> dict:
    topic = plan["topic"]
    fetch_limit = plan["fetch_limit"]
    source_preference = plan["source_preference"]

    articles: list[dict] = []
    notes: list[str] = []
    sources_used: list[str] = []

    if source_preference in {"auto", "newsapi"}:
        try:
            newsapi_articles = fetch_newsapi_articles(topic=topic, limit=fetch_limit)
            if newsapi_articles:
                articles.extend(newsapi_articles)
                sources_used.append("NewsAPI")
        except Exception as exc:
            notes.append(f"NewsAPI fetch skipped: {exc}")

    if source_preference in {"auto", "gnews"} and len(articles) < fetch_limit:
        try:
            gnews_articles = fetch_gnews_articles(topic=topic, limit=fetch_limit)
            if gnews_articles:
                articles.extend(gnews_articles)
                sources_used.append("GNews")
        except Exception as exc:
            notes.append(f"GNews fetch skipped: {exc}")

    needs_rss = source_preference == "rss" or (
        source_preference == "auto" and len(articles) < fetch_limit
    )
    if needs_rss:
        try:
            rss_articles = fetch_rss_articles(topic=topic, limit=fetch_limit)
            if rss_articles:
                articles.extend(rss_articles)
                sources_used.append("RSS")
        except Exception as exc:
            notes.append(f"RSS fetch skipped: {exc}")

    if not articles and not notes:
        notes.append("No articles were returned by the configured sources.")

    return {
        "articles": articles,
        "notes": notes,
        "sources_used": sources_used,
    }
