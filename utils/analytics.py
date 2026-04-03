from __future__ import annotations

import streamlit as st


def init_session_metrics() -> None:
    st.session_state.setdefault("analytics_runs", [])


def record_run(run_data: dict) -> None:
    st.session_state["analytics_runs"].append(run_data)


def get_session_metrics() -> dict:
    runs = st.session_state.get("analytics_runs", [])
    if not runs:
        return {
            "runs": 0,
            "avg_total_time": 0.0,
            "avg_articles": 0.0,
        }

    total_time = sum(item["total_time"] for item in runs)
    total_articles = sum(item["article_count"] for item in runs)
    count = len(runs)

    return {
        "runs": count,
        "avg_total_time": total_time / count,
        "avg_articles": total_articles / count,
    }
