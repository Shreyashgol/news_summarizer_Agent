from __future__ import annotations

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None


def cache_data(*args, **kwargs):
    if st is None:
        def decorator(func):
            return func

        return decorator

    return st.cache_data(*args, **kwargs)
