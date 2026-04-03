from __future__ import annotations


def plan_query(
    query: str,
    display_limit: int = 5,
    source_preference: str = "auto",
    model_name: str = "gpt-4o-mini",
) -> dict:
    clean_query = " ".join(query.split())
    return {
        "topic": clean_query,
        "display_limit": display_limit,
        "fetch_limit": max(display_limit * 2, 8),
        "source_preference": source_preference,
        "model_name": model_name,
    }
