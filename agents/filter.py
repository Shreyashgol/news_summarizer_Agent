from __future__ import annotations

import re


def _normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def filter_articles(articles: list[dict], max_articles: int = 5) -> list[dict]:
    seen: set[str] = set()
    filtered: list[dict] = []

    for article in articles:
        title = (article.get("title") or "").strip()
        if not title:
            continue

        normalized_title = _normalize_title(title)
        url = (article.get("url") or "").strip()
        unique_key = normalized_title or url

        if not unique_key or unique_key in seen or url in seen:
            continue

        seen.add(unique_key)
        if url:
            seen.add(url)

        filtered.append(article)
        if len(filtered) >= max_articles:
            break

    return filtered
