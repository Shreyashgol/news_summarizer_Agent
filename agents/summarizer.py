from __future__ import annotations

from openai import OpenAI

from utils.settings import available_llm_provider, read_secret


SYSTEM_PROMPT = (
    "You are a news summarizer. Produce exactly two concise sentences. "
    "Focus on the main development and why it matters."
)


def _fallback_summary(article: dict) -> str:
    description = (article.get("description") or "").strip()
    content = (article.get("content") or "").strip()
    source_text = description or content or article.get("title") or "No summary available."
    return source_text[:240].rstrip()


def _build_user_prompt(article: dict) -> str:
    return (
        f"Title: {article.get('title', '')}\n"
        f"Description: {article.get('description', '')}\n"
        f"Content: {article.get('content', '')}\n"
        f"Source: {article.get('source', '')}\n"
        f"URL: {article.get('url', '')}"
    )


def summarize_articles(
    articles: list[dict],
    model_name: str = "gpt-4o-mini",
) -> tuple[list[dict], str]:
    provider = available_llm_provider()
    client = None
    provider_label = "Fallback"

    if provider == "openai":
        api_key = read_secret("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key) if api_key else None
        provider_label = "OpenAI"
    elif provider == "groq":
        api_key = read_secret("GROQ_API_KEY") or read_secret("groq_api")
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1") if api_key else None
        provider_label = "Groq"

    summarized: list[dict] = []
    used_llm = False

    for article in articles:
        summary = _fallback_summary(article)

        if client:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": _build_user_prompt(article)},
                    ],
                )
                content = response.choices[0].message.content
                if content:
                    summary = content.strip()
                    used_llm = True
            except Exception as exc:
                summary = f"{summary} [LLM summary unavailable: {exc}]"

        enriched = dict(article)
        enriched["summary"] = summary
        summarized.append(enriched)

    summary_mode = provider_label if used_llm else "Fallback"
    return summarized, summary_mode
