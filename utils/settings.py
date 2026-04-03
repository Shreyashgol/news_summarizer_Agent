from __future__ import annotations

import os

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None


def read_secret(name: str, default: str | None = None) -> str | None:
    if st is not None:
        try:
            if name in st.secrets:
                value = st.secrets[name]
                return str(value)
        except Exception:
            pass

    return os.getenv(name, default)


def available_llm_provider() -> str | None:
    if read_secret("OPENAI_API_KEY"):
        return "openai"
    if read_secret("GROQ_API_KEY") or read_secret("groq_api"):
        return "groq"
    return None
