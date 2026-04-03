from __future__ import annotations


def format_output(articles: list[dict]) -> list[dict]:
    formatted: list[dict] = []

    for index, article in enumerate(articles, start=1):
        formatted.append(
            {
                "index": index,
                "title": article.get("title", "Untitled article"),
                "summary": article.get("summary", "No summary available."),
                "url": article.get("url", ""),
                "source": article.get("source", ""),
                "published_at": article.get("published_at", ""),
            }
        )

    return formatted
