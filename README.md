# News Summarizer Agent

This project converts your notebook prototype into a modular Streamlit app that follows a multi-step agent pipeline:

1. Planner agent
2. Fetch agent
3. Filter agen t
4. Summarizer agent
5. Formatter agent

## Notebook analysis

Your original notebook at `/Users/shreyashgolhani/Downloads/News_Summarizer_Agent.ipynb` is a useful proof of concept, but it is not ready to deploy directly.

What it currently does well:

- Uses a graph-style loop so the model can call tools.
- Fetches news and summarizes it with an LLM.
- Keeps the notebook short and easy to understand.

What blocks deployment in its current form:

- It depends on `google.colab.userdata`, which only works in Colab.
- It hardcodes a placeholder `NEWSAPI_KEY`.
- It mixes setup, orchestration, and testing in one notebook.
- It returns raw tool strings instead of structured article objects.
- It has no caching, UI state, filtering, or deployment files.
- It is effectively one LLM with tools, not a clear multi-agent app.

## Project structure

```text
news_summarizer_agent/
├── app.py
├── agents/
├── tools/
├── utils/
├── .streamlit/
├── requirements.txt
└── README.md
```

## Local setup

1. Create a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
4. Add either `OPENAI_API_KEY` or `GROQ_API_KEY`/`groq_api`, plus a news source key such as `NEWSAPI_KEY` or `GNEWS_API_KEY`.
5. Run `streamlit run app.py`.

If `NEWSAPI_KEY` and `GNEWS_API_KEY` are missing, the app falls back to Google News RSS.
If no LLM key is available, the app still runs with description-based fallback summaries.

## Deployment on Streamlit Community Cloud

1. Push this folder to a GitHub repository.
2. Sign in at `share.streamlit.io`.
3. Create a new app and point it to your repository.
4. Use `app.py` as the entrypoint.
5. Add your secrets in the app settings.

Notes from the current Streamlit docs:

- Community Cloud runs `streamlit run` from the repository root, so keep `requirements.txt` and `.streamlit/config.toml` in the repo structure expected by Streamlit.
- Streamlit Community Cloud lets you set a custom app URL subdomain under `*.streamlit.app`.
- Streamlit Community Cloud includes built-in app analytics showing total viewers, recent unique viewers, and their last visit times.

## Security note

If an API key is ever pasted into chat, committed to Git, or shown in a screenshot, treat it as exposed and rotate it before a public deployment.

## Custom domain guidance

As of April 3, 2026, Streamlit Community Cloud documents customizable app URLs as a `streamlit.app` subdomain, not a fully custom root domain. A recent Streamlit forum reply also says full custom domains are not natively supported on Community Cloud.

If you want `news.yourdomain.com`, the stronger option is:

1. Keep this app as a normal Streamlit app.
2. Deploy it on a host that supports custom domains for app services.
3. Point your DNS there.

Popular path:

- Render web service for the Streamlit app
- Custom domain on Render
- Built-in dashboard metrics on the host

## Analytics guidance

You now have two analytics layers:

- In-app session analytics in the Streamlit UI for pipeline timings and per-session usage.
- Hosting analytics for real viewer counts after deployment.

For resume/demo quality, the most practical split is:

- Streamlit Community Cloud for fastest launch and built-in viewer analytics.
- Render or another app host if you specifically need a real custom domain.

## Next upgrades

- Add article sentiment scoring.
- Add topic history with persistent storage.
- Add email digest delivery.
- Add a second page for trend comparison across topics.
