from __future__ import annotations

import html
from time import perf_counter

import streamlit as st

from agents.fetcher import fetch_articles
from agents.filter import filter_articles
from agents.formatter import format_output
from agents.planner import plan_query
from agents.summarizer import summarize_articles
from utils.analytics import get_session_metrics, init_session_metrics, record_run
from utils.settings import available_llm_provider


def render_header() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-1: #f7f4eb;
            --bg-2: #fffdf7;
            --ink: #1f2430;
            --muted: #596275;
            --accent: #b55d3d;
            --accent-soft: #f0d7ce;
            --card: rgba(255, 255, 255, 0.82);
            --border: rgba(181, 93, 61, 0.18);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, #f6d8b6 0%, transparent 35%),
                radial-gradient(circle at top right, #d7ebf2 0%, transparent 28%),
                linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
        }

        .hero {
            padding: 1.2rem 1.4rem;
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(255,255,255,0.88), rgba(255,247,240,0.96));
            border: 1px solid var(--border);
            box-shadow: 0 12px 28px rgba(86, 59, 42, 0.08);
            margin-bottom: 1rem;
        }

        .hero h1 {
            color: var(--ink);
            margin: 0;
            font-size: 2rem;
            line-height: 1.1;
        }

        .hero p {
            color: var(--muted);
            margin: 0.5rem 0 0;
            font-size: 1rem;
        }

        .article-card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 10px 22px rgba(86, 59, 42, 0.06);
        }

        .article-meta {
            color: var(--muted);
            font-size: 0.92rem;
            margin-bottom: 0.45rem;
        }

        .article-title {
            color: var(--ink);
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.45rem;
        }

        .article-summary {
            color: var(--ink);
            font-size: 0.98rem;
            line-height: 1.55;
        }
        </style>
        <div class="hero">
            <h1>PulseBrief AI</h1>
            <p>
                A modular news agent that plans, fetches, filters, summarizes, and formats
                briefings for Streamlit.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_results(run_data: dict) -> None:
    results = run_data["results"]
    fetch_notes = run_data["fetch_notes"]
    sources_used = run_data["sources_used"]
    timings = run_data["timings"]

    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    metrics_col1.metric("Articles", len(results))
    metrics_col2.metric("Sources", ", ".join(sources_used) or "None")
    metrics_col3.metric("Total Time", f"{run_data['total_time']:.2f}s")
    metrics_col4.metric("Summaries", run_data["summary_mode"])

    if fetch_notes:
        for note in fetch_notes:
            st.info(note)

    briefing_tab, analytics_tab = st.tabs(["Briefing", "Analytics"])

    with briefing_tab:
        if not results:
            st.warning("No articles were returned for this query. Try a broader topic.")
            return

        for item in results:
            published_at = html.escape(item["published_at"] or "Time unavailable")
            source = html.escape(item["source"] or "Unknown source")
            title = html.escape(item["title"])
            summary = html.escape(item["summary"])
            article_url = item["url"] or "#"
            st.markdown(
                f"""
                <div class="article-card">
                    <div class="article-meta">#{item["index"]} · {source} · {published_at}</div>
                    <div class="article-title">{title}</div>
                    <div class="article-summary">{summary}</div>
                    <div style="margin-top:0.8rem;">
                        <a href="{article_url}" target="_blank">Read full article</a>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with analytics_tab:
        st.subheader("Pipeline Timings")
        for stage, seconds in timings.items():
            st.metric(stage, f"{seconds:.2f}s")

        session_metrics = get_session_metrics()
        st.subheader("Session Dashboard")
        dash_col1, dash_col2, dash_col3 = st.columns(3)
        dash_col1.metric("Runs This Session", session_metrics["runs"])
        dash_col2.metric("Avg Total Time", f"{session_metrics['avg_total_time']:.2f}s")
        dash_col3.metric("Avg Articles", f"{session_metrics['avg_articles']:.1f}")

        st.caption(
            "This in-app dashboard tracks only the current Streamlit session. "
            "For deployed viewer analytics, use your hosting platform's analytics panel."
        )


def main() -> None:
    st.set_page_config(page_title="PulseBrief AI", page_icon="📰", layout="wide")
    init_session_metrics()
    render_header()

    with st.sidebar:
        st.header("Controls")
        query = st.text_input("Topic", value="Artificial intelligence")
        source_mode = st.selectbox("News source", ["auto", "newsapi", "gnews", "rss"], index=0)
        display_limit = st.slider("Articles to show", min_value=3, max_value=10, value=5)
        default_model = "llama-3.3-70b-versatile" if available_llm_provider() == "groq" else "gpt-4o-mini"
        model_name = st.text_input("LLM model", value=default_model)
        st.caption("`auto` tries NewsAPI, then GNews, then RSS.")
        run_clicked = st.button("Run Agents", type="primary", use_container_width=True)

    if run_clicked:
        if not query.strip():
            st.error("Enter a topic before running the pipeline.")
            return

        timings: dict[str, float] = {}
        total_start = perf_counter()

        start = perf_counter()
        plan = plan_query(
            query=query,
            display_limit=display_limit,
            source_preference=source_mode,
            model_name=model_name,
        )
        timings["Planner"] = perf_counter() - start

        start = perf_counter()
        fetch_result = fetch_articles(plan)
        timings["Fetcher"] = perf_counter() - start

        start = perf_counter()
        filtered_articles = filter_articles(
            fetch_result["articles"],
            max_articles=plan["display_limit"],
        )
        timings["Filter"] = perf_counter() - start

        start = perf_counter()
        summarized_articles, summary_mode = summarize_articles(
            filtered_articles,
            model_name=plan["model_name"],
        )
        timings["Summarizer"] = perf_counter() - start

        start = perf_counter()
        results = format_output(summarized_articles)
        timings["Formatter"] = perf_counter() - start

        total_time = perf_counter() - total_start

        run_data = {
            "plan": plan,
            "results": results,
            "timings": timings,
            "total_time": total_time,
            "fetch_notes": fetch_result["notes"],
            "sources_used": fetch_result["sources_used"],
            "summary_mode": summary_mode,
        }
        st.session_state["last_run"] = run_data

        record_run(
            {
                "total_time": total_time,
                "article_count": len(results),
            }
        )

    if "last_run" in st.session_state:
        render_results(st.session_state["last_run"])
    else:
        st.info("Run the pipeline from the sidebar to generate your first news briefing.")


if __name__ == "__main__":
    main()
